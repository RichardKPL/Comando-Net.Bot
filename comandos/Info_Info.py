import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _create_info_embed(self, inviter: discord.User = None) -> discord.Embed:
        """Função auxiliar para criar o embed de informações, incluindo detalhes de status."""
        embed = discord.Embed(
            title="✨ Olá! Sou o Bot de Gestão Corporativa ✨",
            description=(
                "Fui projetado para ser o seu **assistente de gestão de corporação**. "
                "Minha missão é simplificar tarefas e automatizar processos, "
                "deixando sua equipe mais eficiente e focada no que realmente importa."
            ),
            color=0xffd700
        )

        embed.set_author(
            name="🤖 Assistente de Gestão Corporativa",
            icon_url=self.bot.user.display_avatar.url
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Campo sobre o desenvolvedor
        embed.add_field(
            name="🛠️ Desenvolvedor",
            value="Fui criado e sou mantido por **Castorizzando (Richard Kaua)**.",
            inline=False
        )

        # Campo que 'dedura' quem convidou o bot
        if inviter:
            embed.add_field(
                name="🔗 Convidado por",
                value=f"Fui adicionado neste servidor por {inviter.mention}.",
                inline=False
            )
        else:
            embed.add_field(
                name="🔗 Convidado por",
                value="Não consegui identificar quem me adicionou. Mas, de qualquer forma, obrigado!",
                inline=False
            )
        
        # Campo para guiar o usuário aos comandos
        embed.add_field(
            name="💡 Comece agora!",
            value="Use o comando **/ajuda** para ver a lista completa de funcionalidades e descobrir tudo que posso fazer por sua corporação.",
            inline=False
        )
        
        # Informações adicionais
        embed.add_field(
            name="📊 Status e Estatísticas",
            value=f"Servidores: **{len(self.bot.guilds)}**\nUsuários: **{len(self.bot.users)}**",
            inline=True
        )

        embed.add_field(
            name="✨ Links Úteis",
            value=f"[Convide-me para seu servidor](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)",
            inline=True
        )

        embed.set_footer(
            text="Conte comigo para organizar a sua corporação!",
            icon_url=self.bot.user.display_avatar.url
        )
        
        return embed

    @app_commands.command(
        name="info",
        description="Apresenta um resumo sobre mim e meu desenvolvedor."
    )
    async def info(self, interaction: discord.Interaction):
        embed = self._create_info_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        # Aguarda um curto período para garantir que o bot tenha permissões e informações.
        await asyncio.sleep(2) 
        
        # Tenta encontrar o canal de sistema
        channel = guild.system_channel
        
        # Se não houver, procura o primeiro canal de texto onde pode enviar mensagens.
        if channel is None:
            for text_channel in guild.text_channels:
                if text_channel.permissions_for(guild.me).send_messages:
                    channel = text_channel
                    break
        
        # Envia a mensagem de boas-vindas se um canal for encontrado.
        if channel:
            try:
                # 'Dedura' quem convidou o bot, buscando no registro de auditoria.
                inviter = None
                async for log_entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                    if log_entry.target.id == self.bot.user.id:
                        inviter = log_entry.user
                        break
                
                embed = self._create_info_embed(inviter=inviter)
                
                await channel.send("Olá! Fui adicionado ao servidor e estou pronto para ajudar. Use **/info** para saber mais sobre mim e **/ajuda** para ver meus comandos.", embed=embed)
            except discord.Forbidden:
                print(f"Não foi possível enviar a mensagem de boas-vindas no servidor {guild.name} ({guild.id})")

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))