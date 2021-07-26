import json
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
from parser import * # type: ignore
import time
from threading import Thread
from web3.auto.gethdev import w3
import plotly.graph_objects as go
from datetime import datetime
import ast
import pretty_errors

with open(r"contract_data.json","r") as infile:
    contract_data = json.load(infile)

def make_api_call(contract):
    with open(r"settings.json","r") as infile:
        settings = json.load(infile)
    with open(r"contract_data.json","r") as infile:
        contract_data = json.load(infile)
    old_key = contract.functions.get_hash().call()
    contract = w3.eth.contract(address=contract_data[str(old_key)][2],abi=contract_data[str(old_key)][0],bytecode=contract_data[str(old_key)][1])
    length = contract.functions.get_api_length().call()
    config = contract.functions.get_config_file().call()
    i = 0
    api_call = list()
    while i < length:
        api_call.append(contract.functions.get_api_info(i).call())
        i += 1
    config = json.loads(config)
    r = eval(config["manufacturer"])(api_call[1])
    df_data = dict()
    df_data = r
    key = "calc_" + json.loads(contract.functions.get_config_file().call())['template'] + "_" + str(old_key)
    contract = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    df_old_data = contract.functions.get_data().call()
    # if str(df_data) != str(df_old_data):
    #     send(config["communication"]["phone"],"Thanks for taking your medication today!")
    contract.functions.set_hash(old_key).transact()
    contract.functions.set_data(str(df_data)).transact()
    contract.functions.set_config_file(str(config)).transact()
    contract.functions.set_time(str(int(datetime.now().timestamp())-2 * int(settings["Delay for Representing Data(in seconds)"]))).transact()
    contract.functions.set_alerttime(str(int(datetime.now().timestamp())-2 * int(settings["Alert Fatigue Delay(in seconds)"]))).transact()
    contract.functions.control().transact()
    return True

def retrieve_data(patient):
    with open(r"contract_data.json","r") as infile:
        contract_data = json.load(infile)
    for key in contract_data.keys():
        contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
        if contract.functions.return_type().call() == "calculator":
            config = ast.literal_eval(contract.functions.get_config_file().call())
            if config["first_name"].lower() == patient["first_name"].lower():
                if config["last_name"].lower() == patient["last_name"].lower():
                    #contract.functions.represent().transact()
                    fig = represent_data(contract)
                    break

def oracle():
    with open(r"settings.json","r") as infile:
        settings = json.load(infile)
    for key in contract_data.keys():
        contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
        if contract.functions.return_type().call() == "register":
            make_api_call(contract)
    for key in contract_data.keys():
        contract = w3.eth.contract(address=contract_data[key][2],abi=contract_data[key][0],bytecode=contract_data[key][1])
        length = contract.functions.get_event_length().call()
        i = 0
        used = []
        while i < length:
            event = contract.functions.get_event(i).call()
            if "ParseAdherence" in event:
                #print(str(ast.literal_eval(contract.functions.get_config_file().call())["first_name"]) + ": Parsing Adherence")
                parse_adherence(contract)
                used.append(event)
            if "CalculateAdherence" in event:
                #print(str(ast.literal_eval(contract.functions.get_config_file().call())["first_name"]) + ": Calculating Adherence")
                calculate_adherence(contract)
                used.append(event)
            if "RepresentData" in event:
                if (int(datetime.now().timestamp()) - int(contract.functions.get_time().call()) > int(settings["Delay for Representing Data(in seconds)"])):
                    #print(str(ast.literal_eval(contract.functions.get_config_file().call())["first_name"] + ": Representing Adherence"))
                    fig = represent_data(contract)
                    contract.functions.set_time(str(int(datetime.now().timestamp()))).transact()
                    used.append(event)
                else:
                    pass
                    print("Time limit has passed")
            if "SendAlert" in event:
                if (int(datetime.now().timestamp()) - int(contract.functions.get_alerttime().call()) > int(settings["Alert Fatigue Delay(in seconds)"])):
                    #print(str(ast.literal_eval(contract.functions.get_config_file().call())["first_name"] + ": Sending Alert"))
                    send_alert(event,contract)
                    contract.functions.set_alerttime(str(int(datetime.now().timestamp()))).transact()
                    used.append(event)
                else:
                    pass
                    print("Time limit for alerts has passed: " + str((int(datetime.now().timestamp()) - int(contract.functions.get_alerttime().call()))))
            i += 1
        contract.functions.clear_event().transact()