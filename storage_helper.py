import ipfshttpclient # type: ignore
import json
import os
import sys
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
        with open(self.pt_val_hash + "/patient_values.json","r") as infile:
            patient_values = json.load(infile)
        return patient_values

    def get_emr_dict(self):
        '''Retrieve EMR Dictionary'''
        hash = {}
        hash = client.name.resolve(name=self.emr_dict_key)
        self.emr_hash = list(hash.values())[0].split("/")[2]
        client.get(self.emr_hash)
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
    
    '''Returns data using IPNS key'''
    def get_data_folder(self,data_key):
        hash = {}
        hash = client.name.resolve(name=data_key)
        data_hash= list(hash.values())[0].split("/")[2]
        client.get(data_hash)
        return data_hash

    '''Retrieve device data and return it'''
    def get_device_data(self,config):
        #Hash config values to search patient values dict
        pt_val_key = self.hash_config(config)
        #Search patient values dict for the config values
        key = self.search_pt_val(pt_val_key,ret=True)
        data_list = []
        if key == False: 
            return False
        else:
            hash = self.get_data_folder(key)
            device_dict = self.get_device_dict()
            for key in device_dict:
                print(device_dict[key])
                if device_dict[key] == hash:
                    
                    #removed patient_data
                    with open(hash + "/" + key + ".json","r") as infile:
                        data_dict = json.load(infile)
                        data_list.append(data_dict)
            print(data_list)

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

    '''Uploads given data into IPFS w/ IPNS key'''
    def upload_data(self,path,data_key):
        hash = dict()
        #Check if path is a folder, and upload it accordingly.
        if os.path.isdir(path):
            hash = client.add(path,recursive=True,wrap_with_directory=True)
            client.name.publish(list(hash[-1].values())[1],key=data_key)
            return True
        else:
            hash = client.add(path,wrap_with_directory=True)
        client.name.publish(list(hash[-1].values())[1],key=data_key)
        return True

    ######################
    ###### Modifiers #####
    ######################

    def push_data(self,ipns_key,device_key,data):    
        hash = self.get_data_folder(ipns_key)
        device_dict = self.get_device_dict()
        #removed patient_data
        with open(ipns_key + "/" + device_key + ".json","w") as outfile:
            json.dump(data,outfile)
        return True
        

    '''Adds a key/value to emr_dict'''
    def add_emr(self,key,value):
        #Retrieve emr_dict
        emr_dict = dict()
        emr_dict = self.get_emr_dict()
        #Add a new key if necessary
        #If not, make a new value
        if key in emr_dict:
            emr_dict[key].append(value)
        else:
            emr_dict[key] = value
        with open(self.emr_hash+ "/emr_dict.json","w") as outfile:
            json.dump(emr_dict,outfile)
        return True

    '''Adds a key/value to device_dict'''
    def add_device(self,key,value):
        #Retrieve emr_dict
        device_dict = dict()
        device_dict = self.get_device_dict()
        device_dict[key]=value
        with open(self.device_hash+ "/device_dict.json","w") as outfile:
            json.dump(device_dict,outfile)
        return True
    '''Adds a key/value to emr_dict'''
    def add_pt_val(self,key,value):
        #Retrieve emr_dict
        pt_dict = dict()
        pt_dict = self.get_patient_values()
        pt_dict[key]=value
        with open(self.pt_val_hash+ "/patient_values.json","w") as outfile:
            json.dump(pt_dict,outfile)
        return True

    #######################
    ### Other Functions ###
    #######################
    '''Search patient_value table for specific key'''
    def search_pt_val(self,pt_val_key,ret=False):
        #Get patient values dict
        pt_val = self.get_patient_values()
        #Search for the key in the dict
        if str(pt_val_key) in pt_val and ret == True:
            return pt_val[str(pt_val_key)]
        elif pt_val_key in pt_val.keys():
            return True
        else:
            return False
    
    #def search_device_dict(self,device_hash,ret=False)
        #Retrieve device dictionary

        #Search device_hash in dictionary

        #If device hash is found

            #If ret = True

                #return the value
            
            #If ret is False

                #return False

        #If device hash is not found

            #return False

    def hash_config(self,config,type=0):
        '''Hashes the first name, last name and dob of all incoming config files'''
        #Collect first name, last name, dob. 
        #Or, if it is a device, identifiers and template
        hashed_config = ""
        if type == 1:
            #Ex. patient_id=124medication_id=14125template=ekg
            for key,value in config.items():
                if key != "first_name" or key != "last_name" or key != "dob":
                    item = str(key + "=" + config[key])
                    hashed_config += item
        else:
            hashed_config = "first=" + config["first_name"] + "last=" + config["last_name"]\
            +"dob="+config["dob"]
        #Generate hash
        
        #Return hashed_config without any hashing to be done. 
        
        hashed_config = hashlib.sha224(hashed_config.encode()).hexdigest()
        return hashed_config
   
client = ipfshttpclient.connect()