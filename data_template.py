import json
import os
from storage import storage
from threading import Thread
import shutil
from storage_helper import storage_helper
import ipfshttpclient # type: ignore
import datetime
import matplotlib # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore

class data_template:
    def __init__(self):
        self.template_dict="QmYBRghZRZLpVcwrF29VUuqgJkVJWz6RFBvPFyWfZWaf6z"
        self.template_hash = ""
        self.pt_val_hash = ""
        self.device_hash = ""

    '''Verify labels to see if the data is valid'''
    def verify_labels(self,packet):
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
                return True
        else:
            return False

    '''Check parameters of incoming data'''
    def check_device_params(self,template_dict,packet,config):
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

    #Retrieve a config file given the key
    def get_config(self,file_title,ipns_key):
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

    '''Looks through data and extracts data. Checks to see if right order is present'''
    def format_data(self,file_title,ipns_key,presentation):
        config = self.get_config(file_title,ipns_key)

        template_dict = self.get_template(config["template"])
        folder_title = helper.get_data_folder(ipns_key)
        with open(folder_title+ "/"+file_title+".json","r") as infile:
            device_dict = json.load(infile)
        
        #Check whether each timestamp in patient_info is valid
        for key in device_dict["patient_info"].keys():
            if self.check_timestamp(key):
                pass
            #To work on... method to fix data
            else:
                exit(0)

        #self.generate_graph(device_dict,presentation)

    # def generate_graph(self,device_dict,presentation_value):
        #Gather list of all timestamps in device dict

        #Gather list of all data values in device_dict

        #Use Matplotlib to generate a line graph 

    '''Upload template dictionary which store all templates'''
    def upload_template_dict(self):
        hashed_dict = client.add(self.template_hash+"/template_dict.json",wrap_with_directory=True)
        ipfs_hash = list(hashed_dict[1].values())[1]
        client.name.publish(ipfs_hash,key=self.template_dict)
        return True

    '''Get template dictionary'''
    def get_template_dict(self):
        hash = {}
        hash = client.name.resolve(name=self.template_dict)
        self.template_hash = list(hash.values())[0].split("/")[2]
        client.get(self.template_hash)
        with open(self.template_hash + "/template_dict.json","r") as infile:
            template_dict = json.load(infile)
        return template_dict
    
    '''Search for a specific template'''
    def search_template_dict(self,key,ret=False):
        template_dict = self.get_template_dict()
        if key in template_dict and ret==False:
            return True
        elif key in template_dict and ret==True:
            return template_dict[key]
        else:
            return False
    
    '''Add a template to template_dict'''
    def add_template_dict(self,key,value):
        template_dict = self.get_template_dict()
        template_dict[key]=value
        with open(self.template_hash+ "/template_dict.json","w") as outfile:
            json.dump(template_dict,outfile)
        return True

    '''Delete a template from template_dict'''
    def delete_template_dict(self,key):
        template_dict = self.get_template_dict()
        template_dict.pop(key, None)
        with open(self.template_hash+ "/template_dict.json","w") as outfile:
            json.dump(template_dict,outfile)
        return True
    
    '''Retrieve a specific template'''
    def get_template(self,template):
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
sample = storage()
helper = storage_helper()

#print(template.search_template_dict("adherence",ret=True))
# print(template.delete_template_dict("sample"))
# print(template.upload_template_dict())
print(template.check_timestamp("26459961405"))