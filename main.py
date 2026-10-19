import os
import sys
from pathlib import Path
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Exibe versão do discord.py
print("🔹 Versão do discord.py:", discord.__version__)

# Carregar .env
print("🔹 Carregando variáveis de ambiente...")
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Erro: DISCORD_TOKEN não encontrado no .env")
    sys.exit(1)
else:
    print("✅ Token carregado com sucesso.")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot
print("🔹 Inicializando bot...")
bot = commands.Bot(command_prefix="/", intents=intents)

# --- Função de reinício ---
def reiniciar_bot():
    """Reinicia o script atual em Python"""
    print("🔄 Reiniciando bot...")
    python = sys.executable
    os.execv(python, [python] + sys.argv)

# --- Carregar Cogs ---
async def carregar_cogs():
    print("🔹 Carregando Cogs da pasta comandos...")
    for caminho in sorted((Path(__file__).resolve().parent / "comandos").glob("*.py")):
        arquivo = caminho.name
        if arquivo.endswith(".py") and arquivo != "__init__.py":
            cog_name = arquivo[:-3]
            try:
                # Usa bot.load_extension para carregar e recarregar
                # (load_extension recarrega se já existir)
                if f"comandos.{cog_name}" in bot.extensions:
                    await bot.reload_extension(f"comandos.{cog_name}")
                    print(f"♻️ Cog recarregado: {arquivo}")
                else:
                    await bot.load_extension(f"comandos.{cog_name}")
                    print(f"✅ Cog carregado: {arquivo}")
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")

# --- Evento on_ready ---
@bot.event
async def on_ready():
    print(f"🎉 Bot conectado como {bot.user} ({bot.user.id})")
    
    # Sincronização em todas as Guilds (forçada para garantir)
    print("🔄 Forçando a sincronização em todas as guilds...")
    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=guild)
            print(f"✅ Comandos sincronizados na guild: {guild.name} ({guild.id})")
        except Exception as e:
            print(f"❌ Erro ao sincronizar comandos na guild {guild.name}: {e}")
            
    # Sincronização Global (executada apenas uma vez para evitar atrasos)
    if not hasattr(bot, 'is_synced'):
        bot.is_synced = False
    
    if not bot.is_synced:
        try:
            print("🌐 Iniciando sincronização global...")
            synced_commands = await bot.tree.sync()
            print(f"✅ Comandos sincronizados globalmente: {len(synced_commands)} comandos.")
            bot.is_synced = True
        except Exception as e:
            print(f"❌ Erro na sincronização global: {e}")

# --- Main ---
async def main():
    while True:
        try:
            async with bot:
                await carregar_cogs()
                await bot.start(TOKEN)
        except KeyboardInterrupt:
            print("⚠️ Bot encerrado manualmente.")
            break
        except Exception as e:
            print(f"❌ Bot caiu com erro: {e}")
            reiniciar_bot()

# --- Executar ---
if __name__ == "__main__":
    asyncio.run(main())