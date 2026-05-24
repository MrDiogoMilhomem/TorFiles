# Banco de Dados

## Visao Geral

O sistema utiliza dois bancos de dados:
- **MariaDB**: Dados estruturados (usuarios, metadados)
- **PostgreSQL**: Dados binarios (arquivos criptografados)

## MariaDB

### Tabela: users

Armazena informacoes de usuarios.

```sql
CREATE DATABASE torfiles;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | INT | Identificador unico |
| username | VARCHAR(50) | Nome de usuario unico |
| password_hash | VARCHAR(255) | Hash Argon2 da senha |
| created_at | TIMESTAMP | Data de criacao |

### Tabela: files

Armazena metadados dos arquivos.

```sql
CREATE DATABASE torfiles;

USE torfiles;

CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code CHAR(5) UNIQUE NOT NULL,
    uuid CHAR(36) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    description TEXT,
    file_hash CHAR(64) NOT NULL,
    downloads_remaining INT NOT NULL,
    download_limit INT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    status ENUM('active', 'paused', 'expired') DEFAULT 'active',
    has_password BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | INT | Identificador unico |
| user_id | INT | Referencia ao usuario |
| code | CHAR(5) | Codigo de compartilhamento |
| uuid | CHAR(36) | UUID para busca no PostgreSQL |
| filename | VARCHAR(255) | Nome original do arquivo |
| description | TEXT | Descricao do arquivo |
| file_hash | CHAR(64) | Hash SHA-256 do arquivo |
| downloads_remaining | INT | Downloads restantes |
| download_limit | INT | Limite original de downloads |
| expires_at | TIMESTAMP | Data/hora de expiracao |
| status | ENUM | Estado: active, paused, expired |
| has_password | BOOLEAN | Se tem senha de download |
| password_hash | VARCHAR(255) | Hash da senha de download |
| created_at | TIMESTAMP | Data de criacao |

### Indices

```sql
CREATE INDEX idx_files_code ON files(code);
CREATE INDEX idx_files_user_status ON files(user_id, status);
CREATE INDEX idx_files_expires ON files(expires_at);
```

## PostgreSQL

### Tabela: file_blobs

Armazena arquivos criptografados.

```sql
CREATE DATABASE torfiles;

USE torfiles;

CREATE TABLE file_blobs (
    uuid UUID PRIMARY KEY,
    encrypted_data BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| uuid | UUID | Identificador unico (referencia files.uuid) |
| encrypted_data | BYTEA | Arquivo criptografado |
| created_at | TIMESTAMP | Data de criacao |

## Variaveis de Ambiente

```
MARIADB_URL=mysql://user:pass@host:3306/database
POSTGRES_URL=postgresql://user:pass@host:5432/database
```

## Relacionamentos

```
users (1) ----< (N) files
files (1) ----< (1) file_blobs
```

## Consideracoes

### Integridade Referencial

- `files.user_id` referencia `users.id` com CASCADE DELETE
- `file_blobs.uuid` deve ser removido manualmente ao apagar arquivo

### Limpeza

O worker de limpeza:
1. Atualiza status de arquivos expirados
2. Opcionalmente remove arquivos expirados ha muito tempo

### Backup

Recomenda-se backup regular de ambos os bancos:
- MariaDB: dump SQL
- PostgreSQL: pg_dump incluindo BLOBs
