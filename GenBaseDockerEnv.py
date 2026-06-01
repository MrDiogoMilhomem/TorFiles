from sys import argv
import secrets
import base64

SECRET_KEY = secrets.token_hex(32)
ENCRYPTION_KEY = base64.b64encode(secrets.token_bytes(32)).decode()

# nome do arquivo
if len(argv) > 1:
    nome_arquivo = argv[1]
else:
    nome_arquivo = ".env.example"

env = f"""# Configuração dos bancos de dados
# Segurança
SECRET_KEY={SECRET_KEY}
ENCRYPTION_KEY={ENCRYPTION_KEY}

# Senhas dos bancos (escolha senhas fortes)
MARIADB_ROOT_PASSWORD=senha-root-forte
MARIADB_PASSWORD=senha-torfiles-forte
POSTGRES_PASSWORD=senha-torfiles-forte

# Opcional
DOCS_ENABLED=true
"""

with open(nome_arquivo, "w") as f:
    f.write(env)

print(f"Configurações salvas em {nome_arquivo}")