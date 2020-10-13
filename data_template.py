import json
import os
#from storage import storage
from threading import Thread
import time
import shutil
from storage_helper import storage_helper
import ipfshttpclient # type: ignore
import datetime
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly # type: ignore

class data_template:
    def __init__(self):
        self.template_dict=""
        self.template_hash = ""
        self.pt_val_hash = ""
        self.device_hash = ""
        try:
            self.setup()
        except:
            pass

    def setup(self):
        setup_dict= list()
        with open("env.json","r") as infile:
            setup_dict = json.load(infile)
        self.template_dict = setup_dict[3]

    def verify_labels(self,packet):
        '''Verify labels to see if the data is valid'''
        device_dict = helper.get_device_dict() #type: ignore
        #Search to see if key and values match.
        #We need at least 2 matches to verify
        a = 0
        found = False
        full_key = ""
        for key in device_dict.keys():
            for key1,value1 in packet.items():
                if key1 in key and value1 in key:
                    a += 1
            if a < 2:
                a == 0
            else:
                full_key = key
                found = True
                break
        if found == True:
            template_name = full_key.split("=")[-1]
            config = self.get_config(full_key,device_dict[full_key])
            template_dict = self.get_template(template_name)
            if self.check_device_params(template_dict,packet,config) == True:
                return full_key
        else:
            return False

    def check_device_params(self,template_dict,packet,config):
        '''Check parameters of incoming data'''
        #Check if device data equals config data
        a = 0
        for key1 in config["data"].keys():
            a += 1
            for key in packet.keys():
                if key1 == key:
                    parameter = config["data"][key1]
                    #Check if the device's data matches the template
                    if config["data"][key1] in template_dict["parameters"]:
                        if float(packet[key]) >= template_dict["parameters"][parameter]["min"] and \
                        float(packet[key]) <= template_dict["parameters"][parameter]["max"]:
                            a -= 1
        return (a == 0)

    def get_config(self,file_title,ipns_key):
        '''Retrieve a config file given the key'''
        folder_title = helper.get_data_folder(ipns_key)
        with open(folder_title+ "/"+file_title+".json","r") as infile:
            device_dict = json.load(infile)
        config = dict()
        config["characteristics"] = device_dict["characteristics"]
        config["template"] = device_dict["template"]
        config["identifiers"] = device_dict["identifiers"]
        config["data"] = device_dict["data"]
        return config

    def check_timestamp(self,line):
        try:
            datetime.datetime.fromtimestamp(int(line)).strftime('%Y-%m-%d %H:%M:%S')
            return True
        except:
            return False
    
    def get_device_data(self,config):
        '''Get device data given identifiers
        Hash config values to search patient values dict'''
        pt_val_key = helper.hash_config(config)
        '''Search patient values dict for the config values'''
        key = helper.search_pt_val(pt_val_key,ret=True)
        data_list = []
        if key == False: 
            return False
        else:
            folder_title = helper.get_data_folder(key)
            files = os.listdir(folder_title)
            for file in files:
                if file != "config.json":
                    #Remove .json extension
                    file = file[:-5]
                    self.format_data(file,key,"scatter")
    
    def format_data(self,file_title,ipns_key,presentation):
        '''Looks through data and extracts data. Checks to see if right order is present'''
        config = self.get_config(file_title,ipns_key)
        template_dict = self.get_template(config["template"])
        folder_title = helper.get_data_folder(ipns_key)
        with open(folder_title+ "/"+file_title+".json","r") as infile:
            device_dict = json.load(infile)
        '''Check whether each timestamp in patient_info is valid'''
        for key in device_dict["patient_info"].keys():
            if self.check_timestamp(key):
                pass
            #To work on... method to fix data
        updated_data = self.sort_data(device_dict["patient_info"])
        '''Sort Data and convert to datetime object'''
        df_data = dict()
        df_data["Timestamp"]=list(updated_data.keys())
        for key in device_dict["data"].keys():
            sample_list = []
            for key1 in device_dict["patient_info"].keys():
                sample_list.append(device_dict["patient_info"][key1][key])
            df_data[key]=list(sample_list)
        self.generate_graph(df_data,presentation)

    def generate_graph(self,df_data,presentation_value):
        '''Generate a graph based on patient data, and method to present data'''
        df = pd.DataFrame(df_data)
        fig = px.scatter(df,x=list(df_data.keys())[0], y=list(df_data.keys())[1])
        plotly.offline.plot(fig)

    def upload_template_dict(self):
        '''Upload template dictionary which store all templates'''
        hashed_dict = client.add(self.template_hash+"/template_dict.json",wrap_with_directory=True)
        ipfs_hash = list(hashed_dict[1].values())[1]
        client.name.publish(ipfs_hash,key=self.template_dict)
        return True
    
    def push_data(self,data):
        '''Handle pushing data to ipfs'''
        found = self.verify_labels(data)
        if found == False:
            return False
        key = helper.search_device_dict(found,True)
        hash = helper.get_data_folder(key)
        with open(hash + "/" + found + ".json","r") as infile:
            current_dict = json.load(infile)
        if "patient_info" not in current_dict:
            current_dict["patient_info"] = dict()
        current_dict["patient_info"][str(int(time.time()))] = data
        with open(hash + "/" + found + ".json","w") as outfile:
            json.dump(current_dict,outfile)
        helper.upload_data(hash,key)
        return True
    
    def get_template_dict(self):
        '''Get template dictionary'''
        hash = {}
        hash = client.name.resolve(name=self.template_dict)
        self.template_hash = list(hash.values())[0].split("/")[2]
        client.get(self.template_hash)
        with open(self.template_hash + "/template_dict.json","r") as infile:
            template_dict = json.load(infile)
        return template_dict
    
    def search_template_dict(self,key,ret=False):
        '''Search for a specific template'''
        template_dict = self.get_template_dict()
        if key in template_dict and ret==False:
            return True
        elif key in template_dict and ret==True:
            return template_dict[key]
        else:
            return False

    def sort_data(self,patient_info):
        '''Sort all patient data based on timestamp'''
        sorted_items = dict(sorted(patient_info.items()))
        new_dict = dict()
        for key in sorted_items.keys():
            new_dict[datetime.datetime.fromtimestamp(int(key)).strftime('%Y-%m-%d %H:%M:%S')] = sorted_items[key]
        return new_dict
    
    def add_template_dict(self,key,value):
        '''Add a template to template_dict'''
        template_dict = self.get_template_dict()
        template_dict[key]=value
        with open(self.template_hash+ "/template_dict.json","w") as outfile:
            json.dump(template_dict,outfile)
        return True

    def delete_template_dict(self,key):
        '''Delete a template from template_dict'''
        template_dict = self.get_template_dict()
        template_dict.pop(key, None)
        with open(self.template_hash+ "/template_dict.json","w") as outfile:
            json.dump(template_dict,outfile)
        return True
    
    def get_template(self,template):
        '''Retrieve a specific template'''
        template_dict = self.get_template_dict()
        if template in template_dict:
            temp_hash = template_dict[template]
            hash = client.name.resolve(name=temp_hash)
            hash = list(hash.values())[0].split("/")[2]
            client.get(hash)
            with open(hash+ "/" + template + "_template.json","r") as infile:
                template_dict = json.load(infile)
            return template_dict
        else:
            return False

