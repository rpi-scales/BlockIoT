# BlockIoT

## Setup

### Requirements
1. IPFS(for hashing purposes only)
2. Ethereum Geth
3. Python 3.8

## Running

1. On one terminal, run "ipfs daemon"
2. On another, run "geth --dev --ipcpath ~/Library/Ethereum/geth.ipc"
3. To simulate some sample data, run "python3 -m http.server 8000" as a test server
4. Run "python3.8 [path_to_main.py]"
