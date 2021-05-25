# BlockIoT

## Setup

### Requirements
1. IPFS(for hashing purposes only)
2. Ethereum Geth
3. Python 3.8

## Running

1. On one terminal, run "ipfs daemon"
2. On another, run "geth --dev --ipcpath ~/Library/Ethereum/geth.ipc"
3. To simulate some sample data, run "python3 -m http.server 8000" as a test server in another terminal
4. Run "python3.8 [path_to_main.py]"

## Notes when Running

1. You may expect an error the first 1-2 times you run the code. This is simply coming from the ethereum chain. It should resolve itself when you run it again.

## Important Highlights to Look At

1. The "control" file is main.py. Here, you can see a couple of things: the configuration file, and the basic control functions. Registration creates register.sol and registers the patient. Deploy deploys smart contracts. The Oracle is the main loop that facilitates all commands coming from the smart contracts. 
2. Time limits are set to the amount of times you can request patient graphs as well as the the amount of alerts a physician can get. Physicians can request charts once an hour, and alerts are only sent once a week. 
3. Compliance for the last 7 days(rather than 30) are calculated when sending alerts, to prevent overlaps w/ compliance every week. 
4. The information you see in the terminal after running it is simply all events that are sent into the oracle. This helps track actions done by the program. 
5. Sending SMSes involves using your email address, and password to set it up. Obviously, I didn't want to send over my personal Gmail password, but please feel free to test it yourself by adding in your gmail user/pass, your phone number, and carrier. 
