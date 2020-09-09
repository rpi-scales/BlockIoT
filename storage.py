import json
import os
from threading import Thread
import shutil
from storage_helper import storage_helper

import ipfshttpclient # type: ignore

class storage:
    def __init__(self):
        self.patient_values_peer = "QmX2EGscc7jbRwNtUdU9Mkp5Y7zaNUrrWrFq2v8Ai7f1GM"
        self.emr_dict_key = "QmSQCE5pZ4jAaxdBbrZs6PKB3mWUUH2kewvJT3jEXtQQEu"
        self.device_dict_key = "QmaZvWEJbSyptzD4bVHMZhYLjNEZn2eJAdpbBzPGzDkDuU"
        self.emr_hash = ""
        self.pt_val_hash = ""
        self.device_hash = ""

    '''Check whether the emr_id is valid by checking emr_dict
    emr_id is given to the EMR admin when the EMR registers itself.'''
    def check_emr(self,emr_id):
        #Retrieve emr_dict
        emr_dict = helper.get_emr_dict()
        #Check if the id is present. 
        if emr_id in emr_dict.keys():
            return True
        else:
            return False

    '''Generate a key based on patient's first, last and dob
    This is the IPNS key needed to access the patient's folder'''
    def generate_key(self,config):
        hashed_config = "first=" + config["first_name"] + "last=" + config["last_name"]\
            +"dob="+config["dob"]
        #Check if key is already made currently
        for element in client.key.list()['Keys']:
            if list(element.values())[0] == hashed_config:
                return list(element.values())[1]
        key = list(client.key.gen(hashed_config,type='rsa').values())[1]
        return key

    '''Checks whether a config file has First name, last name and DOB.'''
    '''A config file is a dictionary with patient value'''
    '''For Devices, must have at least 2 identifiers'''
    def check_config(self,config,type):
        #type == 1 refers to an EMR
        if type == 1:
            #Ensure first, last and dob is present
            if "first_name" in config.keys() and \
                "last_name" in config.keys() and \
                "dob" in config.keys():
                if len(config["dob"]) == 10 and config["dob"].count('/') == 2:
                    return True
                else:
                    return False
            else:
                return False
        #type == 2 refers to a Device
        if type == 2:
            #Ensure first, last, template and dob is present
            if "first_name" in config["characteristics"].keys() and \
            "last_name" in config["characteristics"].keys() and \
            "dob" in config["characteristics"].keys():
                if len(config["characteristics"]["dob"]) == 10 and \
                config["characteristics"]["dob"].count('/') == 2:
                    if "identifiers" in config.keys() and \
                    "template" in config.keys() and \
                    "data" in config.keys():
                        return True
                else:
                    return False
            else:
                return False

    '''Setup a new patient's configuration file'''
    def pt_setup(self,config):
        #Create a new folder with title patient_data
        shutil.rmtree("patient_data")
        os.mkdir("patient_data")
        #Modify config dict so that the key is config, and identifiers are not in file. 
        new_config = dict()
        new_config["first_name"] = config["first_name"]
        new_config["last_name"] = config["last_name"]
        new_config["dob"] = config["dob"]
        new_values = dict(new_config)
        new_config.clear()
        new_config["config"] = new_values
        #Add a config file in json format
        with open("patient_data/config.json","w") as outfile:
            json.dump(new_config,outfile)
        return True

    '''Create a new device file for the patient
    If path is not changed, it means that a new patient is being made
    If it is changed, patient already has his/her folder'''
    def add_device_setup(self,config,path=""):
        file_title = helper.hash_config(config,type=1)
        if path == "":
            with open("patient_data/"+str(file_title)+".json","w") as outfile:
                json.dump(config,outfile)
        else:
            with open(path+"/"+str(file_title)+".json","w") as outfile:
                json.dump(config,outfile)

    '''Handle creation of a new patient from emr side'''
    def emr_patient(self,config,emr_id):
        #Check if emr is correct by checking for emr_id in emr_dict
        if sample.check_emr(emr_id) == False:
            return "EMR_ID is incorrect!"
        if sample.check_config(config,type=1) == False:
            return "Configuration file is invalid!"
        #Create shorthand form of config file
        config_shorthand = helper.hash_config(config)
        #Search shorthand
        pt_values_found = helper.search_pt_val(config_shorthand,ret=True)
        if pt_values_found == False:
            sample.pt_setup(config)
            key = self.generate_key(config)
            #Upload patient folder
            t1 = Thread(target=helper.upload_data,args=("patient_data",key))
            t1.start()
            #Add patient values
            t2 = Thread(target=helper.add_pt_val,args=(config_shorthand,key))
            t2.start()
            #Add emr values
            t3 = Thread(target=helper.add_emr,args=(emr_id,config_shorthand))
            t3.start()
            t2.join()
            t3.join()
        else:
            #Add patient to the emr_dict
            key = self.generate_key(config)
            helper.add_pt_val(config_shorthand,key)
            helper.add_emr(emr_id,config_shorthand)
        #Re-upload emr_dict
        Thread(target = helper.upload_emr_dict).start()
        #Re-upload patient_values
        Thread(target = helper.upload_patient_values).start()
        return True

    def device_patient(self,config):
        if sample.check_config(config,type=2) == False:
            return "Configuration file is invalid!"
        #Create shorthand form of config file
        config_shorthand = helper.hash_config(config["characteristics"])
        pt_values_found = helper.search_pt_val(config_shorthand,ret=True)
        if pt_values_found == False:
            #Make a new folder with patient's config file. 
            sample.pt_setup(config["characteristics"])
            sample.add_device_setup(config)
            #Generate the key
            key = sample.generate_key(config["characteristics"])
            #Upload this folder
            Thread(target = helper.upload_data,args=("patient_data",key)).start()
            #Add patient to patient values and device dict
            helper.add_pt_val(config_shorthand,key)
            helper.add_device(helper.hash_config(config,type=1),key)
            #Upload all
            Thread(target = helper.upload_patient_values).start()
            Thread(target = helper.upload_device_dict).start()
            return True
        else:
            #Retrieve the folder
            key = sample.generate_key(config["characteristics"])
            folder_name = helper.get_data_folder(key)
            sample.add_device_setup(config,path=folder_name + "/patient_data")
            #Upload this folder
            Thread(target = helper.upload_data,args=(folder_name,key)).start()
            #Add patient to device dictionary
            helper.add_device(helper.hash_config(config,type=1),key)
            Thread(target = helper.upload_device_dict).start()
            return True

#Classic Sample Patient: manan shukla 011201
client = ipfshttpclient.connect()
sample_config_device = {
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
    }
}
'''if template was EKG, data would look like:
        "data":{
            "s":"s-wave"
            "p":"p-wave"
        }
where s-wave and p-wave are keywords that the class would understand'''

sample_config_emr = {"first_name":"manan","last_name":"shukla","dob":"01/12/2001"}

sample = storage()
helper = storage_helper()