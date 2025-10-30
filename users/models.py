"""
CustomUser Model with RSA Encryption Keys
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import os


class CustomUser(AbstractUser):
    """
    Extended User model with RSA encryption keys
    
    Fields from AbstractUser:
    - username (unique)
    - email
    - password (auto-hashed by Django)
    - first_name, last_name
    - is_staff, is_active, is_superuser
    - date_joined, last_login
    
    New Fields:
    - encrypted_private_key: RSA private key encrypted with user's password
    - public_key: RSA public key (PEM format)
    """
    
    # Make email unique and required
    email = models.EmailField(
        unique=True,
        help_text='User email address (must be unique)'
    )
    
    # RSA Keys (stored as text)
    encrypted_private_key = models.TextField(
        blank=True,
        null=True,
        help_text='RSA private key encrypted with user password'
    )
    
    public_key = models.TextField(
        blank=True,
        null=True,
        help_text='RSA public key in PEM format'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def has_rsa_keys(self):
        """Check if user has RSA keys generated"""
        return bool(self.public_key and self.encrypted_private_key)
    
    def generate_rsa_keys(self, password):
        """
        Generate RSA-2048 key pair and encrypt private key with password
        
        Args:
            password (str): User's password to encrypt private key
        """
        # Generate RSA-2048 key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Encrypt private key with user's password
        encrypted_private = self._encrypt_private_key(private_pem, password)
        
        # Store in database
        self.encrypted_private_key = encrypted_private
        self.public_key = public_pem.decode('utf-8')
        self.save()
    
    def _encrypt_private_key(self, private_key_bytes, password):
        """
        Encrypt private key using password-derived key (PBKDF2)
        
        Args:
            private_key_bytes: RSA private key as bytes
            password: User's password
            
        Returns:
            Encrypted private key as base64 string
        """
        # Generate salt
        salt = os.urandom(16)
        
        # Derive encryption key from password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Encrypt private key
        f = Fernet(key)
        encrypted = f.encrypt(private_key_bytes)
        
        # Combine salt + encrypted key for storage
        combined = base64.b64encode(salt + encrypted).decode('utf-8')
        return combined
    
    def decrypt_private_key(self, password):
        """
        Decrypt private key using user's password
        
        Args:
            password: User's password
            
        Returns:
            Decrypted private key as bytes, or None if failed
        """
        if not self.encrypted_private_key:
            return None
        
        try:
            # Decode from base64
            combined = base64.b64decode(self.encrypted_private_key.encode('utf-8'))
            
            # Extract salt and encrypted key
            salt = combined[:16]
            encrypted = combined[16:]
            
            # Derive decryption key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt private key
            f = Fernet(key)
            private_key_bytes = f.decrypt(encrypted)
            
            return private_key_bytes
        except Exception as e:
            print(f"Failed to decrypt private key: {e}")
            return None
    
    def get_public_key_bytes(self):
        """Get public key as bytes"""
        if self.public_key:
            return self.public_key.encode('utf-8')
        return None
