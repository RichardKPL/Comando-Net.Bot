import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime

# --- Views ---
class BOPMStartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Iniciar Novo BO PM", style=discord.ButtonStyle.red, custom_id="bopm_start_button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BOPMForm1(interaction.user))

# --- Botões para continuar entre etapas ---
class ContinuarBOPMButtonEtapa2(discord.ui.View):
    def __init__(self, author, dados):
        super().__init__(timeout=None)
        self.author = author
        self.dados = dados

    @discord.ui.button(label="Continuar para Etapa 2", style=discord.ButtonStyle.primary)
    async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)
            return
        await interaction.response.send_modal(BOPMForm2(self.author, self.dados))
        await interaction.delete_original_response()
        self.stop()

class ContinuarBOPMButtonEtapa3(discord.ui.View):
    def __init__(self, author, dados):
        super().__init__(timeout=None)
        self.author = author
        self.dados = dados

    @discord.ui.button(label="Continuar para Etapa 3", style=discord.ButtonStyle.primary)
    async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)
            return
        await interaction.response.send_modal(BOPMForm3(self.author, self.dados))
        await interaction.delete_original_response()
        self.stop()

# --- Modal Etapa 1 ---
class BOPMForm1(discord.ui.Modal, title="BO PM - Etapa 1"):
    def __init__(self, author):
        super().__init__()
        self.author = author

        self.guarnicao = discord.ui.TextInput(
            label="BO PM / Guarnição - Prefixo", 
            placeholder="Ex: I-12345", 
            required=True
        )
        self.encarregado = discord.ui.TextInput(
            label="Encarregado", 
            placeholder="Ex: Sd. Kaua", 
            required=True
        )
        self.motorista = discord.ui.TextInput(
            label="Motorista", 
            placeholder="Ex: Sd. Richard", 
            required=True
        )
        self.homem3 = discord.ui.TextInput(
            label="3º Homem", 
            placeholder="Ex: Sd. João", 
            required=False
        )
        self.homem4 = discord.ui.TextInput(
            label="4º Homem", 
            placeholder="Ex: Sd. Felipe", 
            required=False
        )

        self.add_item(self.guarnicao)
        self.add_item(self.encarregado)
        self.add_item(self.motorista)
        self.add_item(self.homem3)
        self.add_item(self.homem4)

    async def on_submit(self, interaction: discord.Interaction):
        dados = {
            "guarnicao": self.guarnicao.value,
            "encarregado": self.encarregado.value,
            "motorista": self.motorista.value,
            "homem3": self.homem3.value,
            "homem4": self.homem4.value
        }

        await interaction.response.send_message(
            "✅ Etapa 1 concluída! Clique no botão abaixo para abrir a Etapa 2.",
            ephemeral=True,
            view=ContinuarBOPMButtonEtapa2(self.author, dados)
        )

# --- Modal Etapa 2 ---
class BOPMForm2(discord.ui.Modal, title="BO PM - Etapa 2"):
    def __init__(self, author, etapa1_dados):
        super().__init__()
        self.author = author
        self.etapa1 = etapa1_dados

        self.nome_suspeitos = discord.ui.TextInput(
            label="Nome(s) do(s) suspeito(s)", 
            placeholder="Ex: Carlos, Maria", 
            required=True
        )
        self.rgs_suspeitos = discord.ui.TextInput(
            label="RG(s) dos suspeitos", 
            placeholder="Ex: 12.345.678-9, 98.765.432-1", 
            required=True
        )

        self.add_item(self.nome_suspeitos)
        self.add_item(self.rgs_suspeitos)

    async def on_submit(self, interaction: discord.Interaction):
        dados = self.etapa1.copy()
        dados.update({
            "nome_suspeitos": self.nome_suspeitos.value,
            "rgs_suspeitos": self.rgs_suspeitos.value
        })

        await interaction.response.send_message(
            "✅ Etapa 2 concluída! Clique no botão abaixo para abrir a Etapa 3.",
            ephemeral=True,
            view=ContinuarBOPMButtonEtapa3(self.author, dados)
        )

