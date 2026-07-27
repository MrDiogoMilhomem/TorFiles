# Arquitetura do Sistema

## Visao Geral

O TorFiles segue uma arquitetura modular em camadas, separando responsabilidades entre rotas, servicos, modelos e utilitarios.

## Estrutura de Diretorios

```
backend/
├── app.py                 # Aplicacao Flask principal
├── config.py              # Configuracoes e variaveis de ambiente
├── models/
│   ├── user.py            # Modelo de usuario
│   └── file.py            # Modelo de arquivo
├── routes/
│   ├── auth.py            # Autenticacao
│   ├── upload.py          # Upload de arquivos
│   ├── download.py        # Download de arquivos
│   ├── dashboard.py       # Dashboard do usuario
│   └── docs.py            # Documentacao
├── services/
│   ├── database.py        # Conexoes com bancos
│   ├── crypto.py          # Criptografia
│   ├── code_generator.py  # Geracao de codigos
│   └── cleanup.py         # Limpeza automatica
├── utils/
│   ├── validators.py      # Validacao de inputs
│   ├── rate_limiter.py    # Rate limiting
│   └── helpers.py         # Funcoes auxiliares
├── templates/             # Templates HTML
├── static/                # CSS e JavaScript
└── docs/                  # Documentacao Markdown
```

## Fluxo de Dados

### Upload

1. Usuario faz upload via formulario
2. Arquivo e validado (tipo, tamanho)
3. Hash SHA-256 e calculado
4. Arquivo e criptografado com AES-256
5. Metadados salvos no MariaDB
6. Arquivo criptografado salvo no PostgreSQL
7. Codigo de 5 digitos e gerado e retornado

### Download

1. Usuario acessa `/d/CODIGO`
2. Metadados sao buscados no MariaDB
3. Validacoes: expiracao, downloads, status
4. Se tem senha, valida senha
5. Arquivo criptografado e buscado no PostgreSQL
6. Arquivo e descriptografado
7. Contador de downloads e decrementado
8. Arquivo e enviado ao usuario

## Componentes Principais

### MariaDB

Armazena dados estruturados:
- Usuarios (credenciais)
- Metadados de arquivos (codigo, expiracao, downloads, etc.)

### PostgreSQL

Armazena dados binarios:
- Arquivos criptografados como BYTEA

### Servico de Criptografia

- Usa Fernet (AES-256) para arquivos
- Argon2 para hash de senhas
- Derivacao de chave via PBKDF2 quando ha senha de download

### Worker de Limpeza

- Thread em background
- Executa a cada minuto
- Marca arquivos expirados
- Remove arquivos antigos (opcional)

## Consideracoes de Design

### Separacao de Bancos

A separacao entre MariaDB e PostgreSQL permite:
- Otimizar cada banco para seu tipo de dado
- Escalar independentemente
- Manter metadados acessiveis mesmo com grande volume de arquivos

### Stateless

A aplicacao e stateless, permitindo:
- Escalabilidade horizontal
- Deploy em ambiente serverless (Vercel)
- Sessoes via cookies assinados

### Seguranca em Camadas

- Criptografia em repouso (AES-256)
- Hash de senhas (Argon2)
- Rate limiting
- Validacao de inputs
- Cookies seguros

### License

> Este projeto está licenciado sob a GNU License v2.0 (GPL-2.0). Consulte o arquivo LICENSE para obter detalhes.

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)