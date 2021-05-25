import json
import time 
import requests
from datetime import datetime
from pywebio import start_server
from pywebio.input import input, FLOAT
from pywebio.output import put_text
import plotly.graph_objects as go
from web3.auto.gethdev import w3
import pandas as pd # type: ignore
import plotly.express as px
import plotly
from collections import OrderedDict
import ipfshttpclient # type: ignore
import os.path
from os import path

client = ipfshttpclient.connect()
if path.exists(r"new_BlockIoT/contract_data.json"):
    with open(r"new_BlockIoT/contract_data.json","r") as infile:
        contract_data = json.load(infile)
else:
    infile = open(r"new_BlockIoT/contract_data.json","w")
    infile.write("{}")
    infile.close()
    with open(r"new_BlockIoT/contract_data.json","r") as infile:
        contract_data = json.load(infile)

def get_consent(contract):
    key = contract.functions.get_hash().call()
    contract_old = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    if(contract_old.functions.check_consent().call() == False):
        consent = input("Please enter \"CONSENT\" to allow your physician to access your medical device data?")
        if consent == "CONSENT":
            contract_old.functions.set_consent(True).transact()
            return True

def publish_data(self,contract):
    key = contract.functions.get_hash().call()
    contract_old = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    length = contract_old.functions.get_api_length().call()
    i = 0
    api_call = list()
    while i < length:
        api_call.append(contract_old.functions.get_api_info(i).call())
        i += 1
    r = requests.get(api_call[1])
    df_data = dict()
    df_data = r.json()
    new_df_data = dict()
    for element in df_data.keys():
        new_df_data[datetime.utcfromtimestamp(int(element)).strftime('%Y-%m-%d %H:%M:%S')] = df_data[element]
    go.Figure(data=go.Scatter(x=list(new_df_data.keys()), y=list(new_df_data.values()),mode='markers',marker=dict(size=20,color="red"))).show()
    return True