sample_config = {
    "characteristics":{
        "first_name":"manan",
        "last_name":"shukla",
        "dob":"01/12/2001"
    },
    "template":"adherence",
    "identifiers":{
        "patient_id":"12d345",
        "medication_id":"678f9"},
    "data":{
        "Pills Taken":"compliance"
    },
    "patient_info":{
        #Include all patient data here
    }
}
'''if template was EKG, data would look like:
        "data":{
            "s":"s-wave"
            "p":"p-wave"
        }'''

label_2 = {"patient_id":"12345","r-wave":"1","s-wave":"4"}

sample_template = {
    "parameters":{
        "compliance":{
            "min":0,
            "max":1
        }
    },
    "presentation":{
        "line"
    }
}

sample_data = {
    "patient_id":"12d345",
    "medication_id":"678f9",
    "Pills Taken":"0"
}

sample_ekg = {
    "patient_id":"12d345",
    "medication_id":"678f9",
    "s-wave":"13",
    "q-wave":"12",
    "4-wave":"11"
}
client = ipfshttpclient.connect()

template = data_template()
helper = storage_helper()

#print(template.search_template_dict("adherence",ret=True))
# print(template.delete_template_dict("sample"))
# print(template.upload_template_dict())
#print(template.format_data("patient_id=12d345medication_id=678f9template=adherence","QmVxkCtr9JgaUVUH5Wvmou9p9pHSsb6rHzzeDktesawhw3","line"))
