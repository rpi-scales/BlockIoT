from flask import config
import ipfshttpclient # type: ignore
import json
import os
import os.path
import time
from os import path
import hashlib

class storage_helper:
    def __init__(self):
        self.patient_values_peer = "QmX2EGscc7jbRwNtUdU9Mkp5Y7zaNUrrWrFq2v8Ai7f1GM"
        self.emr_dict_key = "QmSQCE5pZ4jAaxdBbrZs6PKB3mWUUH2kewvJT3jEXtQQEu"
        self.device_dict_key = "QmaZvWEJbSyptzD4bVHMZhYLjNEZn2eJAdpbBzPGzDkDuU"
        self.emr_hash = ""
        self.pt_val_hash = ""
        self.device_hash = ""

    ######################
    ###### GETTERS #######
    ######################
    def get_patient_values(self):
        '''Retrieve patient values dictionary'''
        hash = {}
        hash = client.name.resolve(name=self.patient_values_peer)
        self.pt_val_hash = list(hash.values())[0].split("/")[2]
        client.get(self.pt_val_hash)
        #Time out in 30 seconds
        a = 30
        while a > 0:
            if path.exists(self.pt_val_hash + "/patient_values.json"):
                break
            else:
                a -= 1
                time.sleep(1)
        with open(self.pt_val_hash + "/patient_values.json","r") as infile:
            patient_values = json.load(infile)
        return patient_values

    def get_emr_dict(self):
        '''Retrieve EMR Dictionary'''
        hash = {}
        hash = client.name.resolve(name=self.emr_dict_key)
        self.emr_hash = list(hash.values())[0].split("/")[2]
        client.get(self.emr_hash)
        #Time out in 30 seconds
        a = 30
        while a > 0:
            if path.exists(self.emr_hash + "/emr_dict.json"):
                break
            else:
                a -= 1
                time.sleep(1)
        with open(self.emr_hash + "/emr_dict.json","r") as infile:
            emr_dict = json.load(infile)
        return emr_dict

    def get_device_dict(self):
        '''Retrieve Device Dictionary'''
        hash = {}
        hash = client.name.resolve(name=self.device_dict_key)
        self.device_hash = list(hash.values())[0].split("/")[2]
        client.get(self.device_hash)
        with open(self.device_hash + "/device_dict.json","r") as infile:
            device_dict = json.load(infile)
        return device_dict
    
    def get_data_folder(self,data_key):
        '''Returns data using IPNS key'''
        hash = {}
        hash = client.name.resolve(name=data_key)
        folder_title= list(hash.values())[0].split("/")[2]
        client.get(folder_title)
        return folder_title

    ######################
    ###### SETTERS #######
    ######################

    def upload_patient_values(self):
        '''Upload patient values dictionary'''
        hashed_dict = client.add(self.pt_val_hash+"/patient_values.json",wrap_with_directory=True)
        ipfs_hash = list(hashed_dict[1].values())[1]
        client.name.publish(ipfs_hash,key=self.patient_values_peer)
        return True

    def upload_emr_dict(self):
        '''Upload emr_dict to IPFS'''
        hashed_dict = dict()
        hashed_dict = client.add(self.emr_hash+"/emr_dict.json",wrap_with_directory=True)
        ipfs_hash = list(hashed_dict[1].values())[1]
        client.name.publish(ipfs_hash,key=self.emr_dict_key)
        return True

    def upload_device_dict(self):
        '''Upload emr_dict to IPFS'''
        hashed_dict = dict()
        hashed_dict = client.add(self.device_hash+"/device_dict.json",wrap_with_directory=True)
        ipfs_hash = list(hashed_dict[1].values())[1]
        client.name.publish(ipfs_hash,key=self.device_dict_key)
        return True

    def upload_data(self,path,data_key):
        '''Uploads given data into IPFS w/ IPNS key'''
        hash = dict()
        '''Check if path is a folder, and upload it accordingly.'''
        if os.path.isdir(path):
            hash = client.add(path,recursive=True)
            client.name.publish(list(hash[-1].values())[1],key=data_key)
            return True
        else:
            hash = client.add(path,wrap_with_directory=True)
        client.name.publish(list(hash[-1].values())[1],key=data_key)
        return True

    ######################
    ###### Modifiers #####
    ######################
      
    def add_emr(self,key,value):
        '''Adds a key/value to emr_dict'''
        #Retrieve emr_dict
        emr_dict = dict()
        emr_dict = self.get_emr_dict()
        #Add a new key if necessary
        #If not, make a new value
        if self.search_emr(key,value) == True:
            return True
        if key in emr_dict:
            emr_dict[key].append(value)
        else:
            emr_dict[key] = value
        with open(self.emr_hash+ "/emr_dict.json","w") as outfile:
            json.dump(emr_dict,outfile)
        return True

    def add_device(self,key,value):
        '''Adds a key/value to device_dict'''
        #Retrieve emr_dict
        device_dict = dict()
        device_dict = self.get_device_dict()
        if key in device_dict.keys() and value == device_dict[key]:
            return True
        else:
            device_dict[key]=value
            with open(self.device_hash+ "/device_dict.json","w") as outfile:
                json.dump(device_dict,outfile)
            return True

    def add_pt_val(self,key,value):
        '''Adds a key/value to emr_dict'''
        #Retrieve emr_dict
        pt_dict = dict()
        pt_dict = self.get_patient_values()
        if key in pt_dict.keys() and value == pt_dict[key]:
            return True
        else:
            pt_dict[key]=value
            with open(self.pt_val_hash+ "/patient_values.json","w") as outfile:
                json.dump(pt_dict,outfile)
            return True

    #######################
    ### Other Functions ###
    #######################
    def search_pt_val(self,pt_val_key,ret=False):
        '''Search patient_value table for specific key'''
        #Get patient values dict
        pt_val = self.get_patient_values()
        #Search for the key in the dict
        if str(pt_val_key) in pt_val and ret == True:
            return pt_val[str(pt_val_key)]
        elif pt_val_key in pt_val.keys():
            return True
        else:
            return False
    
    def search_emr(self,key,value):
        '''Search emr_dict given key and value. Value must be given as well as value is a list. '''
        #Retrieve emr_dict
        emr_dict = self.get_emr_dict()
        #Add a new key if necessary
        #If not, make a new value
        if value in emr_dict[key]:
            return True
        else:
            return False

    def search_device_dict(self,key,ret=False):
        '''Search device_dict for key or value'''
        #Retrieve device_dict
        device_dict = self.get_device_dict()
        if key in device_dict and ret==False:
            return True
        elif key in device_dict and ret==True:
            return device_dict[key]
        else:
            return False

    def hash_config(self,config,type=0):
        '''Hashes the first name, last name and dob of all incoming config files'''
        '''Why 2 types? 1 for pt values table to actually get the folder. 
        The other one is to find the title of the file and search device_dict keys'''
        #Collect first name, last name, dob. 
        #Or, if it is a device, identifiers and template
        hashed_config = ""
        if type == 1:
            #Ex. patient_id=124medication_id=14125template=ekg
            for key,value in config["identifiers"].items():
                item = str(key + "=" + config["identifiers"][key])
                hashed_config += item
            hashed_config+="template"+ "="+config["template"]
        else:
            hashed_config = "first=" + config["first_name"] + "last=" + config["last_name"]\
            +"dob="+config["dob"]
        return hashed_config
   
client = ipfshttpclient.connect()

sample_get_data_request = {
    "first_name":"manan",
    "last_name":"shukla",
    "dob":"01/12/2001"
}