# Segurança

## Informações sensíveis

Não publique tokens do Discord, arquivos `.env`, solicitações de usuários ou logs com dados pessoais em issues e pull requests.
O exemplo `.env.example` contém apenas um marcador e não deve receber credenciais reais.
O `.gitignore` não remove arquivos que já estejam no histórico do Git.

## Token exposto

Se um token real for publicado, redefina-o no Discord Developer Portal e atualize o ambiente do bot.
Apagar o arquivo atual não revoga o token nem apaga as cópias no histórico.

## Relato de vulnerabilidades

Procure a opção de relato privado na aba Security do repositório, caso esteja habilitada.
Se ela não estiver disponível, solicite ao mantenedor um canal privado sem divulgar detalhes exploráveis em público.
Inclua passos para reproduzir em um servidor de teste e as versões usadas; omita credenciais e dados de usuários.

## Operação

Conceda ao bot apenas as permissões necessárias aos módulos utilizados.
Restrinja o acesso ao diretório de dados e aos backups e revise a hierarquia de cargos antes de habilitar aprovações e transferências.
