import json
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from threading import Thread
from storage_helper import storage_helper
import data_template
from storage import storage

sample = storage()
helper = storage_helper()
template = data_template.data_template()

a = 0
print("Setting up environment. This may take a while.")
print("Resolving dictionaries/templates to cache")
while a < 10:
    helper.get_device_dict()
    helper.get_emr_dict()
    helper.get_patient_values()
    template.get_template("Adherence")
    template.get_template_dict()
    a+=1
print("Storing data to cache")
a = 0
pt_val = dict()
pt_val = helper.get_patient_values()
while a < 10:
    for value in pt_val.values():
        try:
            helper.get_data_folder(value)
        except:
            pass
    a += 1