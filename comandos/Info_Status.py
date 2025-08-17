
import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    @app_commands.command(
        name="status",
        description="Mostra informações e o status atual do bot."
    )
    async def status(self, interaction: discord.Interaction):
        # Calcula o tempo de atividade do bot (uptime)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        uptime = current_time - self.start_time
        
        days, remainder = divmod(uptime.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_string = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # Cria o embed de status
        embed = discord.Embed(
            title="📊 Status do Bot",
            description="Informações em tempo real sobre o desempenho do bot.",
            color=0x2ecc71 # Cor verde, indicando que está online
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.add_field(
            name="📶 Latência (Ping)",
            value=f"**{round(self.bot.latency * 1000)}ms**",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Tempo de Atividade",
            value=f"**{uptime_string}**",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Servidores",
            value=f"**{len(self.bot.guilds)}**",
            inline=True
        )
        
        embed.add_field(
            name="👥 Usuários",
            value=f"**{len(self.bot.users)}**",
            inline=True
        )
        
        embed.set_footer(
            text=f"Solicitado por {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))