# TorFiles - Sistema de Compartilhamento Seguro de Arquivos

## Visao Geral

TorFiles e um sistema web para upload e compartilhamento seguro de arquivos compactados. Desenvolvido com foco em privacidade, seguranca e anonimato.

- **Images do projeto**
- ![Screenshot ilustrativa do projeto](./screenshot.png)

## Principais Funcionalidades

- **Criptografia AES-256**: Todos os arquivos sao criptografados antes de serem armazenados
- **Codigos de 5 digitos**: Compartilhamento facil via codigos curtos e aleatorios
- **Controle de downloads**: Limite de quantas vezes um arquivo pode ser baixado
- **Expiracao automatica**: Defina por quanto tempo o arquivo fica disponivel
- **Senha opcional**: Proteja downloads com uma senha adicional
- **Anonimato**: Registro sem email, compativel com Tor

## Stack Tecnologica

- **Backend**: Python Flask
- **Frontend**: HTML + CSS + JavaScript puro
- **Banco de dados**:
  - MariaDB: Usuarios e metadados
  - PostgreSQL: Arquivos criptografados (BLOB)
- **Criptografia**: AES-256 via Fernet, Argon2 para senhas

## Arquivos Suportados

- `.zip`
- `.rar`
- `.7z`

Tamanho maximo: 100MB

## Limites

- Maximo de 3 arquivos ativos por usuario
- Arquivos pausados/expirados nao contam no limite

## Inicio Rapido

1. Crie uma conta (sem necessidade de email)
2. Faca upload de um arquivo compactado
3. Compartilhe o codigo de 5 digitos
4. O destinatario acessa `/d/CODIGO` para baixar

## Navegacao

- [Arquitetura](./arquitetura.md) - Estrutura do sistema
- [API](./api.md) - Endpoints e rotas
- [Banco de Dados](./database.md) - Schemas e estrutura
- [Seguranca](./security.md) - Medidas de protecao
- [Deployment](./deployment.md) - Como implantar
- [Uso](./usage.md) - Guia de uso detalhado

### License

> Este projeto está licenciado sob a GNU License v2.0 (GPL-2.0). Consulte o arquivo LICENSE para obter detalhes.

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)