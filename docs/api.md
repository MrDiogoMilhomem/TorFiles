# API e Rotas

## Rotas Publicas

### Pagina Inicial

```
GET /
```

Exibe a pagina inicial com informacoes sobre o sistema.

### Download

```
GET /d
GET /d/<codigo>
POST /d/<codigo>
```

- `GET /d`: Formulario para inserir codigo
- `GET /d/<codigo>`: Exibe informacoes do arquivo
- `POST /d/<codigo>`: Processa o download

**Parametros POST:**
- `download`: Flag de confirmacao
- `password`: Senha do arquivo (se necessario)

## Autenticacao

### Registro

```
GET /register
POST /register
```

**Parametros POST:**
- `username`: Nome de usuario (3-50 caracteres)
- `password`: Senha (minimo 8 caracteres)
- `confirm_password`: Confirmacao da senha

### Login

```
GET /login
POST /login
```

**Parametros POST:**
- `username`: Nome de usuario
- `password`: Senha

### Logout

```
GET /logout
```

Encerra a sessao do usuario.

## Rotas Autenticadas

### Dashboard

```
GET /dashboard
```

Exibe lista de arquivos do usuario.

### Upload

```
GET /upload
POST /upload
```

**Parametros POST (multipart/form-data):**
- `file`: Arquivo (.zip, .rar, .7z)
- `description`: Descricao (opcional, max 1000 chars)
- `password`: Senha de download (opcional)
- `download_limit`: Limite de downloads (1-1000)
- `expires_hours`: Horas ate expiracao

### Acoes no Dashboard

#### Apagar Arquivo

```
POST /dashboard/delete/<codigo>
```

Remove completamente o arquivo.

#### Pausar Arquivo

```
POST /dashboard/pause/<codigo>
```

Bloqueia downloads temporariamente.

#### Reativar Arquivo

```
POST /dashboard/activate/<codigo>
```

Reativa um arquivo pausado.

## Documentacao

```
GET /docs
GET /docs/<pagina>
```

Exibe documentacao em formato HTML.

## Codigos de Resposta

| Codigo | Significado |
|--------|-------------|
| 200 | Sucesso |
| 302 | Redirecionamento |
| 400 | Requisicao invalida |
| 401 | Nao autenticado |
| 403 | Proibido |
| 404 | Nao encontrado |
| 413 | Arquivo muito grande |
| 429 | Rate limit excedido |
| 500 | Erro interno |

## Rate Limiting

Endpoints sensiveis tem rate limiting:
- 5 tentativas por 5 minutos
- Baseado em IP
- Mensagem de erro indica tempo de espera

## Protecao CSRF

Todas as rotas POST sao protegidas por:
- Cookies SameSite
- Verificacao de sessao

### License

> Este projeto está licenciado sob a GNU License v2.0 (GPL-2.0). Consulte o arquivo LICENSE para obter detalhes.

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)