import unittest
from blockchain import Blockchain

class TestBlockchain(unittest.TestCase):
    
    def setUp(self):
        """Tworzy nową instancję Blockchain przed każdym testem."""
        self.blockchain = Blockchain()
        self.blockchain.used_proofs = set() 
    
    def test_create_block(self):
        """Testuje, czy blok jest tworzony prawidłowo."""
        previous_block = self.blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        proof = self.blockchain.proof_of_work(previous_proof)
        previous_hash = self.blockchain.hash(previous_block)
        block = self.blockchain.create_block(proof, previous_hash)
        
        self.assertEqual(block['index'], 2)
        self.assertEqual(block['previous_hash'], previous_hash)
        self.assertEqual(len(self.blockchain.chain), 2)
    
    def test_add_transaction(self):
        """Testuje, czy transakcje są dodawane prawidłowo."""
        index = self.blockchain.add_transaction(sender="Alice", receiver="Bob", amount=10)
        
        self.assertEqual(index, 2)
        self.assertEqual(len(self.blockchain.transactions), 1)
        self.assertEqual(self.blockchain.transactions[0]['sender'], "Alice")
        self.assertEqual(self.blockchain.transactions[0]['receiver'], "Bob")
        self.assertEqual(self.blockchain.transactions[0]['amount'], 10)
    
    def test_proof_of_work(self):
        """Testuje algorytm dowodu pracy."""
        previous_block = self.blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        proof = self.blockchain.proof_of_work(previous_proof)
    
        # Sprawdź, czy dowód pracy jest liczbą całkowitą
        self.assertIsInstance(proof, int)
    
        # Dodaj dowód do zestawu użytych dowodów w testach
        self.blockchain.used_proofs.add(proof)
    
        # Sprawdź, czy dowód pracy jest teraz w zestawie użytych dowodów
        self.assertIn(proof, self.blockchain.used_proofs)


    
    def test_is_chain_valid(self):
        """Testuje, czy metoda sprawdzająca ważność łańcucha działa poprawnie."""
        # Dodaj kilka bloków do łańcucha
        for _ in range(2):
            previous_block = self.blockchain.get_previous_block()
            previous_proof = previous_block['proof']
            proof = self.blockchain.proof_of_work(previous_proof)
            previous_hash = self.blockchain.hash(previous_block)
            self.blockchain.create_block(proof, previous_hash)
        
        # Sprawdź, czy łańcuch jest ważny
        is_valid = self.blockchain.is_chain_valid(self.blockchain.chain)
        self.assertTrue(is_valid)
        
        # Manipulacja łańcuchem, aby sprawdzić, czy zostanie wykryta jako nieprawidłowa
        self.blockchain.chain[1]['proof'] = 12345  # Nieprawidłowy dowód pracy
        is_valid = self.blockchain.is_chain_valid(self.blockchain.chain)
        self.assertFalse(is_valid)

    def test_hash(self):
        """Testuje generowanie hashu dla bloku."""
        block = self.blockchain.get_previous_block()
        block_hash = self.blockchain.hash(block)
        
        self.assertIsInstance(block_hash, str)
        self.assertEqual(len(block_hash), 64)  # SHA256 hash ma długość 64 znaków

if __name__ == '__main__':
    unittest.main()


