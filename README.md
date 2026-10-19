# Comando-Net.Bot

Bot de Discord em Python para gerenciamento de batalhões de FiveM, com painéis de ausências, boletins, BOPM, funcionais, transferências, cargos e RSO.

## Instalação

Use Python 3.13 em um ambiente virtual e execute os comandos na raiz deste repositório.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

No Linux/macOS, use `.venv/bin/python` e `cp .env.example .env`.
Edite `.env` e substitua o valor de `DISCORD_TOKEN` pelo token do seu bot.

## Configuração do Discord

No Developer Portal, habilite os intents **Server Members** e **Message Content**, usados em `main.py`.
Convide a aplicação ao servidor com os escopos `bot` e `applications.commands`.
Conceda as permissões de canais e cargos necessárias aos módulos que pretende usar.
A hierarquia de cargos do Discord também limita quais cargos o bot pode administrar.

## Executar

```powershell
.venv/Scripts/python main.py
```

No Linux/macOS, use `.venv/bin/python main.py`.
Use `/ajuda`, `/info` e `/status` no servidor para consultar os recursos disponíveis.
Os canais e cargos dos painéis são configurados pelos comandos de cada módulo.

## Dados locais

Os módulos gravam configurações e solicitações em arquivos JSON relativos à pasta de execução.
Mantenha a execução na raiz do projeto e faça backup desses arquivos antes de atualizar o bot.
Não publique `.env`, registros de usuários ou logs contendo dados pessoais.

## Comandos

Consulte a [referência dos comandos](docs/COMANDOS.md) implementados nos módulos.

## Operação

Consulte [backup, restauração e diagnóstico](docs/OPERACAO.md).

## Licença

Este projeto usa a [licença MIT](LICENSE).
