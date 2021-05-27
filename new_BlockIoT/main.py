
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
from oracle import * # type: ignore
from threading import Thread

# Keywords such as BL_timestamp signify what type of data will be present there. 
config= {
    "first_name":"manan",
    "last_name":"shukla",
    "dob":"01-12-2001",
    "communication":{
        "phone":"5162708383",
        "email":"manan.shukla2001@gmail.com",
    },
    "api server": "http://localhost:8000/new_BlockIoT/server_data.json",
    "api parameters": {},
    "template":"adherence",
    "adherence":{
        "medication_name":"Albuterol",
        "Dosage":"90 mcg",
        "Times per day":"0"
    },
    "identifiers":{
        "BL_timestamp":"BL_pillstaken"
    },
}
config2 = {
    "first_name":"kavin",
    "last_name":"shukla",
    "dob":"01-12-2001",
    "communication":{
        "phone":"5162708383",
        "email":"manan.shukla2001@gmail.com",
    },
    "api server": "http://localhost:8000/new_BlockIoT/server_data2.json",
    "api parameters": {},
    "template":"adherence",
    "adherence":{
        "medication_name":"Albuterol",
        "Dosage":"90 mcg",
        "Times per day":"0"
    },
    "identifiers":{
        "BL_timestamp":"BL_pillstaken"
    },
}

registration(config)
registration(config2)

#To view a patient's data...
patient_1 = {
    "first_name":"kavin",
    "last_name":"shukla",
    "dob":"01-12-2001"
}
t1 = Thread(target=oracle).start()
time.sleep(4)
t2 = Thread(target=retrieve_data,args=(patient_1,)).start()


