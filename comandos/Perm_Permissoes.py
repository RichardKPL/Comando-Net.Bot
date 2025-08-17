import discord
from discord.ext import commands

# Lista de todos os comandos que exigem permissão de administrador para serem executados
ADMIN_COMMANDS = [
    "setboletim", "setboletimcanal",
    "settransferencia", "settransferenciaap",
    "setfuncional", "funcionalcargos", "setfuncionalap",
    "setausencia", "setausenciacanal","settransferenciadmin", "setfuncionaladmin",
]

class SetCommandLimiter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command(self, interaction: discord.Interaction):
        cmd_name = interaction.command.name.lower()

        # Ignorar comandos que não estão na lista
        if cmd_name not in ADMIN_COMMANDS + ["setcargos"]:
            return

        # Permissão para setcargos: Gerenciar Cargos
        if cmd_name == "setcargos":
            if not interaction.user.guild_permissions.manage_roles:
                await interaction.response.send_message(
                    "❌ Você precisa da permissão 'Gerenciar Cargos' para usar este comando.", ephemeral=True
                )
                raise commands.CheckFailure(f"Usuário {interaction.user} sem permissão tentou usar {cmd_name}.")
            return

        # Permissão para outros set*: Gerenciar Canais
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "❌ Você precisa da permissão 'Gerenciar Canais' para usar este comando.", ephemeral=True
            )
            raise commands.CheckFailure(f"Usuário {interaction.user} sem permissão tentou usar {cmd_name}.")

# --- Setup ---
async def setup(bot: commands.Bot):
    await bot.add_cog(SetCommandLimiter(bot))
