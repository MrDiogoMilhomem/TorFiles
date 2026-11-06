from sys import argv
import secrets
import base64

SECRET_KEY = secrets.token_hex(32)
ENCRYPTION_KEY = base64.b64encode(secrets.token_bytes(32)).decode()

# nome do arquivo
if len(argv) > 1:
    nome_arquivo = argv[1]
else:
    nome_arquivo = ".env"

env = f"""# Configuração dos bancos de dados
MARIADB_URL=mysql://user:pass@host:3306/torfiles
POSTGRES_URL=postgresql://user:pass@host:5432/torfiles

# Chaves de criptografia do flask e dos arquivos
SECRET_KEY={SECRET_KEY}
ENCRYPTION_KEY={ENCRYPTION_KEY}

# Habilitar a documentação do app
DOCS_ENABLED=true

# Configurações do desenvolvimento local
LOCALDEV=true
LOCALDEV_DEBUG=true
LOCALDEV_HOST=127.0.0.1
LOCALDEV_PORT=5000
"""

with open(nome_arquivo, "w") as f:
    f.write(env)

print(f"Configurações salvas em {nome_arquivo}")