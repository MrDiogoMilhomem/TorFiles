"""
Modelo de arquivo para operações no MariaDB e PostgreSQL.
"""
import uuid as uuid_lib
from datetime import datetime, timedelta
from services.database import mariadb, postgres
from services.crypto import crypto
from services.code_generator import code_generator


class File:
    """Modelo de arquivo."""
    
    def __init__(self, id=None, user_id=None, code=None, uuid=None, filename=None,
                 description=None, file_hash=None, downloads_remaining=None,
                 download_limit=None, expires_at=None, status='active',
                 has_password=False, password_hash=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.code = code
        self.uuid = uuid
        self.filename = filename
        self.description = description
        self.file_hash = file_hash
        self.downloads_remaining = downloads_remaining
        self.download_limit = download_limit
        self.expires_at = expires_at
        self.status = status
        self.has_password = has_password
        self.password_hash = password_hash
        self.created_at = created_at
    
    @classmethod
    def from_dict(cls, data):
        """Cria um File a partir de um dicionário."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            code=data.get('code'),
            uuid=data.get('uuid'),
            filename=data.get('filename'),
            description=data.get('description'),
            file_hash=data.get('file_hash'),
            downloads_remaining=data.get('downloads_remaining'),
            download_limit=data.get('download_limit'),
            expires_at=data.get('expires_at'),
            status=data.get('status'),
            has_password=data.get('has_password'),
            password_hash=data.get('password_hash'),
            created_at=data.get('created_at')
        )
    
    @classmethod
    def find_by_code(cls, code):
        """Busca arquivo por código de 5 dígitos."""
        result = mariadb.execute(
            "SELECT * FROM files WHERE code = %s",
            (code.upper(),),
            fetchone=True
        )
        return cls.from_dict(result)
    
    @classmethod
    def find_by_uuid(cls, uuid):
        """Busca arquivo por UUID."""
        result = mariadb.execute(
            "SELECT * FROM files WHERE uuid = %s",
            (uuid,),
            fetchone=True
        )
        return cls.from_dict(result)
    
    @classmethod
    def find_by_user(cls, user_id, status=None):
        """Busca todos os arquivos de um usuário."""
        if status:
            result = mariadb.execute(
                "SELECT * FROM files WHERE user_id = %s AND status = %s ORDER BY created_at DESC",
                (user_id, status),
                fetch=True
            )
        else:
            result = mariadb.execute(
                "SELECT * FROM files WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
                fetch=True
            )
        return [cls.from_dict(row) for row in result]
    
    @classmethod
    def count_active_by_user(cls, user_id):
        """Conta arquivos ativos de um usuário."""
        result = mariadb.execute(
            "SELECT COUNT(*) as count FROM files WHERE user_id = %s AND status = 'active'",
            (user_id,),
            fetchone=True
        )
        return result['count'] if result else 0
    
    @classmethod
    def create(cls, user_id, filename, file_data, description=None,
               password=None, download_limit=10, expires_hours=24):
        """
        Cria um novo arquivo.
        
        Args:
            user_id: ID do usuário
            filename: Nome do arquivo original
            file_data: Dados binários do arquivo
            description: Descrição opcional
            password: Senha opcional para download
            download_limit: Limite de downloads
            expires_hours: Horas até expiração
        """
        # Gerar código e UUID
        code = code_generator.generate()
        file_uuid = str(uuid_lib.uuid4())
        
        # Hash do arquivo original
        file_hash = crypto.hash_file(file_data)
        
        # Criptografar arquivo
        encrypted_data, has_password = crypto.encrypt_file(file_data, password)
        
        # Hash da senha se fornecida
        password_hash = None
        if password:
            password_hash = crypto.hash_password(password)
        
        # Calcular expiração
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        # Salvar dados criptografados no PostgreSQL
        postgres.save_blob(file_uuid, encrypted_data)
        
        # Salvar metadados no MariaDB
        file_id = mariadb.execute(
            """
            INSERT INTO files (user_id, code, uuid, filename, description, file_hash,
                             downloads_remaining, download_limit, expires_at, status,
                             has_password, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, code, file_uuid, filename, description, file_hash,
             download_limit, download_limit, expires_at, 'active',
             has_password, password_hash)
        )
        
        return cls(
            id=file_id, user_id=user_id, code=code, uuid=file_uuid,
            filename=filename, description=description, file_hash=file_hash,
            downloads_remaining=download_limit, download_limit=download_limit,
            expires_at=expires_at, status='active', has_password=has_password,
            password_hash=password_hash
        )
    
    def get_encrypted_data(self):
        """Recupera dados criptografados do PostgreSQL."""
        return postgres.get_blob(self.uuid)
    
    def decrypt(self, password=None):
        """Descriptografa e retorna os dados do arquivo."""
        encrypted_data = self.get_encrypted_data()
        if not encrypted_data:
            return None
        return crypto.decrypt_file(encrypted_data, password, self.has_password)
    
    def verify_download_password(self, password):
        """Verifica a senha de download."""
        if not self.has_password:
            return True
        if not password:
            return False
        return crypto.verify_password(self.password_hash, password)
    
    def jls_extract_def(self):
        return """
        UPDATE files SET downloads_remaining = %s WHERE id = %s
        """

    def decrement_downloads(self):
        """Decrementa o contador de downloads de forma atômica."""
        # Atualiza o contador e verifica se chegou a zero em uma operação única
        self.downloads_remaining = self.downloads_remaining - 1
        result = mariadb.execute(
            self.jls_extract_def(),
            (self.downloads_remaining, self.id,)
        )
        
        # Atualiza o objeto local com o novo valor
        if result:
            self.downloads_remaining = result['new_count']
    
    def update_status(self, status):
        """Atualiza o status do arquivo."""
        self.status = status
        mariadb.execute(
            "UPDATE files SET status = %s WHERE id = %s",
            (status, self.id)
        )
    
    def delete(self):
        """Remove o arquivo completamente."""
        # Remover do PostgreSQL
        postgres.delete_blob(self.uuid)
        
        # Remover do MariaDB
        mariadb.execute("DELETE FROM files WHERE id = %s", (self.id,))
    
    def is_expired(self):
        """Verifica se o arquivo está expirado."""
        if self.status == 'expired':
            return True
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        if self.downloads_remaining <= 0:
            return True
        return False
    
    def is_downloadable(self):
        """Verifica se o arquivo pode ser baixado."""
        if self.status != 'active':
            return False
        if self.is_expired():
            return False
        return True
    
    def time_remaining(self):
        """Retorna o tempo restante até expiração."""
        if not self.expires_at:
            return None
        remaining = self.expires_at - datetime.now()
        if remaining.total_seconds() < 0:
            return timedelta(0)
        return remaining
    
    def to_dict(self, include_sensitive=False):
        """Converte para dicionário."""
        data = {
            'id': self.id,
            'code': self.code,
            'filename': self.filename,
            'description': self.description,
            'file_hash': self.file_hash,
            'downloads_remaining': self.downloads_remaining,
            'download_limit': self.download_limit,
            'expires_at': str(self.expires_at) if self.expires_at else None,
            'status': self.status,
            'has_password': self.has_password,
            'created_at': str(self.created_at) if self.created_at else None
        }
        
        if include_sensitive:
            data['uuid'] = self.uuid
            data['user_id'] = self.user_id
        
        return data