
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
from oracle import * # type: ignore

# Keywords such as BL_timestamp signify what type of data will be present there. 
config= {
    "first_name":"manan",
    "last_name":"shukla",
    "dob":"01-12-2001",
    "api server": "http://localhost:8000/new_BlockIoT/server_data.json",
    "api parameters": {},
    "template":"adherence",
    "identifiers":{
        "BL_timestamp":"BL_pillstaken"
    },
}

#registration(config)
print("Patient is Registered")
oracle()