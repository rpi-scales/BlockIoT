# BlockIoT

## Setup

### Requirements
* Install IPFS <= 0.6.0!

### Python environment setup

* `pip -m venv env`
* `source env/bin/activate`
* `pip install -r requirements.txt`

## Running

1. Make sure all of the given files are in one folder
2. Make sure your IPFS Daemon is up and running. 
3. Please run setup.py first (`python setup.py`). This may take a while, due to a lot of IPNS publishing involved. 

## How to use:

1. Make sure your IPFS Daemon is running. 

2. To run the program, please run the following flask functions:

### Windows instructions 

`set FLASK_APP=receive_data.py`

`set FLASK_ENV=development`

`flask run`

### Linux/MacOS instructions 

`export FLASK_APP=receive_data.py`

`export FLASK_ENV=development`

`flask run`

3. Open up an http client, preferably postman. 
To get sample api requests, please use the following link: https://www.getpostman.com/collections/0eb96ba71bd26c141884. 
Each request in the collection represents a specific functionality of the system. 
