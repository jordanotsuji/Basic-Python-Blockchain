import hashlib
import json
import requests
from time import time
from uuid import uuid4
from textwrap import dedent
from urllib.parse import urlparse
from flask import Flask, jsonify, request

# Blockchain.py
# Features:
#   Ability to add multiple nodes to the Blockchain
#   Proof of Work
#   Simple conflict resolution (two blocks solved at the same time)
#   Trasactions with RSA encryption

class Blockchain:
    """
    Blocks of transactional and/or other information that each depend on the last block's
    hash, making the entire history of the chain of blocks (blockchain) immutable.

    Tracks transactions, but can easily store other data if modified.
    """

    def __init__(self):
        self.chain = []         # Chain of previous blocks of data
        self.transactions = []  # Transactions of the current block being created
        # Create genesis block
        self.new_block(previous_hash = 1, proof = 100)
        self.nodes = set()      # Set containing neighboring nodes for validation  


    def new_block(self, proof, previous_hash=None):
        """
        Creates a new block and adds it to the chain

        :param proof: <int> The proof given by POW algorithm
        :param previous_hash: (Optional) <str> Hash of previous block
        :return: <dict> new Block
        """

        block = {
                'index':len(self.chain) + 1,
                'timestamp':time(),
                'transactions':self.transactions,
                'proof':proof,
                'previous_hash':previous_hash or self.hash(self.chain[-1])
                }

        # Clear list of current transactions and append new block to chain
        self.transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Adds new transaction to the list of transactions 
        """

        self.transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
            })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Returns the SHA-256 hash of a block
        """
        # Sort the keys of the block so jsons are consistant, and convert to json
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Returns the last block of the chain
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Simple proof of work algorithm
        - Find a number x such that hash("x(previous block's hash)") has 4 leading zeroes (0000)
        """

        proof = 0
        while self.valid_proof(proof, last_proof) is False:
            proof += 1

        return proof

    def valid_proof(self, proof, last_proof):
        """
        Returns true if hash(guess, last_proof) has 4 leading zeroes 
        """

        guessString = f'{last_proof}{proof}'.encode()
        # TODO: Possibly change this to hash()
        guessHash = hashlib.sha256(guessString).hexdigest()
        return guessHash[:4] == "0000"

    def register_node(self, address):
        """
        Accepts a new node as a URL and registers it into the blockchain
        Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        # "netloc" = netlocation, and returns the domain, port, and optional username/password
        self.nodes.add(parsed_url.netloc)        

    def valid_chain(self, chain):
        """
        Determines if a given blockchain is valid

        :param chain: <list> A blockchain
        :return: <bool> True if valid, False otherwise
        """

        last_block = chain[0]
        current_index = 1
        # Loop from first node in chain the last validating proofs for each pair of neighbors 
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}') 
            print(f'{block}')
            print("\n----------------\n")
            # Make sure that this block's last_proof = last block's proof
            # & Make sure that this block's proof and last_proof are valid together
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(block['proof'], last_block['proof']):
                return False

            last_block = block
            current_index += 1
        
        # Return true if loop finds everything valid
        return True 

    def resolve_conflicts(self):
        """
        Use Consensus Algorithm to resolve conflicts on the blockchain
        For this blockchain, the longest valid chain is the authority

        :return: <bool> True if this blockchain's chain was replaced, False if otherwise
        """
         
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                tempNodeLength = response.json()['length']
                tempChain = response.json()['chain']
                if tempNodeLength > max_length and self.valid_chain(tempChain):
                    new_chain = tempChain
                    max_length = tempNodeLength
        # If there was a longer chain, replace the current chain and return True        
        if new_chain:
            self.chain = new_chain
            return True
        # Return false if chain wasn't replaced 
        return False
         

# Blockchain class definition end

# Instantiate node
app = Flask(__name__)

# Generate uuid for this node (universally unique id protocol not based on central authority)
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = Blockchain()

# API definition

# Mining Endpoint
#   - Calculate POW
#   - Reward miner for work (1 unit)
#   - Forge new block by adding to the chain
@app.route('/mine', methods=['GET'])
def mine():
    # Run POW algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # If proof_of_work completes, reward user with 1 coin
    blockchain.new_transaction("0", node_identifier, 1)
     
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
            'message':"New Block Forged",
            'index':block['index'],
            'transactions':block['transactions'],
            'proof':block['proof'],
            'previous_hash':block['previous_hash']
            }
    return jsonify(response), 200

# Example Transaction:
# {
#  "sender": "my address",
#  "recipient": "someone else's address",
#  "amount": 5
# }
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Handles POST requests with new transactions for the blockchain
    """  
    # Get response body as json 
    values = request.json
    if values is None:
        return "Invalid Body", 400
    # Check to see that all fields are in the reqeust
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Required Field(s)', 400
    
    # Add new transaction to the blockchain
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = { 'message':f'Adding transaction to block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
            'chain':blockchain.chain,
            'length':len(blockchain.chain)
            }
    return jsonify(response), 200 

# Start server on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
