# Blockchain.py
# Features:
#   Ability to add multiple nodes to the Blockchain
#   Proof of Work
#   Simple conflict resolution (two blocks solved at the same time)
#   Trasactions with RSA encryption

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []

    def new_block(self):
        # Creates a new block and ads it to the chain
        """
        Comment/long string but used as comments sometimes
        """
        pass

    def new_transaction(self, sender, recipient, amount):
        # Adds new transaction to the list of transactions 
        self.transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
            })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        #Hashes a block
        pass

    @property
    def last_block(self):
        # Returns the last block in the chain
        return self.chain[-1]
