import json
import os
import sys
import hashlib
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

    '''Check whether the emr_id is valid by checking emr_dict'''
    def check_emr(self,emr_id):
        #Retrieve emr_dict
        emr_dict = helper.get_emr_dict()
        #Check if the id is present. 
        if emr_id in emr_dict.keys():
            return True
        else:
            return False

    '''Generate a key based on patient's first, last and dob'''
    def generate_key(self,config):
        hashed_config = "first=" + config["first_name"] + "last=" + config["last_name"]\
            +"dob="+config["dob"]
        current_keys = dict()
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
            if "first_name" in config["characteristics"].keys() and \
                "last_name" in config["characteristics"].keys() and \
                "dob" in config["characteristics"].keys():
                
                if len(config["dob"]) == 10 and config["dob"].count('/') == 2:
                    return True
                else:
                    return False
            else:
                return False
        #type == 2 refers to a Device
        if type == 2:
            #Ensure first, last, template and dob is present
            if "first_name" in config.keys() and "template" in config.keys() and "last_name" in config.keys() and "dob" in config.keys():
                if len(config["dob"]) == 10 and config["dob"].count('/') == 2:
                    return True
                else:
                    return False
            else:
                return False

    '''Setup a new patient'''
    def pt_setup(self,config):
        #Create a new folder with title patient_data
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

    '''Create a new device file for the patient'''
    def add_device_setup(self,config,path=""):
        #Delete this line. File title is for now just a string of the patient information
        file_title = helper.hash_config(config,type=1)

        new_config = dict()
        for key,value in config.items():
            if key == "first_name" or key == "last_name" or key == "dob":
                continue
            else:
                new_config[key] = value
        if path == "":

            #No need to use patient_data. Delete that folder
            with open("patient_data/"+str(file_title)+".json","w") as outfile:
                json.dump(new_config,outfile)
        else:
            with open(path+"/"+str(file_title)+".json","w") as outfile:
                json.dump(new_config,outfile)

    '''Handle creation of a new patient from emr side'''
    def emr_patient(self,config,emr_id):
        #Check if config file is valid
        if self.check_config(config,type=1) == False:
            return 1
        #Check if emr is valid. 
        if self.check_emr(emr_id) == False:
            return 2
        #Hash config values to search patient values dict
        pt_val_key = helper.hash_config(config)
        #Search patient values dict for the config values
        if helper.search_pt_val(pt_val_key) == True:
            #Add patient to the emr_dict
            key = self.generate_key(config)
            helper.add_emr(emr_id,key)
            helper.add_pt_val(pt_val_key,key)
        else:
            #If not found, create a new folder for patient. 
            self.pt_setup(config)
            #Upload folder to IPFS.
            key = self.generate_key(config)
            helper.upload_data("patient_data",key)
            #Add new key/value to the emr_dict
            helper.add_emr(emr_id,key)
            helper.add_pt_val(pt_val_key,key)
        #Re-upload emr_dict
        helper.upload_emr_dict()
        #Re-upload patient_values
        helper.upload_patient_values()
        return True

    '''Handle creation of a new patient from device side'''
    def device_patient(self,config):
        #Check if config file is valid
        if self.check_config(config,type=2) == False:
            return 1
        #Hash config values to search patient values dict
        pt_val_key = helper.hash_config(config)
        #Search patient values dict for the config values
        key = helper.search_pt_val(pt_val_key,ret=True)
        if key == False:
            #If not found, create a new folder for patient. 
            self.pt_setup(config)
            self.add_device_setup(config)
            #Upload folder to IPFS.
            key = self.generate_key(config)
            helper.upload_data("patient_data",key)
            #Update and upload patient values
            helper.add_pt_val(pt_val_key,key)
            helper.upload_patient_values()
            helper.add_device(helper.hash_config(config,type=1),key)
            helper.upload_device_dict()
        else:
            key = self.generate_key(config)
            hash = helper.get_data_folder(key)
            self.add_device_setup(config,hash)
            helper.upload_patient_values()
            helper.add_device(helper.hash_config(config,type=1),key)
            helper.upload_device_dict()

#Classic Sample Patient: manan shukla 011201
client = ipfshttpclient.connect()
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
        "Pills Taken":"int"
    }
}
sample = storage()
helper = storage_helper()
print(helper.check_config