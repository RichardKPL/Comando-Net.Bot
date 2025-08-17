import discord
from discord.ext import commands
from discord import app_commands

# --- Constantes de Estilo e Cores ---
EMBED_COLOR_MAIN = discord.Color.from_rgb(52, 152, 219)  # Azul vibrante
EMBED_COLOR_TUTORIAL = discord.Color.from_rgb(46, 204, 113)  # Verde para tutoriais
EMBED_COLOR_BACK = discord.Color.from_rgb(231, 76, 60) # Vermelho para o botão voltar

# --- Conteúdo dos Tutoriais com nova estrutura ---
TUTORIAIS = {
    "lideranca": {
        "title": "👑 Comandos de Liderança",
        "label": "Liderança",
        "emoji": "👑",
        "description": "Comandos de configuração e gestão, exclusivos para a liderança.",
        "guides": {
            "boletim": {
                "title": "📝 Guia de Boletins",
                "emoji": "📝",
                "description": "Guarde registros de atividades e incidentes de forma organizada e eficiente.",
                "fields": [
                    {
                        "name": "👤 Para a Liderança",
                        "value": "• **`/setboletim`**: Cria o painel com o botão de boletim. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/setboletimcanal`**: Define onde os boletins serão enviados. (Permissão: **Gerenciar Canais**)",
                        "inline": False
                    },
                    {
                        "name": "👥 Para a Equipe",
                        "value": "• Clique no botão '📝 Novo Boletim' no painel para preencher o formulário.",
                        "inline": False
                    }
                ]
            },
            "transferencia": {
                "title": "✈️ Guia de Transferências",
                "emoji": "✈️",
                "description": "Sistema para solicitar e gerenciar transferências entre guarnições de forma rápida e segura.",
                "fields": [
                    {
                        "name": "👤 Para a Liderança",
                        "value": "• **`/settransferencia`**: Envia embed público para solicitar transferência. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/settransferenciaap`**: Define o canal de aprovação de transferências. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/setadmintransferencia`**: Define os cargos de aprovação de transferência. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/transferenciacargos`**: Define os cargos para transferência. (Permissão: **Gerenciar Canais**)",
                        "inline": False
                    }
                ]
            },
            "funcional": {
                "title": "🎖️ Guia de Funcionais e Cargos",
                "emoji": "🎖️",
                "description": "Automatize a troca de cargos e apelidos para evitar erros e otimizar a gestão.",
                "fields": [
                    {
                        "name": "👤 Para a Liderança",
                        "value": "• **`/setfuncional`**: Envia embed público para solicitar funcional. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/setfuncionalap`**: Define o canal de aprovação. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/funcionalcargos`**: Define cargos disponíveis. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/setfuncionaladmin`**: Define cargos que podem aprovar/reprovar funcionais. (Permissão: **Gerenciar Canais**)",
                        "inline": False
                    }
                ]
            },
            "ausencia": {
                "title": "📌 Guia de Ausências",
                "emoji": "📌",
                "description": "Comunique à liderança seus períodos de ausência de forma oficial para evitar problemas.",
                "fields": [
                    {
                        "name": "👤 Para a Liderança",
                        "value": "• **`/setausencia`**: Cria um painel público de ausências. (Permissão: **Gerenciar Canais**)\n"
                                 "• **`/setausenciacanal`**: Define o canal onde as ausências serão enviadas. (Permissão: **Gerenciar Canais**)",
                        "inline": False
                    }
                ]
            },
            "config": {
                "title": "⚙️ Guia de Configurações Gerais",
                "emoji": "⚙️",
                "description": "Comandos administrativos para a configuração geral do bot.",
                "fields": [
                    {
                        "name": "🛠️ Comandos disponíveis",
                        "value": "• **`/setcargos`**: Adiciona ou remove múltiplos cargos de um usuário. (Permissão: **Gerenciar Cargos**)\n"
                                 "• **`/setbopm`**: Envia o painel de BO PM para o canal selecionado. (Permissão: **Gerenciar Canais**)",
                        "inline": False
                    }
                ]
            }
        }
    },
    "operacionais": {
        "title": "📋 Comandos Operacionais",
        "label": "Operacionais",
        "emoji": "📋",
        "description": "Comandos de uso diário para a equipe. Facilitam o registro de atividades e a comunicação.",
        "guides": {
            "relatorios": {
                "title": "📋 Guia de Relatórios de Serviço",
                "emoji": "📋",
                "description": "Documente suas atividades em serviço de forma rápida e intuitiva.",
                "fields": [
                    {
                        "name": "⚙️ Comandos de Relatório",
                        "value": "• **`/rso`**: Abre o painel para iniciar um novo Relatório de Serviço Operacional.\n"
                                 "• **`/bopm`**: Relatório para Boletim de Ocorrência da PM.",
                        "inline": False
                    }
                ]
            },
            "ausencia": {
                "title": "📌 Guia de Ausências",
                "emoji": "📌",
                "description": "Comunique à liderança seus períodos de ausência de forma oficial.",
                "fields": [
                    {
                        "name": "👥 Para a Equipe",
                        "value": "• Use o comando `/ausencia` para registrar sua ausência.",
                        "inline": False
                    }
                ]
            }
        }
    },
    "gerais": {
        "title": "💡 Comandos Gerais",
        "label": "Gerais",
        "emoji": "💡",
        "description": "Comandos básicos e informativos, disponíveis para todos os membros do servidor.",
        "guides": {
            "info_status": {
                "title": "💡 Guia de Informações do Bot",
                "emoji": "💡",
                "description": "Informações gerais sobre o bot e seu status.",
                "fields": [
                    {
                        "name": "🛠️ Comandos Disponíveis",
                        "value": "• **`/ajuda`**: Exibe este menu interativo.\n"
                                 "• **`/info`**: Apresenta um resumo sobre mim e meu desenvolvedor.\n"
                                 "• **`/status`**: Mostra informações e o status atual do bot.",
                        "inline": False
                    }
                ]
            }
        }
    }
}

