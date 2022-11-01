# Basic Python Blockchain

Loosely Following Daniel van Flymen's guide 
- https://medium.com/@vanflymen/learn-blockchains-by-building-one-117428612f46

API Query Options:

GET: /chain  
- Returns the full blockchain of current node  

GET: /nodes/resolve  
- Resolves any conflicts and makes sure current node's chain is accurate  

GET: /mine  
- Run Proof of Work algorithm and reward miner with 1 coin  
POST: /transactions/new  
- Adds a new transaction to the blockchain  
POST: /nodes/register  
- Accepts a list of nodes and adds them to the blockchain  
