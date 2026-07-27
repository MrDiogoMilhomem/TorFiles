# Guia de Uso

## Criando uma Conta

1. Acesse a pagina inicial
2. Clique em "Criar Conta"
3. Escolha um username (3-50 caracteres)
4. Crie uma senha forte (minimo 8 caracteres, letras e numeros)
5. Confirme a senha
6. Clique em "Criar Conta"

**Nota:** Nao e necessario email. Guarde seu username e senha com seguranca.

## Fazendo Upload

1. Faca login na sua conta
2. Clique em "Upload" ou "Novo Upload"
3. Selecione um arquivo (.zip, .rar ou .7z)
4. Preencha os campos:
   - **Descricao** (opcional): Descreva o conteudo
   - **Limite de Downloads**: Quantas vezes pode ser baixado
   - **Tempo de Expiracao**: Quando o arquivo sera removido
   - **Senha** (opcional): Proteja o download com senha
5. Clique em "Enviar Arquivo"
6. Copie o codigo de 5 digitos gerado

## Compartilhando

Apos o upload, voce recebe um codigo de 5 digitos (ex: `X7K9M`).

Compartilhe de duas formas:

1. **Codigo direto**: Envie `X7K9M`
2. **Link completo**: Envie `https://seusite.com/d/X7K9M`

Se definiu senha, envie a senha separadamente por outro canal.

## Baixando um Arquivo

1. Acesse `/d` ou `/d/CODIGO`
2. Insira o codigo de 5 digitos
3. Verifique as informacoes:
   - Nome do arquivo
   - Descricao
   - Hash SHA-256
   - Downloads restantes
4. Se requerido, insira a senha
5. Clique em "Baixar Arquivo"

### Verificando Integridade

Apos baixar, verifique o hash SHA-256:

**Windows (PowerShell):**
```powershell
Get-FileHash arquivo.zip -Algorithm SHA256
```

**Linux/Mac:**
```bash
sha256sum arquivo.zip
```

Compare com o hash exibido no site.

## Dashboard

### Visualizando Arquivos

O dashboard mostra seus arquivos em 3 secoes:
- **Ativos**: Disponiveis para download
- **Pausados**: Temporariamente bloqueados
- **Expirados**: Nao podem mais ser baixados

### Acoes Disponiveis

**Copiar Codigo:**
Clique no icone de copia ao lado do codigo.

**Pausar:**
Bloqueia downloads temporariamente. Util para:
- Investigar uso suspeito
- Pausar compartilhamento sem apagar

**Reativar:**
Volta a permitir downloads de arquivo pausado.

**Apagar:**
Remove completamente o arquivo. Esta acao e irreversivel.

## Limites

- **Arquivos ativos**: Maximo 3 por usuario
- **Tamanho**: Maximo 100MB por arquivo
- **Tipos**: Apenas .zip, .rar, .7z

Arquivos pausados e expirados nao contam no limite de 3.

## Expiracao

Arquivos expiram quando:
- O tempo definido passa
- O limite de downloads e atingido (opcional)

Arquivos expirados:
- Nao podem ser baixados
- Permanecem no dashboard para referencia
- Podem ser apagados manualmente

## Boas Praticas

### Seguranca

1. Use senhas diferentes para cada arquivo sensivel
2. Defina o menor tempo de expiracao possivel
3. Use o minimo de downloads necessario
4. Verifique hash apos download

### Privacidade

1. Nao inclua informacoes pessoais na descricao
2. Compartilhe codigo e senha por canais diferentes
3. Apague arquivos apos uso
4. Considere usar Tor para anonimato

### Organizacao

1. Use descricoes claras
2. Monitore downloads no dashboard
3. Pause arquivos quando nao estiver compartilhando ativamente
4. Limpe arquivos expirados regularmente

## Resolucao de Problemas

### "Codigo nao encontrado"

- Verifique se digitou corretamente (5 caracteres)
- O arquivo pode ter sido apagado
- O arquivo pode ter expirado

### "Arquivo expirado"

- O tempo de expiracao passou
- Os downloads chegaram a zero
- Contate quem compartilhou para novo upload

### "Arquivo pausado"

- O proprietario pausou temporariamente
- Aguarde reativacao ou contate o proprietario

### "Muitas tentativas"

- Rate limiting ativado
- Aguarde o tempo indicado
- Verifique se esta usando o codigo/senha corretos

### "Limite de arquivos atingido"

- Voce tem 3 arquivos ativos
- Pause ou apague algum arquivo
- Aguarde expiracao de algum arquivo

### License

> Este projeto está licenciado sob a GNU License v2.0 (GPL-2.0). Consulte o arquivo LICENSE para obter detalhes.

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)