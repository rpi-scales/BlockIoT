import json
from register import * # type: ignore
from calc_adherence import * # type: ignore
import time
from threading import Thread
from pywebio import start_server
from pywebio.input import input, FLOAT
from pywebio.output import put_text
from storage_helper import helper_functions
from blockchain import *
from web3.auto.gethdev import w3
from datetime import datetime
import ipfshttpclient # type: ignore

class BlockIoT:
    def registration(self,config):
        '''Only for device:
        1. We get the api call to make to the Medtronic server
        2. We use a standard or multiple standards to define incoming data. 
        3. We get the right “template” to store this data. 
        4. Total: Fname, Lname, DOB, template, api server, api parameters, standard, data
        5. We store all of these “settings” in the patient’s “hash(mananshukla011201).sol”'''
        print("Checking Config")
        if check_config(config) == False: return False # type: ignore
        #Create shorthand, and hash it.
        print("Generating Key")
        key = generate_key(config) # type: ignore
        #Create smart contract
        file1 = open(r"new_BlockIoT/register.sol","r")
        pt_contract = str(file1.read())
        pt_contract = pt_contract.replace("contract emr","contract " + key)
        # Make sure that the contract title is hashed.
        f = open(str(key) + ".sol", "w")
        f.write(pt_contract)
        f.close()
        print("Deploying contract")
        deploy(str(key))
        print("Adding registration data")
        add_register_data(config,key) # type: ignore

    def retrieve(self):
        config = self.get_data_web()
        hashed_config = "first=" + config[0] + "last=" + config[1]+"dob="+config[2]
        found = False
        old_key = ""
        for element in client.key.list()['Keys']:
            if list(element.values())[0] == hashed_config:
                old_key = list(element.values())[1]
                found = True
                break
        if found == False:
            print("Patient not registered!")
            exit(0)
        # Create Transaction
        w3.eth.send_transaction({'to': w3.eth.coinbase, 'from': w3.eth.coinbase})
        file1 = open(r"new_BlockIoT/retrieve.sol","r")
        pt_contract = str(file1.read())
        pt_contract = pt_contract.replace("contract retrieve","contract " + old_key + "_retrieve")
        pt_contract = pt_contract.replace("Base",old_key)
        # Make sure that the contract title is hashed.
        f = open(str(old_key) + "_retrieve.sol", "w")
        f.write(pt_contract)
        f.close()
        deploy(str(old_key) + "_retrieve")
        contract_data = dict()
        with open("contract_data.json","r") as infile:
            contract_data = json.load(infile)
        contract = w3.eth.contract(address=contract_data[str(old_key) + "_retrieve"][2],abi=contract_data[str(old_key) + "_retrieve"][0],bytecode=contract_data[str(old_key) + "_retrieve"][1])
        contract.functions.set_hash(old_key).transact()
        contract.functions.set_watch_addr(contract_data[old_key][2]).transact()
        times = contract.functions.get_time().call()
        contract.functions.set_time(times + 600).transact()
        contract_old = w3.eth.contract(address=contract_data[str(old_key)][2],abi=contract_data[str(old_key)][0],bytecode=contract_data[str(old_key)][1])
        contract.functions.handle_retrieve().transact()
        return config
        
    def get_data_web(self):
        fname = input("First Name?")
        lname = input("Last Name?")
        DOB = input("Date of Birth:", type='date',placeholder='MM-DD-YYYY')
        return [fname,lname,DOB]

with open(r"/Users/manan/Documents/BlockIoT/Code/contract_data.json","r") as infile:
    contract_data = json.load(infile)
client = ipfshttpclient.connect()
# Keywords such as BL_timestamp signify what type of data will be present there. 
config= {
    "first_name":"manan",
    "last_name":"shukla",
    "dob":"01-12-2001",
    "api server": "http://localhost:8000/new_BlockIoT/server_data.json",
    "api parameters": {},
    "template":"adherence",
    "identifiers":{
        "BL_timestamp":"BL_pillstaken"
    },
}

BlockIoT().registration(config)
#config = BlockIoT().retrieve()
deploy_templates("calc_adherence")

print("In loop")
while True:
    for key in contract_data.keys():
        contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
        if contract.functions.return_type().call() == "register":
            helper_functions().make_api_call(contract)
    for key in contract_data.keys():
        contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
        length = contract.functions.get_event_length().call()
        i = 0
        while i < length:
            event = contract.functions.get_event(i).call()
            if "GetConsent" in event:
                helper_functions().get_consent(contract)
            if "PublishData" in event:
                helper_functions().publish_data(contract)
            if "ParseAdherence" in event:
                print("Parsing Adherence")
                parse_adherence(contract)
            if "CalculateAdherence" in event:
                print("Calculating Adherence")
                calculate_adherence(contract)
            if "RepresentData" in event:
                print("Representing Adherence")
               # represent_data(contract)
              #  exit(0)
            if "SendAlert" in event:
                print("Sending Alert")
                send_alert(event)
                exit(0)
            i += 1
        contract.functions.clear_event().call()
    time.sleep(2)

with open("contract_data.json","w") as outfile:
    json.dump(contract_data, outfile)