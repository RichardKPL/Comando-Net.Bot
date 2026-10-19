# Como contribuir

1. Crie uma branch a partir de `main`.
2. Instale as dependências em um ambiente virtual seguindo o README.
3. Mantenha cada alteração focada em um problema e descreva o comportamento antes e depois no PR.
4. Verifique a sintaxe antes de enviar:

```sh
python -m compileall -q main.py comandos
git diff --check
```

A verificação de sintaxe não testa interações com o Discord. Mudanças em comandos, permissões e views precisam de um servidor de teste e uma aplicação própria, nunca do token de produção de outra pessoa.

Cada extensão em `comandos/` expõe `async def setup(bot)` para registrar seu Cog.
Ao adicionar um comando, atualize a ajuda correspondente e descreva as permissões necessárias.
Evite versionar bytecode, ambientes virtuais, dados JSON do servidor e tokens.
Para problemas, informe comando, passos para reproduzir, versões do Python/discord.py e uma saída de erro sem credenciais ou dados pessoais.