# --- Modal Etapa 3 ---
class BOPMForm3(discord.ui.Modal, title="BO PM - Etapa 3"):
    def __init__(self, author, dados):
        super().__init__()
        self.author = author
        self.dados = dados

        self.natureza_fatos = discord.ui.TextInput(
            label="Natureza dos fatos", 
            placeholder="Ex: Tráfico de Drogas, Furto, Homicídio", 
            required=True
        )
        self.artigos_delitos = discord.ui.TextInput(
            label="Artigos / Delitos", 
            placeholder="Ex: Artigo 33, Artigo 155", 
            required=False
        )
        self.apreensao = discord.ui.TextInput(
            label="Apreensão", 
            placeholder="Ex: 50g de cocaína, 1 Revólver cal. 38, R$ 150,00", 
            required=False
        )
        self.ocorrencia = discord.ui.TextInput(
            label="Ocorrência / Detalhes", 
            style=discord.TextStyle.paragraph, 
            placeholder="Descreva o local, horário e todos os detalhes do ocorrido.", 
            required=False
        )

        self.add_item(self.natureza_fatos)
        self.add_item(self.artigos_delitos)
        self.add_item(self.apreensao)
        self.add_item(self.ocorrencia)

    async def on_submit(self, interaction: discord.Interaction):
        bopm_id = random.randint(1000, 9999)
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        embed = discord.Embed(
            title=f"📋 Boletim de Ocorrência da PM - #{bopm_id}",
            color=0xc0392b
        )
        
        embed.set_author(name=f"Assinado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.user.display_avatar.url) # Mantém a foto do usuário na miniatura

        embed.add_field(name="👮 Equipe", value=f"""
**Encarregado:** {self.dados['encarregado']}
**Motorista:** {self.dados['motorista']}
**3º Homem:** {self.dados['homem3'] or "-"}
**4º Homem:** {self.dados['homem4'] or "-"}
""", inline=False)
        
        embed.add_field(name="---", value="", inline=False)

        embed.add_field(name="📌 Suspeito(s)", value=f"""
**Nome(s):** {self.dados['nome_suspeitos']}
**RG(s):** {self.dados['rgs_suspeitos']}
""", inline=False)

        embed.add_field(name="📜 Natureza dos fatos", value=self.natureza_fatos.value, inline=False)
        embed.add_field(name="⚖️ Artigos / Delitos", value=self.artigos_delitos.value or "-", inline=False)
        embed.add_field(name="📦 Apreensão", value=self.apreensao.value or "-", inline=False)
        embed.add_field(name="📝 Ocorrência", value=self.ocorrencia.value or "-", inline=False)

        # Adiciona o footer com a foto do bot, nome e data/hora
        embed.set_footer(
            text=f"BO PM registrado por {interaction.client.user.display_name} • {current_time}",
            icon_url=interaction.client.user.display_avatar.url
        )

        await interaction.response.send_message(
            content=f"📌 BO PM registrado por {interaction.user.mention}",
            embed=embed
        )

# --- Cog ---
class BOPM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(BOPMStartView())

    @app_commands.command(
        name="setbopm",
        description="Envia o painel de BO PM para o canal selecionado."
    )
    @app_commands.describe(channel="O canal onde o painel será enviado.")
    @app_commands.default_permissions(manage_channels=True)
    async def setbopm(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="📋 Painel de Boletim de Ocorrência da Polícia Militar",
            description="Clique no botão abaixo para iniciar um novo BO PM.",
            color=discord.Color.red()
        )
        
        embed.set_author(name=interaction.client.user.display_name, icon_url=interaction.client.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_footer(text="Um registro detalhado é essencial para a investigação e documentação. 🚔")
        
        await channel.send(embed=embed, view=BOPMStartView())
        await interaction.response.send_message(f"✅ Painel de BO PM enviado para o canal {channel.mention}!", ephemeral=True)

# --- Setup ---
async def setup(bot):
    await bot.add_cog(BOPM(bot))