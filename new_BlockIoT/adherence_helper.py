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
    with open("contract_data.json","r") as infile:
        contract_data = json.load(infile)
    key = "calc_adherence"
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
    a = 0
    while(parse_adherence(contract,represent=1) == False):
        a += 1
        time.sleep(1)
        if a == 10:
            break
    df_data = parse_adherence(contract,represent=1)
    new_df_data = dict()
    for element in df_data.keys():
        new_df_data[datetime.utcfromtimestamp(int(element)).strftime('%Y-%m-%d %H:%M:%S')] = df_data[element]
    print("here")
    go.Figure(data=go.Scatter(x=list(new_df_data.keys()), y=list(new_df_data.values()),mode='markers',marker=dict(size=20,color="red"))).show()

#Need to fix.
def calculate_adherence(contract):
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
    #30-day average_median
    days_30 = dict()
    day_30 = datetime.now() - timedelta(30)
    for element in df_data:
        if int(element) > int(day_30.timestamp()):
            days_30[element] = df_data[element]
    thirty_day_comp = sum(days_30.values())/30
    with open("contract_data.json","r") as infile:
        contract_data = json.load(infile)
    key = "calc_adherence"
    contracts = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    contracts.functions.set_compliance(int(thirty_day_comp*100)).transact()
    contracts.functions.set_physician_average(20).transact()
    contracts.functions.physician_prefs(str(physician_pref)).transact()
    contracts.functions.check_alert().transact()

def send_alert(event):
    send("Your patient is not compliant!")
    #send(list(event.split(":"))[1])