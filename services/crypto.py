"""
Serviço de criptografia.
Implementa criptografia AES-256 usando Fernet e derivação de chave com Argon2/PBKDF2.
"""
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from config import Config


class CryptoService:
    """Serviço para criptografia de arquivos e hash de senhas."""
    
    def __init__(self):
        self.password_hasher = PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16
        )
        self._master_key = Config.ENCRYPTION_KEY
    
    def hash_password(self, password):
        """Gera hash Argon2 de uma senha."""
        return self.password_hasher.hash(password)
    
    def verify_password(self, password_hash, password):
        """Verifica se uma senha corresponde ao hash."""
        try:
            self.password_hasher.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False
    
    def hash_file(self, file_data):
        """Gera hash SHA-256 de um arquivo."""
        return hashlib.sha256(file_data).hexdigest()
    
    def _derive_key(self, password=None, salt=None):
        """Deriva uma chave AES-256 a partir de uma senha ou usa a chave mestra."""
        if password:
            # Derivar chave da senha do usuário usando PBKDF2
            if salt is None:
                salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key, salt
        else:
            # Usar chave mestra do sistema
            key = base64.urlsafe_b64encode(self._master_key)
            return key, None
    
    def encrypt_file(self, file_data, password=None):
        """
        Criptografa dados de arquivo com AES-256.
        
        Se uma senha for fornecida, deriva a chave da senha.
        Caso contrário, usa a chave mestra do sistema.
        
        Retorna: (dados_criptografados, salt) - salt é None se sem senha
        """
        key, salt = self._derive_key(password)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(file_data)
        
        if salt:
            # Prepend salt aos dados criptografados para armazenamento
            return salt + encrypted_data, True
        else:
            return encrypted_data, False
    
    def decrypt_file(self, encrypted_data, password=None, has_password=False):
        # Normalização de tipos de entrada para compatibilidade com diferentes drivers de banco
        # Alguns drivers podem retornar memoryview, bytearray ou string em vez de bytes
        if isinstance(encrypted_data, memoryview):
            encrypted_data = encrypted_data.tobytes()
        elif isinstance(encrypted_data, bytearray):
            encrypted_data = bytes(encrypted_data)
        elif isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()

        if has_password and password:
            salt = encrypted_data[:16]
            encrypted_data = encrypted_data[16:]
            key, _ = self._derive_key(password, salt)
        else:
            key, _ = self._derive_key()
        
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)


# Instância global
crypto = CryptoService()
