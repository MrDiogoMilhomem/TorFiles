"""
Configuração do aplicativo Flask.
Gerencia variáveis de ambiente e configurações de segurança.
"""
import os
import secrets
from base64 import b64decode, b64encode
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração principal do aplicativo."""
    
    # Chave secreta para sessões Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Configuração de sessão
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Tor .onion não usa HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas
    
    # Banco de dados MariaDB (usuários e metadados)
    MARIADB_URL = os.environ.get('MARIADB_URL', '')
    
    # Banco de dados PostgreSQL (arquivos criptografados)
    POSTGRES_URL = os.environ.get('POSTGRES_URL', '')
    
    # Chave de criptografia AES-256
    # Deve ser fornecida via variável de ambiente em produção
    _encryption_key = os.environ.get('ENCRYPTION_KEY')
    if not _encryption_key:
        raise ValueError("ENCRYPTION_KEY environment variable must be set for production use")
    ENCRYPTION_KEY = b64decode(_encryption_key)
    
    # Limites de upload
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'zip', 'rar', '7z'}
    
    # Limites de usuário
    MAX_ACTIVE_FILES = 3
    
    # Rate limiting
    RATE_LIMIT_ATTEMPTS = 5  # Máximo de tentativas
    RATE_LIMIT_WINDOW = 300  # Janela de tempo em segundos (5 minutos)
    
    # Worker de limpeza
    CLEANUP_INTERVAL = 60  # Intervalo em segundos

    @classmethod
    def get_mariadb_config(cls):
        """Extrai configurações do MariaDB a partir da URL."""
        url = cls.MARIADB_URL
        if not url:
            return None
        
        # Formato: mysql://user:pass@host:port/database
        try:
            # Remove o prefixo mysql://
            url = url.replace('mysql://', '').replace('mariadb://', '')
            
            # Separa credenciais do host
            if '@' in url:
                credentials, host_part = url.rsplit('@', 1)
                user, password = credentials.split(':', 1)
            else:
                user, password = '', ''
                host_part = url
            
            # Separa host/porta do database
            if '/' in host_part:
                host_port, database = host_part.rsplit('/', 1)
            else:
                host_port = host_part
                database = ''
            
            # Separa host da porta
            if ':' in host_port:
                host, port = host_port.rsplit(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 3306
            
            # Remove query string do database se houver
            if '?' in database:
                database = database.split('?')[0]
            
            return {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'database': database,
                'charset': 'utf8mb4'
            }
        except Exception as e:
            print(f"Erro ao parsear MARIADB_URL: {e}")
            return None

    @classmethod
    def get_postgres_config(cls):
        """Retorna a URL do PostgreSQL."""
        return cls.POSTGRES_URL
