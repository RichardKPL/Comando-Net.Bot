import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DE DADOS ---
DATA_FILE = "ausencia_canais.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        canal_ausencia_dict = data.get("ausencia", {})
else:
    canal_ausencia_dict = {}

def salvar_dados():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"ausencia": canal_ausencia_dict}, f, indent=4)

# --- Modal Etapa 1 ---
class AusenciaForm1(discord.ui.Modal, title="📝 Registro de Ausência | Etapa 1"):
    def __init__(self, author):
        super().__init__()
        self.author = author

        self.qra = discord.ui.TextInput(label="👤 Nome/QRA Completo", required=True, placeholder="Ex: Cb. Richard")
        self.rg = discord.ui.TextInput(label="🆔 RG", required=True, placeholder="Ex: 12.345.678-9")
        self.patente = discord.ui.TextInput(label="🎓 Graduação/Patente", required=True, placeholder="Ex: Cabo, Soldado, Aspirante")
        self.motivo = discord.ui.TextInput(label="❓ Motivo da Ausência", style=discord.TextStyle.paragraph, required=True, placeholder="Ex: Férias, Luto, Problemas Pessoais...")
        self.data = discord.ui.TextInput(label="🗓️ Data de Retorno", required=True, placeholder="Ex: 15/08/2025")

        self.add_item(self.qra)
        self.add_item(self.rg)
        self.add_item(self.patente)
        self.add_item(self.motivo)
        self.add_item(self.data)

    async def on_submit(self, interaction: discord.Interaction):
        dados = {
            "qra": self.qra.value,
            "rg": self.rg.value,
            "patente": self.patente.value,
            "motivo": self.motivo.value,
            "data": self.data.value
        }

        await interaction.response.send_message(
            "✅ Etapa 1 concluída! Clique no botão para a Etapa 2.",
            ephemeral=True,
            view=AusenciaContinuarButton(self.author, dados)
        )

# --- Modal Etapa 2 ---
class AusenciaForm2(discord.ui.Modal, title="📝 Registro de Ausência | Etapa 2"):
    def __init__(self, author, etapa1_dados):
        super().__init__()
        self.author = author
        self.etapa1 = etapa1_dados

        self.observacoes = discord.ui.TextInput(
            label="📝 Observações Adicionais",
            style=discord.TextStyle.paragraph,
            placeholder="Adicione informações que a equipe precisa saber. (Opcional)",
            required=False
        )
        self.add_item(self.observacoes)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        canal_id = canal_ausencia_dict.get(guild_id)

        if not canal_id:
            await interaction.response.send_message(
                "❌ O canal de ausências ainda não foi configurado! Use /setausenciacanal para definir.",
                ephemeral=True
            )
            return

        canal = interaction.guild.get_channel(canal_id)
        if not canal:
            await interaction.response.send_message(
                "❌ Canal configurado não encontrado no servidor!",
                ephemeral=True
            )
            return
        
        # Embeleza o embed final
        embed = discord.Embed(
            title="✅ Registro de Ausência Aprovado",
            description=f"Uma nova ausência foi registrada por {interaction.user.mention}.",
            color=0x2ecc71
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_author(name=f"Por: {self.etapa1['qra']}", icon_url=interaction.user.display_avatar.url)
        
        embed.add_field(name="🎓 Graduação:", value=self.etapa1["patente"], inline=True)
        embed.add_field(name="🆔 RG:", value=self.etapa1["rg"], inline=True)
        embed.add_field(name="🗓️ Data de Retorno:", value=self.etapa1["data"], inline=False)
        embed.add_field(name="❓ Motivo:", value=self.etapa1["motivo"], inline=False)
        embed.add_field(name="📝 Observações:", value=self.observacoes.value or "Nenhuma observação adicional.", inline=False)

        embed.set_footer(
            text=f"Registrado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            icon_url=interaction.client.user.display_avatar.url
        )

        # Envia para o canal definido
        await canal.send(content="@everyone", embed=embed)

        await interaction.response.send_message(
            f"✅ Sua ausência foi registrada e enviada em {canal.mention}!", ephemeral=True
        )

# --- Botão para abrir Etapa 2 ---
class AusenciaContinuarButton(discord.ui.View):
    def __init__(self, author, dados):
        super().__init__(timeout=None)
        self.author = author
        self.dados = dados

    @discord.ui.button(label="Continuar para Etapa 2", style=discord.ButtonStyle.primary, custom_id="continuar_ausencia")
    async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)
            return
        await interaction.response.send_modal(AusenciaForm2(self.author, self.dados))
        self.stop()

# --- Botão persistente para painel público ---
class RegistrarAusenciaButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Registrar Nova Ausência", style=discord.ButtonStyle.primary, custom_id="registrar_ausencia")
    async def registrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AusenciaForm1(interaction.user))

# --- Cog ---
class Ausencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(RegistrarAusenciaButton())

    # Modal direto
    @app_commands.command(name="ausencia", description="Registrar ausência de um membro.")
    async def ausencia(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AusenciaForm1(interaction.user))

    # Painel público persistente
    @app_commands.command(name="setausencia", description="Cria um painel público de ausências.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setausencia(self, interaction: discord.Interaction, canal: discord.TextChannel):
        # Embeleza o embed do painel
        embed = discord.Embed(
            title="📌 Sistema de Registro de Ausências",
            description="Clique no botão abaixo para iniciar o registro de uma nova ausência. O formulário é privado e suas informações serão enviadas para o canal de ausências.",
            color=0x3498db
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_footer(text=f"Painel criado por {interaction.user.display_name}")
        await canal.send(embed=embed, view=RegistrarAusenciaButton())
        await interaction.response.send_message(f"✅ Painel de ausências criado em {canal.mention}.", ephemeral=True)

    # Definir canal de envio de ausências
    @app_commands.command(name="setausenciacanal", description="Define o canal onde as ausências serão enviadas.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setausenciacanal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        canal_ausencia_dict[guild_id] = canal.id
        salvar_dados()
        await interaction.response.send_message(f"✅ Canal de envio de ausências definido para {canal.mention}.", ephemeral=True)

# --- Setup ---
async def setup(bot):
    await bot.add_cog(Ausencia(bot))