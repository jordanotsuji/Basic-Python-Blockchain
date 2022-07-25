import hashlib
import json
from time import time
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
                'previous_hash':previous_hash or self.hash(self.chain[-1]),
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
