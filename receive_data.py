import json
from flask import Flask
app = Flask(__name__)
from flask import request
from storage_helper import storage_helper
from storage import storage
from data_template import data_template
from threading import Thread

store = storage()
helper = storage_helper()
template = data_template()

@app.route("/create", methods=['POST']) # type: ignore
def create_patient():
    '''Create a new patient given config file of patient'''
    if request.method == 'POST':
        json_data = request.get_json()
        json_data = dict(json_data)
        if json_data["party"] == "EMR":
            print(store.emr_patient(json_data["config"],json_data["emr_id"]))
        else:
            store.device_patient(json_data["config"])
        return "Successfully Recieved"

@app.route("/data", methods=['GET']) # type: ignore
def get_data():
    if request.method == 'GET':
        json_data = request.get_json()
        json_data = dict(json_data)
        template.get_device_data(json_data)
        return "Successful"

@app.route("/data", methods=['POST']) # type: ignore
def post_data():
    if request.method == 'POST':
        json_data = request.get_json()
        json_data = dict(json_data)
        template.push_data(json_data)
        return "Successful"