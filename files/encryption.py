"""
CryptFyles Hybrid Encryption System
RSA-2048 + AES-256-GCM for secure file storage
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import os
import base64


class HybridEncryption:
    """
    Complete RSA-AES hybrid encryption system
    
    Flow:
    1. Generate random AES-256 key
    2. Encrypt file with AES-256-GCM (fast for large files)
    3. Encrypt AES key with RSA-2048 (secure key distribution)
    4. Store encrypted file + encrypted AES key + nonce + tag
    """
    
    @staticmethod
    def generate_rsa_key_pair():
        """
        Generate RSA-2048 key pair
        
        Returns:
            tuple: (private_key_pem, public_key_pem) as bytes
        """
        # Generate RSA-2048 private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get public key from private key
        public_key = private_key.public_key()
        
        # Serialize private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key to PEM format
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def generate_aes_key():
        """
        Generate random AES-256 key (32 bytes)
        
        Returns:
            bytes: 32-byte AES key
        """
        return os.urandom(32)
    
    @staticmethod
    def encrypt_file_aes(file_data, aes_key):
        """
        Encrypt file data with AES-256-GCM
        
        Args:
            file_data (bytes): File content to encrypt
            aes_key (bytes): 32-byte AES key
            
        Returns:
            dict: {
                'ciphertext': encrypted data,
                'nonce': 12-byte nonce,
                'tag': 16-byte authentication tag
            }
        """
        # Generate random nonce (12 bytes for GCM)
        nonce = os.urandom(12)
        
        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt the file
        ciphertext = encryptor.update(file_data) + encryptor.finalize()
        
        # Get authentication tag
        tag = encryptor.tag
        
        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'tag': tag
        }
    
    @staticmethod
    def decrypt_file_aes(ciphertext, aes_key, nonce, tag):
        """
        Decrypt file data with AES-256-GCM
        
        Args:
            ciphertext (bytes): Encrypted file data
            aes_key (bytes): 32-byte AES key
            nonce (bytes): 12-byte nonce
            tag (bytes): 16-byte authentication tag
            
        Returns:
            bytes: Decrypted file data
            
        Raises:
            Exception: If authentication fails (file was tampered with)
        """
        # Create AES-GCM cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the file
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    @staticmethod
    def encrypt_aes_key_with_rsa(aes_key, public_key_pem):
        """
        Encrypt AES key with RSA public key
        
        Args:
            aes_key (bytes): 32-byte AES key
            public_key_pem (bytes): RSA public key in PEM format
            
        Returns:
            bytes: Encrypted AES key (256 bytes for RSA-2048)
        """
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        # Encrypt AES key with RSA-OAEP
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_aes_key
    
    @staticmethod
    def decrypt_aes_key_with_rsa(encrypted_aes_key, private_key_pem):
        """
        Decrypt AES key with RSA private key
        
        Args:
            encrypted_aes_key (bytes): Encrypted AES key
            private_key_pem (bytes): RSA private key in PEM format
            
        Returns:
            bytes: Decrypted AES key (32 bytes)
        """
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Decrypt AES key with RSA-OAEP
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return aes_key
    
    @staticmethod
    def encrypt_file_hybrid(file_data, public_key_pem):
        """
        Encrypt file using hybrid encryption (AES + RSA)
        
        Process:
        1. Generate random AES key
        2. Encrypt file with AES-GCM
        3. Encrypt AES key with RSA
        
        Args:
            file_data (bytes): File content to encrypt
            public_key_pem (bytes): RSA public key
            
        Returns:
            dict: {
                'ciphertext': encrypted file,
                'encrypted_aes_key': encrypted AES key,
                'nonce': nonce,
                'tag': authentication tag
            }
        """
        # Generate random AES key
        aes_key = HybridEncryption.generate_aes_key()
        
        # Encrypt file with AES
        encrypted_data = HybridEncryption.encrypt_file_aes(file_data, aes_key)
        
        # Encrypt AES key with RSA
        encrypted_aes_key = HybridEncryption.encrypt_aes_key_with_rsa(
            aes_key, public_key_pem
        )
        
        return {
            'ciphertext': encrypted_data['ciphertext'],
            'encrypted_aes_key': encrypted_aes_key,
            'nonce': encrypted_data['nonce'],
            'tag': encrypted_data['tag']
        }
    
    @staticmethod
    def decrypt_file_hybrid(ciphertext, encrypted_aes_key, nonce, tag, private_key_pem):
        """
        Decrypt file using hybrid encryption (RSA + AES)
        
        Process:
        1. Decrypt AES key with RSA
        2. Decrypt file with AES-GCM
        
        Args:
            ciphertext (bytes): Encrypted file
            encrypted_aes_key (bytes): Encrypted AES key
            nonce (bytes): Nonce
            tag (bytes): Authentication tag
            private_key_pem (bytes): RSA private key
            
        Returns:
            bytes: Decrypted file data
        """
        # Decrypt AES key with RSA
        aes_key = HybridEncryption.decrypt_aes_key_with_rsa(
            encrypted_aes_key, private_key_pem
        )
        
        # Decrypt file with AES
        plaintext = HybridEncryption.decrypt_file_aes(
            ciphertext, aes_key, nonce, tag
        )
        
        return plaintext


# Helper functions for database storage
def encode_for_db(data):
    """Convert bytes to base64 string for database storage"""
    return base64.b64encode(data).decode('utf-8')


def decode_from_db(data_str):
    """Convert base64 string back to bytes"""
    return base64.b64decode(data_str.encode('utf-8'))
