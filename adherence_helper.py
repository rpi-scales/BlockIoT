import json
import time,schedule
from web3.auto.gethdev import w3
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from collections import OrderedDict
from datetime import datetime,timedelta,date
import ast,pyperclip
import plotly.graph_objects as go
from SMS.sms import *
import ast

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

def parse_adherence(contract):
    with open("contract_data.json","r") as infile:
        contract_data = json.load(infile)
    config = contract.functions.get_config_file().call()
    key = "calc_" + ast.literal_eval(config)["template"]+ "_" + str(contract.functions.get_hash().call())
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
    print("first_name")
    config = ast.literal_eval(contract.functions.get_config_file().call())
    a = 0
    while(parse_adherence(contract) == False):
        a += 1
        time.sleep(1)
        if a == 10:
            break
    df_data = parse_adherence(contract)
    days30 = int(datetime.now().timestamp())- 2592000
    new_df_data = dict()
    for element in df_data.keys():
        if int(element) > days30:
            new_df_data[datetime.utcfromtimestamp(int(element)).strftime('%Y-%m-%d %H:%M:%S')] = int(df_data[element])
    formatted = dict()
    formatted["Date"] = list(new_df_data.keys())
    formatted["Amount of Medication Taken"] = list(new_df_data.values())
    df = pd.DataFrame(formatted)
    fig = px.bar(df, x="Date", y="Amount of Medication Taken",text = "Amount of Medication Taken",color="Amount of Medication Taken",color_continuous_scale=px.colors.sequential.Reds)
    fig.update_layout(
        title="30 Day " + config["adherence"]["medication_name"].title() + " Compliance Report for " + config["first_name"].capitalize() + \
            " " + config["last_name"].capitalize() + "(" + str(config["dob"]) + ")",
        font=dict(
            family="Geneva",
            size=17,
            color="#40376E"
        ),
        height=800
    )
    #fig.show()
    with open("/graph.json", 'w') as f:
        f.write(fig.to_json())
    #fig = go.Figure(data=go.Scatter(x=list(new_df_data.keys()), y=list(new_df_data.values()),mode='markers',marker=dict(size=10,color="purple"))).show()

#Need to fix.
def calculate_adherence(contract):
    config = ast.literal_eval(contract.functions.get_config_file().call())
    a = 0
    while(parse_adherence(contract) == False):
        a += 1
        time.sleep(1)
        if a == 10:
            break
    df_data = parse_adherence(contract)
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
    #print(str(ast.literal_eval(contract.functions.get_config_file().call())["first_name"] + " compliance: " + str(comp) + "%"))
    # print("Last 30 day compliance:\n")
    # for element in sorted(days_30.keys()):
    #     print(datetime.fromtimestamp(element).strftime('%Y-%m-%d %H:%M:%S') + "-->" + str(days_30[element]))
    # print(thirty_day_comp)
    # print("Max: " + str(max(days_30.values())))
    with open("contract_data.json","r") as infile:
        contract_data = json.load(infile)
    key = "calc_" + ast.literal_eval(contract.functions.get_config_file().call())['template'] + "_" + str(contract.functions.get_hash().call())
    contracts = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    contracts.functions.set_compliance(int(comp*100)).transact()
    contracts.functions.set_physician_average(20).transact()
    contracts.functions.physician_prefs(str(physician_pref)).transact()
    contracts.functions.check_alert().transact()

def daily_alerts(contract):
    config = ast.literal_eval(contract.functions.get_config_file().call())
    scheduler = {
        1:["08:00"],
        2:["08:00","12:00"],
        3:["08:00","12:00","17:00"]
    }
    if int(config["alerts"]["reminders"]) == 1:
        if int(config["adherence"]["Times per day"]) >= 3:
            schedule.every().day.at(scheduler[3][0]).do(send,to=config["communication"]["phone"],message="Good Morning!")
            schedule.every().day.at(scheduler[3][0]).do(send,to=config["communication"]["phone"],\
                message="This is BlockIoT, just sending you a quick reminder to take your "+ config["adherence"]["medication_name"] + " before 12. Thanks!")

            schedule.every().day.at(scheduler[3][1]).do(send,to=config["communication"]["phone"],message="Good Afternoon!")
            schedule.every().day.at(scheduler[3][1]).do(send,to=config["communication"]["phone"],\
                message="This is BlockIoT, just sending you a quick reminder to take your "+ config["adherence"]["medication_name"] + " before this evening. Thanks!")

            schedule.every().day.at(scheduler[3][1]).do(send,to=config["communication"]["phone"],message="Good Afternoon!")
            schedule.every().day.at(scheduler[3][2]).do(send,to=config["communication"]["phone"],\
                message="This is BlockIoT, just sending you a quick reminder to take your "+ config["adherence"]["medication_name"] + " before you go to bed. Thanks!")
        else:
            for element in scheduler[int(config["adherence"]["Times per day"])]:
                schedule.every().day.at(element).do(send,to=config["communication"]["phone"],message="Hi!")
                schedule.every().day.at(element).do(send,to=config["communication"]["phone"],\
                    message="This is BlockIoT, just sending you a quick reminder to take your "+ config["adherence"]["medication_name"] + " today. Thanks!")
    if int(config["alerts"]["daily_summary"]) == 1:
        schedule.every().day.at("23:00").do(daily_summary,contract=contract)
        
def daily_summary(contract):
    config = ast.literal_eval(contract.functions.get_config_file().call())
    df_data = parse_adherence(contract)
    today = str(int(datetime.today().timestamp()) - int(datetime.today().timestamp()) % 86400)
    if df_data[str(today)] == config["adherence"]["Times per day"]:
        send(config["communication"]["phone"],"You took all of your medications for today! Great Job!")
    if df_data[str(today)] < config["adherence"]["Times per day"]:
        send(config["communication"]["phone"],"Hey, you forgot to take your medication today! No worries- please remember to do it tomorrow :)")

def send_alert(event,contract):
    with open("contract_data.json","r") as infile:
        contract_data = json.load(infile)
    config = ast.literal_eval(contract.functions.get_config_file().call())
    key = "calc_" + json.loads(contract.functions.get_config_file().call())['template'] + "_" + str(contract.functions.get_hash().call())
    contracts = w3.eth.contract(address=contract_data[str(key)][2],abi=contract_data[str(key)][0],bytecode=contract_data[str(key)][1])
    compliance = contracts.functions.get_compliance().call()
    send("Hi! Your patient " + config["first_name"] + " " + config["last_name"] + "(" + str(config["dob"]) + ")" + "has only been " + str(compliance) + "%/ compliant in the last 7 days. Send him/her a reminder alert?")
    time.sleep(2)
    #send(list(event.split(":"))[1])