import multiprocessing
import time
from subprocess import DEVNULL, call


def start_ethereum():
    call(["/home/ec2-user/go/bin/geth","--dev","--ipcpath","/home/ec2-user/.ethereum/geth.ipc"],stderr=DEVNULL,stdout=DEVNULL)

def start_ipfs():
    call(["ipfs","daemon"],stderr=DEVNULL,stdout=DEVNULL)

def start_dashboard():
    call(["python3","dashboard.py"],stderr=DEVNULL,stdout=DEVNULL)
def start_main():
    call(["python3","main.py"])
if __name__ == '__main__':
    p = multiprocessing.Process(target=start_ethereum)
    p.start()
    time.sleep(2)
    print("Ethereum Started")
    p = multiprocessing.Process(target=start_ipfs)
    p.start()
    time.sleep(2)
    print("IPFS Started")
    p = multiprocessing.Process(target=start_dashboard)
    p.start()
    time.sleep(2)
    print("Dashboard Started")
    p = multiprocessing.Process(target=start_main)
    p.start()
    time.sleep(2)
    p.terminate()
    print("finish")
    p = multiprocessing.Process(target=start_main)
    p.start()
    time.sleep(2)
    p.terminate()
    print("finish")
    p = multiprocessing.Process(target=start_main)
    p.start()
    time.sleep(2)