# Seguranca

## Criptografia de Arquivos

### AES-256 via Fernet

Todos os arquivos sao criptografados antes do armazenamento usando Fernet, que implementa AES-256-CBC com autenticacao HMAC.

```python
from cryptography.fernet import Fernet

# Criptografar
fernet = Fernet(key)
encrypted = fernet.encrypt(data)

# Descriptografar
decrypted = fernet.decrypt(encrypted)
```

### Derivacao de Chave

**Sem senha de download:**
- Usa chave mestra do sistema (ENCRYPTION_KEY presente no .env)

**Com senha de download:**
- Deriva chave usando PBKDF2-HMAC-SHA256
- 480.000 iteracoes
- Salt aleatorio de 16 bytes
- Salt armazenado junto aos dados criptografados

## Hash de Senhas

### Argon2

Algoritmo vencedor do Password Hashing Competition, resistente a ataques de GPU e ASIC.

Parametros utilizados:
- time_cost: 3 iteracoes
- memory_cost: 64 MB
- parallelism: 4 threads
- hash_len: 32 bytes
- salt_len: 16 bytes

```python
from argon2 import PasswordHasher

ph = PasswordHasher()
hash = ph.hash(password)
ph.verify(hash, password)
```

## Hash de Arquivos

### SHA-256

Cada arquivo tem seu hash SHA-256 calculado no upload e exibido no download para verificacao de integridade.

```python
import hashlib

hash = hashlib.sha256(file_data).hexdigest()
```

## Sessoes

### Cookies Seguros

- **HTTPOnly**: Inacessivel via JavaScript
- **SameSite=Lax**: Protecao contra CSRF
- **Secure**: Apenas HTTPS (desabilitado para Tor .onion)

### Flask Sessions

- Assinadas com SECRET_KEY
- Expiracao de 24 horas

## Rate Limiting

### Protecao Anti Brute-Force

- 5 tentativas por 5 minutos
- Baseado em IP (considera X-Forwarded-For)
- Aplicado em:
  - Login
  - Registro
  - Acesso por codigo
  - Tentativas de senha

## Validacao de Input

### Sanitizacao

- Caracteres de controle removidos
- HTML escapado (< > & " ')
- Tamanho maximo validado

### Validacoes Especificas

- Username: 3-50 chars, alfanumerico + underscore
- Senha: 8+ chars, letras + numeros
- Arquivo: extensao e tamanho
- Codigo: 5 caracteres alfanumericos

## Protecao de Uploads

### Validacao de Tipo

- Verifica extensao (.zip, .rar, .7z)
- Tamanho maximo: 100MB

### Processamento Seguro

- Arquivo nunca executado
- Criptografado imediatamente
- Armazenado como BLOB binario

## Logs Minimos

Para maximizar privacidade:
- Sem logs de IP
- Sem logs de conteudo
- Apenas erros tecnicos registrados

## Compatibilidade Tor

- Funciona sem JavaScript (funcionalidades basicas)
- Cookies funcionam em .onion
- Sem recursos externos (CDN, fonts)
- Rate limiting considera proxies

## Recomendacoes

### Para Administradores

1. Use HTTPS em producao (exceto .onion)
2. Defina SECRET_KEY forte e unico
3. Defina ENCRYPTION_KEY forte e faca backup
4. Mantenha bancos de dados atualizados
5. Monitore logs de erro
6. Configure firewall adequadamente

### Para Usuarios

1. Use senhas fortes e unicas
2. Defina senha de download para arquivos sensiveis
3. Use menor tempo de expiracao possivel
4. Verifique hash SHA-256 apos download
5. Considere usar via Tor para anonimato
