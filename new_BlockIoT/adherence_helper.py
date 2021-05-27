import json
import time
from web3.auto.gethdev import w3
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from collections import OrderedDict
from datetime import datetime,timedelta,date
import ast,statistics
import plotly.graph_objects as go
from sms import *

physician_pref = {
    "1": "0.90",
    "2": "0.80",
    "3": "0.70",
    "4": "0.60",
    "5": "0.40",
    "6": "0.30",
    "7": "0.20",
    "8": "0.20",
    "9": "0.10",
    "10": "0.10"
}

def parse_adherence(contract,represent=0):
    with open("new_BlockIoT/contract_data.json","r") as infile:
        contract_data = json.load(infile)
    key = "calc_" + json.loads(contract.functions.get_config_file().call())['template'] + "_" + str(contract.functions.get_hash().call())
    contracts = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    data = (contracts.functions.get_data().call())
    if (contracts.functions.get_config_file().call() != ""):
        config = ast.literal_eval(contracts.functions.get_config_file().call())
    else:
        return False
    pillstaken_d = []
    timestamp_d = []
    if data != "":
        data = ast.literal_eval(data)
        pillstaken_d = list(data.values())
        timestamp_d = list(data.keys())
        return dict(data)
    else:
        return False
    
def getpath(nested_dict, value, prepath=()):
    for k, v in nested_dict.items():
        path = prepath + (k,)
        if v == value: # found value
            return list(path)
        elif hasattr(v, 'items'): # v is a dict
            p = getpath(v, value, path) # recursive call
            if p is not None:
                return p

def represent_data(contract):
    config = ast.literal_eval(contract.functions.get_config_file().call())
    a = 0
    while(parse_adherence(contract,represent=1) == False):
        a += 1
        time.sleep(1)
        if a == 10:
            break
    df_data = parse_adherence(contract,represent=1)
    days30 = int(datetime.now().timestamp())- 2592000
    new_df_data = dict()
    for element in df_data.keys():
        if int(element) > days30:
            new_df_data[datetime.utcfromtimestamp(int(element)).strftime('%Y-%m-%d %H:%M:%S')] = int(df_data[element])
    formatted = dict()
    formatted["Date"] = list(new_df_data.keys())
    formatted["Amount of Medication Taken"] = list(new_df_data.values())
    df = pd.DataFrame(formatted)
    fig = px.bar(df, x="Date", y="Amount of Medication Taken",text = "Amount of Medication Taken",color="Amount of Medication Taken")
    fig.update_layout(
        title="30 Day " + config["adherence"]["medication_name"].capitalize() + " Compliance Report for " + config["first_name"].capitalize() + \
            " " + config["last_name"].capitalize() + "(" + str(config["dob"]) + ")",
        font=dict(
            family="Geneva",
            size=17,
            color="RebeccaPurple"
        )
    )
    fig.show()
    #fig = go.Figure(data=go.Scatter(x=list(new_df_data.keys()), y=list(new_df_data.values()),mode='markers',marker=dict(size=10,color="purple"))).show()

#Need to fix.
def calculate_adherence(contract):
    config = ast.literal_eval(contract.functions.get_config_file().call())
    a = 0
    while(parse_adherence(contract,represent=1) == False):
        a += 1
        time.sleep(1)
        if a == 10:
            break
    df_data = parse_adherence(contract,represent=1)
    df_data = dict((int(k),int(v)) for k,v in df_data.items())
    #Overall Average/median
    overall_comp = sum(df_data.values())/(int(((((datetime.today().timestamp() - min(list(df_data.keys())))))/60)/60)/24)
    # print("Total Compliance Dates:\n")
    # for element in sorted(df_data.keys()):
    #     print(datetime.fromtimestamp(element).strftime('%Y-%m-%d %H:%M:%S') + "-->" + str(df_data[element]))
    #30-day average
    days_30 = dict()
    day_30 = datetime.now() - timedelta(30)
    for element in df_data:
        if int(element) > int(day_30.timestamp()):
            days_30[element] = df_data[element]
    comp = sum(days_30.values())/30

    #7-day average
    days_7 = dict()
    day_7 = datetime.now() - timedelta(7)
    for element in df_data:
        if int(element) > int(day_7.timestamp()):
            days_7[element] = df_data[element]
    comp = (sum(days_7.values())/(7 * (int(config["adherence"]["Times per day"]) + 1))) * 100
    print(str(ast.literal_eval(contract.functions.get_config_file().call())["first_name"] + " compliance: " + str(comp) + "%"))
    # print("Last 30 day compliance:\n")
    # for element in sorted(days_30.keys()):
    #     print(datetime.fromtimestamp(element).strftime('%Y-%m-%d %H:%M:%S') + "-->" + str(days_30[element]))
    # print(thirty_day_comp)
    # print("Max: " + str(max(days_30.values())))
    with open("new_BlockIoT/contract_data.json","r") as infile:
        contract_data = json.load(infile)
    key = "calc_" + json.loads(contract.functions.get_config_file().call())['template'] + "_" + str(contract.functions.get_hash().call())
    contracts = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    contracts.functions.set_compliance(int(comp*100)).transact()
    contracts.functions.set_physician_average(20).transact()
    contracts.functions.physician_prefs(str(physician_pref)).transact()
    contracts.functions.check_alert().transact()

def send_alert(event,contract):
    with open("new_BlockIoT/contract_data.json","r") as infile:
        contract_data = json.load(infile)
    config = ast.literal_eval(contract.functions.get_config_file().call())
    key = "calc_" + json.loads(contract.functions.get_config_file().call())['template'] + "_" + str(contract.functions.get_hash().call())
    contracts = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    compliance = contracts.functions.get_compliance().call()
    send("Hi! Your patient " + config["first_name"] + " " + config["last_name"] + "(" + str(config["dob"]) + ")" + "has only been " + str(compliance) + "%/ compliant in the last 7 days. Send him/her a reminder alert?")
    time.sleep(2)
    #send(list(event.split(":"))[1])