
import datetime  # Biblioteka do pracy z datÄ… i czasem
import hashlib   # Biblioteka do hashowania bloku
import json      # Biblioteka do konwersji obiektÃ³w Python do formatu JSON
from flask import Flask, jsonify, request  # Flask dla aplikacji webowej i obsÅ‚ugi Å¼Ä…daÅ„

# Klasa Blockchain
class Blockchain:
    
    #inicjalizujemhy obiket klasy
    def __init__(self):
        self.chain = []  # Lista przechowujÄ…ca wszystkie bloki w Å‚aÅ„cuchu
        self.transactions = []  # Lista przechowujÄ…ca transakcje
        self.create_block(proof=1, previous_hash='0')  # Tworzymy blok genesis (pierwszy blok)
        self.used_proofs = set()  # Zestaw do przechowywania juÅ¼ uÅ¼ytych dowodÃ³w pracy
        
    def create_block(self, proof, previous_hash):
        
        #Tworzy nowy blok i dodaje go do Å‚aÅ„cucha.
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),  # Sygnatura czasowa bloku
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        
        self.transactions = []  # Resetujemy listÄ™ transakcji
        self.chain.append(block)  # Dodajemy blok do Å‚aÅ„cucha
        return block
    
    def add_transaction(self, sender, receiver, amount):
        
        #Dodaje nowÄ… transakcjÄ™ do listy transakcji.
        
        
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        return self.get_previous_block()['index'] + 1
    
    def get_previous_block(self):
        
        #Zwraca ostatni blok w Å‚aÅ„cuchu.
        #return: Ostatni blok
        
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        """
        Algorytm Proof of Work - znajdowanie nowego dowodu pracy.
        :param previous_proof: Dowód pracy poprzedniego bloku
        :return: Nowy dowód pracy
        """
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(f"{new_proof**2 - previous_proof**2}".encode()).hexdigest()
            if hash_operation[:4] == '0000':  # Można zwiększyć liczbę zer dla większej trudności
                if new_proof not in self.used_proofs:
                    check_proof = True
                else:
                    new_proof += 1
            else:
                new_proof += 1
        return new_proof
             
    def hash(self, block):
        
        #Zwraca hash bloku.
        
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        
       # Sprawdza, czy Å‚aÅ„cuch blokÃ³w jest prawidÅ‚owy.
         
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block 
            block_index += 1
        return True

# Aplikacja webowa
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Odpowiedzi JSON nie bÄ™dÄ… formatowane z dodatkowÄ… biaÅ‚Ä… przestrzeniÄ…

# Inicjalizacja blockchain
blockchain = Blockchain()

@app.route("/mine_block", methods=['GET'])
def mine_block():
    
    #Route do wydobywania nowego bloku.
    #return: OdpowiedÅº z informacjami o nowo wydobytym bloku
    
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    blockchain.used_proofs.add(proof)  # Dodaj dowód do zestawu użytych dowodów
    response = {
        'message': 'CONGRATULATIONS! New block mined.',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
        
    }
    return jsonify(response), 200

@app.route("/get_chain", methods=['GET'])
def get_chain():
    
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    
    if not all(key in json for key in transaction_keys):
        return jsonify({'error': 'Some elements of the transaction are missing'}), 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {
        'message': f'Transaction will be added to Block {index}'
    }
    return jsonify(response), 201

@app.route("/is_valid", methods=['GET'])
def is_valid():
    
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The blockchain is valid.'}
    else:
        response = {'message': 'The blockchain is invalid.'}
    return jsonify(response), 200

@app.errorhandler(404)
def not_found(error):
    
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    
    return jsonify({'error': 'Server error'}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
