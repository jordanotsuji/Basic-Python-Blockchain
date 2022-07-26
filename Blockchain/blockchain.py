import hashlib
import json
from time import time
from uuid import uuid4
from textwrap import dedent

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
        self.chain = [] # Chain of previous blocks of data
        self.transactions = [] # Transactions of the current block being created
        # Create genesis block
        self.new_block(previous_hash = 1, proof = 100)

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

    def valid_proof(self, guess, last_proof):
        """
        Returns true if hash(guess, last_proof) has 4 leading zeroes 
        """

        guessString = f'{last_proof}{guess}'.encode()
        guessHash = hashlib.sha256(guessString).hexdigest()
        return guessHash[:4] == "0000"

# Blockchain class definition end

# Instantiate node
app = Flask(__name__)

# Generate uuid for this node (universally unique id protocol not based on central authority)
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = Blockchain()

# API definition
@app.route('/mine', methods=['GET'])
def mine():
    return "Mining a new block"

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
    
    values = request.json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Required Field(s)', 400

    return "Adding new transaction"

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
