import json
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
import time
from threading import Thread
from pywebio import start_server
from pywebio.input import input, FLOAT
from pywebio.output import put_text
from web3.auto.gethdev import w3
from datetime import datetime
import ipfshttpclient # type: ignore

with open(r"/Users/manan/Documents/BlockIoT/Code/contract_data.json","r") as infile:
    contract_data = json.load(infile)

#config = BlockIoT().retrieve()
deploy_templates("calc_adherence")

def make_api_call(contract):
    with open(r"/Users/manan/Documents/BlockIoT/Code/contract_data.json","r") as infile:
        contract_data = json.load(infile)
    key = contract.functions.get_hash().call()
    contract = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    length = contract.functions.get_api_length().call()
    config = contract.functions.get_config_file().call()
    i = 0
    api_call = list()
    while i < length:
        api_call.append(contract.functions.get_api_info(i).call())
        i += 1
    r = requests.get(api_call[1])
    df_data = dict()
    df_data = r.json()
    key = "calc_" + json.loads(contract.functions.get_config_file().call())['template']
    contract = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    contract.functions.set_data(str(df_data)).transact()
    contract.functions.set_config_file(str(config)).transact()
    contract.functions.control().transact()
    print("Made API Call")
    # print(contract.functions.get_event_length().call())
    return True

def oracle():
    while True:
        for key in contract_data.keys():
            contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
            if contract.functions.return_type().call() == "register":
                make_api_call(contract)
        for key in contract_data.keys():
            contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
            length = contract.functions.get_event_length().call()
            i = 0
            while i < length:
                event = contract.functions.get_event(i).call()
                if "GetConsent" in event:
                    get_consent(contract)
                if "PublishData" in event:
                    publish_data(contract)
                if "ParseAdherence" in event:
                    print("Parsing Adherence")
                    parse_adherence(contract)
                if "CalculateAdherence" in event:
                    print("Calculating Adherence")
                    calculate_adherence(contract)
                if "RepresentData" in event:
                    print(contract.functions.return_type().call())
                    print("Representing Adherence")
                    represent_data(contract)
                if "SendAlert" in event:
                    print("Sending Alert")
                    #send_alert(event)
                i += 1
            contract.functions.clear_event().call()
        time.sleep(2)

    with open("contract_data.json","w") as outfile:
        json.dump(contract_data, outfile)