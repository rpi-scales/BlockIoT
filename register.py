
from web3.auto.gethdev import w3
import json
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
from oracle import * # type: ignore
import ipfshttpclient # type: ignore
from pathlib import Path

PUBLISED_SMART_CONTRACT_FOLDER = 'Published/'

client = ipfshttpclient.connect()
with open(r"contract_data.json","r") as infile:
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
    file1 = open(r"Contracts/register.sol","r")
    pt_contract = str(file1.read())
    pt_contract = pt_contract.replace("contract emr","contract " + key)

    #Create the Published directory if it does not exist
    Path(PUBLISED_SMART_CONTRACT_FOLDER).mkdir(parents=True, exist_ok=True)

    # Make sure that the contract title is hashed.
    f = open("PUBLISED_SMART_CONTRACT_FOLDER"+str(key) + ".sol", "w")
    f.write(pt_contract)
    f.close()
    deploy(str(key))
    add_register_data(config,key) # type: ignore
    #Publish the templates related to the patient.
    file1 = open(r"Contracts/calc_" + config["template"] + ".sol","r")
    pt_contract = str(file1.read())
    pt_contract = pt_contract.replace("contract calc_" + config["template"],"contract calc_" + config["template"] + "_" + key)
    f = open("Published/"+"calc_"+ config["template"] + "_" + str(key) + ".sol", "w")
    f.write(pt_contract)
    f.close()
    deploy("calc_"+config["template"] + "_" + str(key))
    print("Patient " + config["first_name"] + " " + config["last_name"] + " has been registered. Template " + config["template"] + " has been published.")
    
    

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
    with open(r"contract_data.json","r") as infile:
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
