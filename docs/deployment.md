# Deployment

## Requisitos

- Python 3.9+
- MariaDB 10.5+
- PostgreSQL 13+
- Servidor com suporte a Python (Vercel, Heroku, VPS)

## Variaveis de Ambiente

```bash
MARIADB_URL=mysql://user:password@host:3306/torfiles
POSTGRES_URL=postgresql://user:password@host:5432/torfiles

SECRET_KEY=chave-secreta-longa-e-aleatoria
ENCRYPTION_KEY=chave-base64-32-bytes

# habilitar a documentaçao do app
DOCS_ENABLED=true

# Configuraçoes do desemvolvimento local
LOCALDEV=true
LOCALDEV_DEBUG=true
LOCALDEV_HOST='127.0.0.1'
LOCALDEV_PORT=5000
```

### Gerando Chaves

```python
import secrets
import base64

# SECRET_KEY
print(secrets.token_hex(32))

# ENCRYPTION_KEY
print(base64.b64encode(secrets.token_bytes(32)).decode())
```

## Deploy

### 1. Clonar Repositorio

```bash
git clone https://github.com/diogopython/TorFiles.git
cd TorFiles
```

### 2. Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Variaveis

```bash
MARIADB_URL=mysql://user:password@host:3306/torfiles
POSTGRES_URL=postgresql://user:password@host:5432/torfiles

SECRET_KEY=chave-secreta-longa-e-aleatoria
ENCRYPTION_KEY=chave-base64-32-bytes

# habilitar a documentaçao do app
DOCS_ENABLED=true

# Configuraçoes do desemvolvimento local
LOCALDEV=true
LOCALDEV_DEBUG=true
LOCALDEV_HOST='127.0.0.1'
LOCALDEV_PORT=5000
```

### 4. Executar

**Desenvolvimento:**
```bash
python app.py
```

**Produçao**
```bash
gunicorn -w <workers> -b 127.0.0.1:8000 app:app 
```

---

## Workers do Gunicorn

Os `workers` são processos separados do Gunicorn que executam sua aplicação Flask.

Mais workers permitem:
- atender mais usuários simultaneamente
- melhor uso da CPU
- maior estabilidade

Porém:
- cada worker consome RAM
- workers demais podem reduzir desempenho

---

## Regra recomendada

A fórmula mais comum é:

```text
(2 × núcleos da CPU) + 1
```

Exemplos:

| Núcleos/Threads | Workers recomendados |
|---|---|
| 2 | 5 |
| 4 | 9 |
| 6 | 13 |
| 8 | 17 |
| 16 | 33 |
(recomentaçao: nao rode em capacidade total de workers suportados pelo seu processador, para manter a estabilidade do sistema e outros processos importantes como os bancos de dados)
---

## Como descobrir quantos núcleos sua máquina possui

### Linux

```bash
nproc
```

ou:

```bash
lscpu
```

---

### Windows

No CMD:

```cmd
echo %NUMBER_OF_PROCESSORS%
```

ou no PowerShell:

```powershell
Get-CimInstance Win32_Processor | Select-Object NumberOfLogicalProcessors
```

---

### macOS

```bash
sysctl -n hw.ncpu
```

---

## Exemplo automático no Linux/macOS

```bash
gunicorn -w $((2 * $(nproc) + 1)) -b 127.0.0.1:8000 app:app
```
(nao recomendado pois usa todos os workers que sua cpu suporta)
---

## Exemplo simples

```bash
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```
(recomendado, funciona bem na maioria dos casos)

## Configuracao de Banco de Dados

### MariaDB

```sql
CREATE DATABASE TorFiles CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'TorFiles'@'%' IDENTIFIED BY 'senha';
GRANT ALL PRIVILEGES ON TorFiles.* TO 'TorFiles'@'%';
```

### PostgreSQL

```sql
CREATE DATABASE TorFiles;
CREATE USER TorFiles WITH PASSWORD 'senha';
GRANT ALL PRIVILEGES ON DATABASE TorFiles TO TorFiles;
```

As tabelas sao criadas automaticamente na primeira execucao.

## Proxy Reverso com Nginx

```nginx
server {
    listen 80;
    server_name TorFiles.example.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## SSL/HTTPS

### Certbot (Let's Encrypt)

```bash
certbot --nginx -d TorFiles.example.com
```

## Tor Hidden Service

### torrc

```
HiddenServiceDir /var/lib/tor/TorFiles/
HiddenServicePort 80 127.0.0.1:8000
```

### Obter Endereco .onion

```bash
cat /var/lib/tor/TorFiles/hostname
```

## Backup

### MariaDB

```bash
mysqldump -u user -p TorFiles > backup.sql
```

### PostgreSQL

```bash
pg_dump -U user TorFiles > backup.sql
```

### Restauracao

```bash
mysql -u user -p TorFiles < backup.sql
psql -U user TorFiles < backup.sql
```