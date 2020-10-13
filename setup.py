import json
import subprocess,os,sys
from flask import config
import ipfshttpclient # type: ignore
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from threading import Thread
from storage_helper import storage_helper
import data_template
from storage import storage

client = ipfshttpclient.connect()

a = 0
print("Setting up environment. This may take a while.")
print("Resolving dictionaries/templates to cache")

def publish(dict_list):
    print(subprocess.call("ipfs name publish " + dict_list[0] + " --key=" + dict_list[1]))
    return True

def setup_dicts(name):
    print("Generating "+name+" and uploading to IPFS")
    hashed_dict = dict()
    hashed_dict = client.add(name + ".json",wrap_with_directory=True)
    ipfs_hash = list(hashed_dict[1].values())[1]
    key1=""
    for element in client.key.list()['Keys']:
        if list(element.values())[0] == name:
            key1=list(element.values())[1]
    if key1 == "":
        key1=list(client.key.gen(name,type='rsa').values())[1]
    env_list = list()
    with open("env.json","r") as infile:
        env_list=json.load(infile)
    env_list.append(key1)
    with open("env.json","w") as outfile:
        json.dump(env_list,outfile)

    return [ipfs_hash,key1]

open('env.json', 'w').close()
env_list = []
with open("env.json","w") as outfile:
    json.dump(env_list,outfile)

list1 = setup_dicts("emr_dict")
list2 = setup_dicts("patient_values")
list3 = setup_dicts("device_dict")

Thread(target=publish,args=(list1,)).start()
Thread(target=publish,args=(list2,)).start()
Thread(target=publish,args=(list3,)).start()

hashed_dict = dict()
hashed_dict = client.add("adherence_template.json",wrap_with_directory=True)
ipfs_hash = list(hashed_dict[1].values())[1]
key1=""
for element in client.key.list()['Keys']:
    if list(element.values())[0] == "adherence_template":
        key1=list(element.values())[1]
if key1 == "":
    key1=list(client.key.gen("adherence_template",type='rsa').values())[1]
template_dict = dict()
template_dict["adherence"] = key1
Thread(target=publish,args=([ipfs_hash,key1],)).start()

with open("template_dict.json","w") as outfile:
    json.dump(template_dict,outfile)

list4 = setup_dicts("template_dict")
Thread(target=publish,args=(list4,)).start()