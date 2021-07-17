import json
from solc import compile_standard # type: ignore
from web3 import Web3
from web3 import EthereumTesterProvider
from web3.auto.gethdev import w3

def deploy(name):
    with open(r"contract_data.json","r") as infile:
        contract_data = json.load(infile)
    file1 = open("Published/" + name + ".sol","r")
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {
            name + ".sol": {
                "content": file1.read()
            }
        },
        "settings":
            {
                "outputSelection": {
                    "*": {
                        "*": [
                            "metadata", "evm.bytecode"
                            , "evm.bytecode.sourceMap"
                        ]
                    }
                }
            }
    })
    # w3 = Web3(EthereumTesterProvider())
    # # set pre-funded account as sender
    w3.eth.default_account = w3.eth.accounts[0]
    # Instantiate and deploy contract
    bytecode = compiled_sol["contracts"][name + '.sol'][name]['evm']['bytecode']['object']
    abi = json.loads(compiled_sol["contracts"][name + '.sol'][name]['metadata'])['output']['abi']
    # Submit the transaction that deploys the contract
    Greeter = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = Greeter.constructor().transact()
    # Wait for the transaction to be mined, and get the transaction receipt
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    # Create the contract instance with the newly-deployed address
    greeter = w3.eth.contract(address=tx_receipt.contractAddress,abi=abi)
    contract_data[name] = [abi,bytecode,tx_receipt.contractAddress]
    file1.close()
    with open(r"contract_data.json","w") as outfile:
        json.dump(contract_data, outfile)

def deploy_templates(template_name):
    deploy(template_name)