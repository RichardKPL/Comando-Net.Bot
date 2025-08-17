# PMESP – Batalhões
"1BPM", "3BPM", "5BPM", "11BPM", "16BPM", "18BPM", "23BPM", "28BPM", "39BPM",

# PMESP – RPM correspondentes aos Batalhões
"1RPM", "3RPM", "5RPM", "11RPM", "16RPM", "18RPM", "23RPM", "28RPM", "39RPM",

# PMESP – ROCAM das Especializadas
"ROCAM BAEP",
"ROCAM ROTA",
"ROCAM Força Tática",
"ROCAM CAEP",
"ROCAM CPTran",
"ROCAM CavPM",
"ROCAM COE",
"ROCAM GATE",
"ROCAM BPTran",
"ROCAM BPRv",
"ROCAM BPChq",

# PMERJ – Batalhões
"1BPM-RJ", "2BPM-RJ", "3BPM-RJ", "4BPM-RJ", "5BPM-RJ", "6BPM-RJ", "7BPM-RJ", "8BPM-RJ",
"9BPM-RJ", "10BPM-RJ", "11BPM-RJ", "12BPM-RJ", "13BPM-RJ", "14BPM-RJ", "15BPM-RJ", "16BPM-RJ",
"17BPM-RJ", "18BPM-RJ", "19BPM-RJ", "20BPM-RJ",

# PMERJ – RPM correspondentes aos Batalhões
"1RPM-RJ", "2RPM-RJ", "3RPM-RJ", "4RPM-RJ", "5RPM-RJ", "6RPM-RJ", "7RPM-RJ", "8RPM-RJ",
"9RPM-RJ", "10RPM-RJ", "11RPM-RJ", "12RPM-RJ", "13RPM-RJ", "14RPM-RJ", "15RPM-RJ", "16RPM-RJ",
"17RPM-RJ", "18RPM-RJ", "19RPM-RJ", "20RPM-RJ",

# PMERJ – ROCAM das Especializadas
"ROCAM BOPE",
"ROCAM BPChoque-RJ",
"ROCAM BPRv-RJ",
"ROCAM BPGE",
"ROCAM BAC",
"ROCAM BPMERJ Ambiental",
"ROCAM UPP",
"ROCAM GAM",
"ROCAM BTM/COE",
"ROCAM Companhia 2º BPM (Botafogo)",

# GCMs – Motopatrulhamento / ROMU
"GCM São Paulo", "GCM Rio de Janeiro", "GCM Santo André", "GCM São Caetano do Sul", "GCM Guarulhos", 
"GCM Campinas", "GCM Osasco", "GCM Diadema", "GCM Mauá", "GCM Ribeirão Pires", "GCM Rio Grande da Serra",

# PCESP – Delegacias e Departamentos
"PCESP", "GARRA", "GER", "GOE", "DEIC", "DHPP", "DIG", "DISE", "Delegacia da Mulher (DDM)", "Delegacia do Idoso", "Delegacia do Meio Ambiente"

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime
from typing import List

# --- CONFIGURAÇÃO DE DADOS ---
DATA_FILE = "boletim_canais.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        canal_boletim_dict = data.get("boletim", {})
else:
    canal_boletim_dict = {}

