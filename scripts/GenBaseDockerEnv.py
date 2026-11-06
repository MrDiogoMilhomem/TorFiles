from sys import argv
import secrets
import base64
import string

SECRET_KEY = secrets.token_hex(32)
ENCRYPTION_KEY = base64.b64encode(secrets.token_bytes(32)).decode()

def GenKey():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@$%&*-_") for _ in range(20))

# nome do arquivo
if len(argv) > 1:
    nome_arquivo = argv[1]
else:
    nome_arquivo = ".env"

env = f"""# Configuração dos bancos de dados
# Segurança
SECRET_KEY={SECRET_KEY}
ENCRYPTION_KEY={ENCRYPTION_KEY}

# Senhas dos bancos
MARIADB_ROOT_PASSWORD={GenKey()}
MARIADB_PASSWORD={GenKey()}
POSTGRES_PASSWORD={GenKey()}

# Opcional
DOCS_ENABLED=true
"""

with open(nome_arquivo, "w") as f:
    f.write(env)

print(f"Configurações salvas em {nome_arquivo}")
