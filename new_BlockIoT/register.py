
from web3.auto.gethdev import w3
import json
import ipfshttpclient # type: ignore
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
client = ipfshttpclient.connect()

with open(r"new_BlockIoT/contract_data.json","r") as infile:
    contract_data = json.load(infile)

def registration(config):
    '''Only for device:
    1. We get the api call to make to the Medtronic server
    2. We use a standard or multiple standards to define incoming data. 
    3. We get the right “template” to store this data. 
    4. Total: Fname, Lname, DOB, template, api server, api parameters, standard, data
    5. We store all of these “settings” in the patient’s “hash(mananshukla011201).sol”'''
    if check_config(config) == False: return False # type: ignore
    #Create shorthand, and hash it.
    key = generate_key(config) # type: ignore
    #Create smart contract
    file1 = open(r"new_BlockIoT/Contracts/register.sol","r")
    pt_contract = str(file1.read())
    pt_contract = pt_contract.replace("contract emr","contract " + key)
    # Make sure that the contract title is hashed.
    f = open("new_BlockIoT/"+str(key) + ".sol", "w")
    f.write(pt_contract)
    f.close()
    deploy(str(key))
    add_register_data(config,key) # type: ignore

def check_config(config):
    if "first_name" in config.keys() and "last_name" in config.keys() and "dob" in config.keys():
            if config["dob"].count('-') == 2:
                return True
            else:
                return False
    else:
        return False

def generate_key(config):
    key = ""
    hashed_config = "first=" + config["first_name"] + "last=" + config["last_name"]+"dob="+config["dob"]
    found = False
    for element in client.key.list()['Keys']:
        if list(element.values())[0] == hashed_config:
            key = list(element.values())[1]
            found = True
            break
    if found == False:
        key = list(client.key.gen(hashed_config,type='rsa').values())[1]
    return key

def add_register_data(config,key):
    contract_data = dict()
    with open(r"new_BlockIoT/contract_data.json","r") as infile:
        contract_data = json.load(infile)
    contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
    contract.functions.add_biometrics(0,config["first_name"]).transact()
    contract.functions.add_biometrics(1,config["last_name"]).transact()
    contract.functions.add_biometrics(2,config["dob"]).transact()
    contract.functions.add_api_info("api server").transact()
    contract.functions.add_api_info(config["api server"]).transact()
    for element in list(config["api parameters"].keys()):
        contract.functions.add_api_info(element).transact()
        contract.functions.add_api_info(config["api parameters"][element]).transact()
    contract.functions.set_config_file(json.dumps(config)).transact()
    contract.functions.set_hash(key).transact()
    contract.functions.get_hash().call()
    contract.functions.set_consent(False).transact()
    contract.functions.control().transact()
    return True

def retrieve():
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
    
def get_data_web():
    fname = input("First Name?")
    lname = input("Last Name?")
    DOB = input("Date of Birth:", type='date',placeholder='MM-DD-YYYY')
    return [fname,lname,DOB]

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