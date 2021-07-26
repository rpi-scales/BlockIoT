from threading import Thread
from register import * # type: ignore
from adherence_helper import * # type: ignore
from solidity_helper import * # type: ignore
from blockchain import * # type: ignore
from oracle import * # type: ignore
import schedule,os

# Keywords such as BL_timestamp signify what type of data will be present there. 

with open(r"contract_data.json","w") as infile:
    json.dump({},infile)
config = list()
with open("configs.json") as f:
    config = json.load(f)
for element in config:
    registration(element)
#To view a patient's data...
patient_1 = {
    "first_name":"kavin",
    "last_name":"shukla",
    "dob":"01-12-2001"
}
def oracle_handler():
    while True:
        oracle()
        time.sleep(1)
        schedule.run_pending()
        time.sleep(1)

def retrieve():
    while True:
        time.sleep(1)
        some_data = dict()
        with open("command.json") as f:
            some_data = json.load(f)
            f.close()
        if some_data != {}:
            print("Got it")
            retrieve_data(some_data)
            with open("command.json","w") as f:
                json.dump({},f)
                f.close()
        time.sleep(1)

t1 = Thread(target=oracle_handler).start()
time.sleep(1)
t2 = Thread(target=retrieve).start()
