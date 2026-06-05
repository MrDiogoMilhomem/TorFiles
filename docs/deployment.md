# Deployment

## Requisitos

- Python 3.9+
- MariaDB 10.5+
- PostgreSQL 13+

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

### 3. Criar .env
```bash
python3 GenBaseEnv.py .env
```

### 4. Configurar Variaveis

```bash
MARIADB_URL=mysql://user:password@host:3306/torfiles
POSTGRES_URL=postgresql://user:password@host:5432/torfiles

SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXX
ENCRYPTION_KEY=XXXXXXXXXXXXXXXXXXXXXXXXX

# habilitar a documentaçao do app
DOCS_ENABLED=true

# Configuraçoes do desemvolvimento local
LOCALDEV=true
LOCALDEV_DEBUG=true
LOCALDEV_HOST='127.0.0.1'
LOCALDEV_PORT=5000
```

### 5. Executar

**Desenvolvimento:**
```bash
python app.py
```

**Produçao**
```bash
gunicorn -w <workers> -b 127.0.0.1:8000 app:app 
```

---

## Deploy com Docker

O Docker empacota a aplicação e todas as suas dependências em um container isolado, eliminando a necessidade de configurar Python, libs do sistema ou o Gunicorn manualmente no servidor.

### Requisitos

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+

### Arquivos necessários

Certifique-se de que os arquivos `Dockerfile`, `.dockerignore` e `docker-compose.yml` estão na raiz do projeto (ao lado de `app.py`).

### 1. Gerar as Chaves e o .env basico com as chaves

Antes de qualquer coisa, gere o .env com as chaves usando o comando:

```python
python3 GenBaseDockerEnv.py .env
```

### 2. Criar o arquivo .env

Edite o arquivo `.env` gerado na raiz do projeto com as variáveis de ambiente, nele vai aparecer:

```bash
# Segurança
SECRET_KEY=XXXXXXXXXXXXXX
ENCRYPTION_KEY=XXXXXXXXXXXXXX

# Senhas dos bancos (escolha senhas fortes)
MARIADB_ROOT_PASSWORD=senha-root-forte
MARIADB_PASSWORD=senha-torfiles-forte
POSTGRES_PASSWORD=senha-torfiles-forte

# Opcional
DOCS_ENABLED=true
```
Coloque senhas **FORTES** para o mariadb e para o postgresql

> As URLs dos bancos (`MARIADB_URL` e `POSTGRES_URL`) são montadas automaticamente pelo `docker-compose.yml` usando os serviços `mariadb` e `postgres` como hostname — não é necessário defini-las no `.env` ao usar o Compose.

### 3. Build da imagem

Constrói a imagem Docker da aplicação a partir do `Dockerfile`:

```bash
docker build -t torfiles:latest .
```

O build usa múltiplos estágios: o primeiro estágio compila as dependências Python, o segundo gera a imagem final enxuta sem ferramentas de compilação.

Para forçar rebuild do zero (sem cache):

```bash
docker build --no-cache -t torfiles:latest .
```

### 4. Subir com Docker Compose

O Compose sobe a aplicação junto com os bancos MariaDB e PostgreSQL, já configurados e conectados entre si:

```bash
docker compose up -d
```

A flag `-d` roda os containers em segundo plano. As tabelas dos bancos são criadas automaticamente na primeira execução.

Para acompanhar os logs em tempo real:

```bash
docker compose logs -f
```

Para parar tudo:

```bash
docker compose down
```

> Os dados dos bancos ficam em volumes Docker (`mariadb_data` e `postgres_data`) e **persistem** entre reinicializações. Para apagar os dados junto com os containers, use `docker compose down -v`.

### 5. Verificar se está rodando

```bash
docker compose ps
```

A aplicação estará disponível em `http://localhost:8000`.

### Atualizar após mudanças no código

Sempre que alterar o código, refaça o build e reinicie:

```bash
docker compose down
docker build -t torfiles:latest .
docker compose up -d
```

### Workers do Gunicorn no Docker

O `Dockerfile` já define 2 workers por padrão. Para ajustar, sobrescreva o `CMD` no `docker-compose.yml`:

```yaml
services:
  app:
    command: >
      gunicorn
      --bind 0.0.0.0:8000
      --workers 5
      --threads 2
      --timeout 120
      --log-level info
      --access-logfile -
      --error-logfile -
      app:app
```

Aplique a mesma regra `(2 × núcleos) + 1` descrita na seção de Workers abaixo.

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