def salvar_dados():
    """Salva o dicionário de canais no arquivo JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump({"boletim": canal_boletim_dict}, f, indent=4)

# --- ESTRUTURA DE DADOS DAS UNIDADES ---
UNIDADES_POR_CATEGORIA = {
    "PMESP": {
        "Batalhões": [
            "1BPM", "3BPM", "5BPM", "11BPM", "16BPM", "18BPM", "23BPM", "28BPM", "39BPM"
        ],
        "RPMs": [
            "1RPM", "3RPM", "5RPM", "11RPM", "16RPM", "18RPM", "23RPM", "28RPM", "39RPM"
        ],
        "ROCAM das Especializadas": [
            "ROCAM BAEP", "ROCAM ROTA", "ROCAM Força Tática", "ROCAM CAEP", "ROCAM CPTran",
            "ROCAM CavPM", "ROCAM COE", "ROCAM GATE", "ROCAM BPTran", "ROCAM BPRv", "ROCAM BPChq"
        ]
    },
    "PMERJ": {
        "Batalhões": [
            "1BPM-RJ", "2BPM-RJ", "3BPM-RJ", "4BPM-RJ", "5BPM-RJ", "6BPM-RJ", "7BPM-RJ", "8BPM-RJ",
            "9BPM-RJ", "10BPM-RJ", "11BPM-RJ", "12BPM-RJ", "13BPM-RJ", "14BPM-RJ", "15BPM-RJ", "16BPM-RJ",
            "17BPM-RJ", "18BPM-RJ", "19BPM-RJ", "20BPM-RJ"
        ],
        "RPMs": [
            "1RPM-RJ", "2RPM-RJ", "3RPM-RJ", "4RPM-RJ", "5RPM-RJ", "6RPM-RJ", "7RPM-RJ", "8RPM-RJ",
            "9RPM-RJ", "10RPM-RJ", "11RPM-RJ", "12RPM-RJ", "13RPM-RJ", "14RPM-RJ", "15RPM-RJ", "16RPM-RJ",
            "17RPM-RJ", "18RPM-RJ", "19RPM-RJ", "20RPM-RJ"
        ],
        "ROCAM das Especializadas": [
            "ROCAM BOPE", "ROCAM BPChoque-RJ", "ROCAM BPRv-RJ", "ROCAM BPGE", "ROCAM BAC",
            "ROCAM BPMERJ Ambiental", "ROCAM UPP", "ROCAM GAM", "ROCAM BTM/COE",
            "ROCAM Companhia 2º BPM (Botafogo)"
        ]
    },
    "GCMs": {
        "Motopatrulhamento / ROMU": [
            "GCM São Paulo", "GCM Rio de Janeiro", "GCM Santo André", "GCM São Caetano do Sul",
            "GCM Guarulhos", "GCM Campinas", "GCM Osasco", "GCM Diadema", "GCM Mauá",
            "GCM Ribeirão Pires", "GCM Rio Grande da Serra"
        ]
    },
    "PCESP": {
        "Delegacias e Departamentos": [
            "PCESP", "GARRA", "GER", "GOE", "DEIC", "DHPP", "DIG", "DISE",
            "Delegacia da Mulher (DDM)", "Delegacia do Idoso", "Delegacia do Meio Ambiente"
        ]
    },
    "Geral": {
        "Boletim Geral": ["Geral"]
    }
}

TODAS_UNIDADES = []
for org, sub_cats in UNIDADES_POR_CATEGORIA.items():
    for sub_cat, units in sub_cats.items():
        TODAS_UNIDADES.extend(units)
TODAS_UNIDADES = sorted(list(set(TODAS_UNIDADES)))


# --- MODAL (Formulário do Boletim) ---
class BoletimModal(discord.ui.Modal):
    def __init__(self, unidade: str, solicitante: discord.Member):
        super().__init__(title=f"Boletim Diário - {unidade}")
        self.unidade = unidade
        self.solicitante = solicitante
        self.servicos = discord.ui.TextInput(label="1ª PARTE – Serviços Diários", style=discord.TextStyle.paragraph, placeholder="Ex: Administrativo, Operacional...", required=True)
        self.instrucoes = discord.ui.TextInput(label="2ª PARTE – Instruções e Operações", style=discord.TextStyle.paragraph, placeholder="Ex: Integração, Exoneração...", required=True)
        self.assuntos = discord.ui.TextInput(label="3ª PARTE – Assuntos Gerais e Administrativos", style=discord.TextStyle.paragraph, placeholder="Ex: Eventos, reuniões...", required=True)
        self.justica = discord.ui.TextInput(label="4ª PARTE – Justiça e Disciplina", style=discord.TextStyle.paragraph, placeholder="Ex: Publique-se, Cumpra-se...", required=True)
        self.fotos = discord.ui.TextInput(label="Links das fotos (separe por vírgula)", style=discord.TextStyle.paragraph, placeholder="Cole os links das fotos aqui.", required=False)
        self.add_item(self.servicos); self.add_item(self.instrucoes); self.add_item(self.assuntos); self.add_item(self.justica); self.add_item(self.fotos)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        key = f"{guild_id}_{self.unidade}"
        canal_id = canal_boletim_dict.get(key)
        
        if not canal_id:
            await interaction.followup.send(f"❌ O canal de boletim para a unidade **{self.unidade}** não foi configurado!", ephemeral=True)
            return
            
        canal = interaction.guild.get_channel(canal_id)
        if not canal:
            await interaction.followup.send("❌ O canal configurado não foi encontrado!", ephemeral=True)
            return
        
        numero = 1
        data_atual = datetime.now().strftime("%d de %B de %Y")
        titulo_embed = f"BOLETIM Nº{numero}/2025" if self.unidade.lower() != "geral" else "BOLETIM GERAL"
        
        embed = discord.Embed(
            title=f"**{titulo_embed}**",
            description=f"**Unidade:** `{self.unidade}`\n**Data:** `{data_atual}`",
            color=0x1f8b4c
        )
        
        embed.set_author(name=f"Emitido por {self.solicitante.display_name}", icon_url=self.solicitante.display_avatar.url)
        
        # --- CORREÇÃO AQUI ---
        # Adiciona a foto do bot no canto superior direito do embed (thumbnail)
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        embed.add_field(name="📜 **1ª PARTE – SERVIÇOS DIÁRIOS**", value=self.servicos.value, inline=False)
        embed.add_field(name="📚 **2ª PARTE – INSTRUÇÃO E OPERAÇÕES**", value=self.instrucoes.value, inline=False)
        embed.add_field(name="📋 **3ª PARTE – ASSUNTOS GERAIS E ADMINISTRATIVOS**", value=self.assuntos.value, inline=False)
        embed.add_field(name="⚖️ **4ª PARTE – JUSTIÇA E DISCIPLINA**", value=self.justica.value, inline=False)
        
        if self.fotos.value:
            links_fotos = [link.strip() for link in self.fotos.value.split(',') if link.strip()]
            if links_fotos:
                embed.set_image(url=links_fotos[0])
        
        embed.set_footer(
            text=f"Sistema de Boletins - {interaction.client.user.display_name}",
            icon_url=interaction.client.user.display_avatar.url
        )
        
        await canal.send(content="@here", embed=embed)
        await interaction.followup.send(f"✅ Boletim da unidade **{self.unidade}** enviado com sucesso em {canal.mention}!", ephemeral=True)


# --- VIEWS PARA EMISSÃO DE BOLETIM ---
class UnidadeSelect(discord.ui.Select):
    def __init__(self, placeholder: str, unidades: list):
        options = [discord.SelectOption(label=unidade, description=f"Emitir boletim para {unidade}") for unidade in unidades]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BoletimModal(unidade=self.values[0], solicitante=interaction.user))

class UnidadeSelectView(discord.ui.View):
    def __init__(self, organizacao: str):
        super().__init__(timeout=180)
        for nome_sub_cat, unidades in UNIDADES_POR_CATEGORIA[organizacao].items():
            self.add_item(UnidadeSelect(placeholder=nome_sub_cat, unidades=unidades))

class OrganizacaoSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.children[0].options=[discord.SelectOption(label=org) for org in UNIDADES_POR_CATEGORIA.keys()]
    @discord.ui.select(placeholder="Passo 1: Selecione a organização...")
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        org_selecionada = select.values[0]
        await interaction.response.edit_message(content=f"**Passo 2:** Agora, selecione a unidade de **{org_selecionada}**:", view=UnidadeSelectView(org_selecionada))

class PainelBoletimView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Emitir Boletim", style=discord.ButtonStyle.primary, custom_id="emitir_boletim_button_v2")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Iniciando emissão de boletim...", view=OrganizacaoSelectView(), ephemeral=True)

# --- VIEWS PARA /setboletimcanal ---
class SetCanalUnidadeSelect(discord.ui.Select):
    def __init__(self, placeholder: str, unidades: list, canal_destino: discord.TextChannel):
        self.canal_destino = canal_destino
        options = [discord.SelectOption(label=unidade) for unidade in unidades]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        unidade_selecionada = self.values[0]; guild_id = str(interaction.guild.id)
        canal_boletim_dict[f"{guild_id}_{unidade_selecionada}"] = self.canal_destino.id
        salvar_dados()
        await interaction.response.edit_message(content=f"✅ Canal da unidade **{unidade_selecionada}** definido para {self.canal_destino.mention}.", view=None)

class SetCanalUnidadeView(discord.ui.View):
    def __init__(self, canal_destino: discord.TextChannel, organizacao: str):
        super().__init__(timeout=180)
        for nome_sub_cat, unidades in UNIDADES_POR_CATEGORIA[organizacao].items():
            self.add_item(SetCanalUnidadeSelect(placeholder=nome_sub_cat, unidades=unidades, canal_destino=canal_destino))

class SetCanalOrganizacaoView(discord.ui.View):
    def __init__(self, canal_destino: discord.TextChannel):
        super().__init__(timeout=180)
        self.canal_destino = canal_destino
        options = [discord.SelectOption(label=org) for org in UNIDADES_POR_CATEGORIA.keys()]
        options.insert(0, discord.SelectOption(label="TODAS AS UNIDADES", value="TODOS", description="Configurar o mesmo canal para todas."))
        self.children[0].options = options
    @discord.ui.select(placeholder="Passo 1: Selecione o grupo de unidades...")
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        selecao = select.values[0]; guild_id = str(interaction.guild.id)
        if selecao == "TODOS":
            for u in TODAS_UNIDADES: canal_boletim_dict[f"{guild_id}_{u}"] = self.canal_destino.id
            salvar_dados()
            await interaction.response.edit_message(content=f"✅ Canal para **TODAS** as unidades definido para {self.canal_destino.mention}.", view=None)
        else:
            await interaction.response.edit_message(content=f"**Passo 2:** Selecione a unidade de **{selecao}**:", view=SetCanalUnidadeView(canal_destino=self.canal_destino, organizacao=selecao))


# --- COG (Comandos do Bot) ---
class Boletim(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(PainelBoletimView())

    @app_commands.command(name="setboletim", description="Cria o painel interativo para emissão de boletins.")
    @app_commands.describe(canal="O canal onde o painel será criado.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setboletim(self, interaction: discord.Interaction, canal: discord.TextChannel):
        embed = discord.Embed(
            title="📜 Painel de Emissão de Boletins",
            description=(
                "Clique no botão abaixo para dar início à emissão de um novo boletim. "
                "Você poderá registrar todas as informações necessárias de forma organizada e eficiente."
                "\n\nRelatórios e boletins são essenciais para a organização da corporação. 📈"
            ),
            color=0x2ecc71 # Verde para indicar uma ação positiva
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await canal.send(embed=embed, view=PainelBoletimView())
        await interaction.response.send_message(f"✅ Painel de boletins criado com sucesso em {canal.mention}.", ephemeral=True)

    @app_commands.command(name="setboletimcanal", description="Define o canal de envio dos boletins usando um menu interativo.")
    @app_commands.describe(canal="O canal de texto para onde os boletins serão enviados.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setboletimcanal(self, interaction: discord.Interaction, canal: discord.TextChannel):
        await interaction.response.send_message(
            "Iniciando a configuração de canais. Use o menu abaixo para selecionar os canais de destino para cada organização.", 
            view=SetCanalOrganizacaoView(canal_destino=canal), ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Boletim(bot))