
from web3.auto.gethdev import w3
import json
import ipfshttpclient # type: ignore
client = ipfshttpclient.connect()

def check_config(config):
    if "first_name" in config.keys() and "last_name" in config.keys() and "dob" in config.keys():
            if config["dob"].count('-') == 2:
                print("Config file is valid")
            else:
                print("Config file is invalid!")
                return False
    else:
        print("Config file is invalid!")
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
    with open("contract_data.json","r") as infile:
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