# --- Views de interação ---
class TutorialSelect(discord.ui.Select):
    def __init__(self, cog: "Ajuda", category_key: str):
        self.cog = cog
        self.category_key = category_key
        options = []
        guides = TUTORIAIS[category_key]["guides"]
        for key, data in guides.items():
            options.append(discord.SelectOption(label=data['title'], emoji=data['emoji'], value=key))
        
        super().__init__(
            placeholder=f"Selecione um guia de {TUTORIAIS[category_key]['label']}...",
            options=options,
            custom_id=f"select_tutorial_{category_key}"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_guide_key = self.values[0]
        await self.cog.show_tutorial(interaction, self.category_key, selected_guide_key)

class CategoryView(discord.ui.View):
    def __init__(self, cog: "Ajuda"):
        super().__init__(timeout=None)
        self.cog = cog
        self.add_buttons()

    def add_buttons(self):
        for i, (key, data) in enumerate(TUTORIAIS.items()):
            button_style = discord.ButtonStyle.primary if key == "lideranca" else discord.ButtonStyle.secondary
            button = discord.ui.Button(
                label=data['label'], 
                style=button_style,
                emoji=data['emoji'],
                custom_id=f"ajuda_category_{key}",
                row=0
            )
            self.add_item(button)

    @discord.ui.button(label="Tutorial Específico", style=discord.ButtonStyle.secondary, emoji="📚", custom_id="ajuda_select_menu", row=1)
    async def select_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.show_select_menu(interaction)

    async def interaction_check(self, interaction: discord.Interaction):
        if "ajuda_category_" in interaction.data['custom_id']:
            category_key = interaction.data['custom_id'].split('_')[-1]
            await self.cog.show_tutorial_list(interaction, category_key)
            return False
        return True

class TutorialView(discord.ui.View):
    def __init__(self, cog: "Ajuda", category_key: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.add_item(TutorialSelect(cog, category_key))
    
    @discord.ui.button(label="🔙 Voltar às Categorias", style=discord.ButtonStyle.danger, custom_id="ajuda_back_to_categories")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.show_main_menu(interaction, edit=True)

class AjudaBackView(discord.ui.View):
    def __init__(self, cog: "Ajuda", category_key: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.category_key = category_key

    @discord.ui.button(label="🔙 Voltar aos Guias", style=discord.ButtonStyle.danger, custom_id="ajuda_back_to_guides")
    async def back_to_guides_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.show_tutorial_list(interaction, self.category_key, edit=True)

# --- Cog Principal ---
class Ajuda(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def _create_main_embed(self, interaction: discord.Interaction) -> discord.Embed:
        embed = discord.Embed(
            title="📚 Central de Ajuda do Bot 🤖",
            description=(
                "Olá! Eu sou seu assistente de gestão de corporação. "
                "Aqui, você encontra guias rápidos sobre como usar meus comandos e formulários. "
                "**Basta clicar em uma das categorias abaixo para começar!** 🚀"
            ),
            color=EMBED_COLOR_MAIN
        )
        embed.set_author(
            name=f"Desenvolvido por Richard Kaua",
            icon_url=self.bot.user.display_avatar.url
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Tutorial solicitado por {interaction.user.display_name} | Use o comando /info para me conhecer melhor.",
            icon_url=interaction.user.display_avatar.url
        )
        return embed

    def _create_tutorial_embed(self, interaction: discord.Interaction, category_key: str, guide_key: str) -> discord.Embed:
        category_data = TUTORIAIS.get(category_key)
        if not category_data:
            return discord.Embed(
                title="❌ Erro",
                description="A categoria de tutorial não foi encontrada.",
                color=discord.Color.red()
            )
        
        guide_data = category_data["guides"].get(guide_key)
        if not guide_data:
            return discord.Embed(
                title="❌ Erro",
                description="O tutorial solicitado não foi encontrado.",
                color=discord.Color.red()
            )
        
        embed = discord.Embed(
            title=guide_data['title'],
            description=guide_data['description'],
            color=EMBED_COLOR_TUTORIAL
        )
        
        for field in guide_data['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
            
        embed.set_footer(
            text=f"Tutorial solicitado por {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )
        return embed

    async def show_main_menu(self, interaction: discord.Interaction, edit: bool = False):
        embed = self._create_main_embed(interaction)
        view = CategoryView(self)
        
        if edit and interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=view)
        elif edit:
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def show_tutorial_list(self, interaction: discord.Interaction, category_key: str, edit: bool = False):
        category_data = TUTORIAIS[category_key]
        embed = discord.Embed(
            title=f"{category_data['emoji']} Guias de {category_data['label']}",
            description=f"Selecione um guia na lista suspensa abaixo para ver os detalhes sobre os comandos de {category_data['label'].lower()}.",
            color=EMBED_COLOR_TUTORIAL
        )
        embed.set_footer(
            text=f"Tutorial solicitado por {interaction.user.display_name}", 
            icon_url=interaction.user.display_avatar.url
        )
        view = TutorialView(self, category_key)
        if edit:
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def show_tutorial(self, interaction: discord.Interaction, category_key: str, guide_key: str):
        embed = self._create_tutorial_embed(interaction, category_key, guide_key)
        view = AjudaBackView(self, category_key)
        await interaction.response.edit_message(embed=embed, view=view)

    @app_commands.command(name="ajuda", description="Exibe um menu interativo com os guias de uso do bot.")
    async def ajuda(self, interaction: discord.Interaction):
        await self.show_main_menu(interaction)

    # --- Setup da extensão ---
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CategoryView(self))
        self.bot.add_view(TutorialView(self, "lideranca"))
        self.bot.add_view(TutorialView(self, "operacionais"))
        self.bot.add_view(TutorialView(self, "gerais"))
        self.bot.add_view(AjudaBackView(self, "lideranca"))
        self.bot.add_view(AjudaBackView(self, "operacionais"))
        self.bot.add_view(AjudaBackView(self, "gerais"))

# --- Setup da extensão ---
async def setup(bot: commands.Bot):
    cog = Ajuda(bot)
    await bot.add_cog(cog)