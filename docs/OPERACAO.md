# Operação e diagnóstico

## Pasta de execução e persistência

Inicie o processo na raiz do repositório. Os caminhos dos JSON e logs são relativos à pasta corrente, mesmo que a descoberta de extensões use a pasta de main.py.
Use somente uma instância por diretório de dados: a persistência em JSON não oferece coordenação entre processos.

## Backup e restauração

1. Pare o bot para evitar cópias durante uma gravação.
2. Copie os JSON locais e o `.env` para um destino privado e protegido.
3. Atualize o código e reinstale as dependências se necessário.
4. Para restaurar, pare o bot, recoloque os arquivos na mesma pasta de execução e inicie novamente.

Arquivos presentes incluem `ausencia_canais.json`, `boletim_canais.json`, `solicitacoes_funcional.json`, `funcional_cargos.json`, `funcional_config.json`, `funcional_admin_roles.json`, `transferencias.json`, `transferencia_cargos.json`, `transferencia_config.json` e `transferencia_admin_roles.json`.

## Erros comuns

| Sintoma | Verificação |
| --- | --- |
| DISCORD_TOKEN não encontrado | Confira a variável no ambiente ou no .env; espaços nas extremidades são removidos. |
| Login recusado | Confira se o token é da aplicação correta e não foi revogado. Não o inclua no relato de erro. |
| Intent não permitido | Confira Server Members e Message Content no Developer Portal. |
| Cog não carregado | Consulte a mensagem de erro do módulo e confirme a instalação de requirements.txt. |
| Comando ausente | Confira erros de carregamento/sincronização e o convite com applications.commands. |
| Atribuição de cargo recusada | Confira Gerenciar Cargos e a posição do cargo do bot na hierarquia. |
| Configurações desapareceram | Confira se o processo foi iniciado na mesma pasta de antes. |

Os registros de falha de sincronização e carregamento aparecem na saída do processo.
O comando `/status` informa latência e tempo de atividade; ele não substitui o diagnóstico dos logs.
