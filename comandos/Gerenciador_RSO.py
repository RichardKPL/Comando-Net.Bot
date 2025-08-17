import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime

# --- Estrutura de dados e configurações dinâmicas dos formulários ---
FORMULARIO_ETAPA1 = {
    "PMESP Padrão": {
        "title": "📋 RSO PMESP Padrão | Equipe Operacional",
        "fields": {
            "viatura": {"label": "🚓 Viatura", "required": True, "max_length": 15, "placeholder": "Ex: VTR I-12345"},
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "motorista": {"label": "🧑‍✈️ Motorista", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "homem3": {"label": "👮‍♂️ 3º Homem", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. João"},
            "homem4": {"label": "👮‍♂️ 4º Homem", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. Matheus"}
        }
    },
    "PMESP ROCAM": {
        "title": "🏍️ RSO PMESP ROCAM | Equipe Operacional",
        "fields": {
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "rocam2": {"label": "🏍️ 2º ROCAM", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "rocam3": {"label": "🏍️ 3º ROCAM", "required": False, "max_length": 50, "placeholder": "Opcional: Sd. João"}
        }
    },
    "PMESP RPMs": {
        "title": "🏍️ RSO PMESP RPMs | Equipe Operacional",
        "fields": {
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "rocam2": {"label": "🏍️ 2º RPM", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "rocam3": {"label": "🏍️ 3º RPM", "required": False, "max_length": 50, "placeholder": "Opcional: Sd. João"}
        }
    },
    "PMESP Especializadas": {
        "title": "⭐ RSO PMESP Especializadas | Equipe Operacional",
        "fields": {
            "viatura": {"label": "🚓 Viatura", "required": True, "max_length": 15, "placeholder": "Ex: VTR ROTA-01"},
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "motorista": {"label": "🧑‍✈️ Motorista", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "homem3": {"label": "👮‍♂️ 3º Homem", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. João"},
            "homem4": {"label": "👮‍♂️ 4º Homem", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. Matheus"}
        }
    },
    "PMERJ Batalhões": {
        "title": "📋 RSO PMERJ Batalhões | Equipe Operacional",
        "fields": {
            "viatura": {"label": "🚔 Viatura", "required": True, "max_length": 15, "placeholder": "Ex: VTR RJ-12345"},
            "comandante": {"label": "👨‍✈️ Comandante", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "auxiliar": {"label": "🧑‍✈️ Auxiliar", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "auxiliar2": {"label": "👮‍♂️ 3º Homem", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. João"},
            "auxiliar3": {"label": "👮‍♂️ 4º Homem", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. Matheus"}
        }
    },
    "PMERJ RPMs": {
        "title": "🏍️ RSO PMERJ RPMs | Equipe Operacional",
        "fields": {
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "rocam2": {"label": "🏍️ 2º RPM", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "rocam3": {"label": "🏍️ 3º RPM", "required": False, "max_length": 50, "placeholder": "Opcional: Sd. João"}
        }
    },
    "PMERJ ROCAM": {
        "title": "🏍️ RSO PMERJ ROCAM | Equipe Operacional",
        "fields": {
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "rocam2": {"label": "🏍️ 2º ROCAM", "required": True, "max_length": 50, "placeholder": "Ex: Sd. Kaua"},
            "rocam3": {"label": "🏍️ 3º ROCAM", "required": False, "max_length": 50, "placeholder": "Opcional: Sd. João"}
        }
    },
    "GCM Padrão": {
        "title": "📋 RSO GCM Padrão | Equipe Operacional",
        "fields": {
            "viatura": {"label": "🚓 Viatura", "required": True, "max_length": 15, "placeholder": "Ex: VTR GCM-12345"},
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "motorista": {"label": "🧑‍✈️ Motorista", "required": True, "max_length": 50, "placeholder": "Ex: GCM. Kaua"},
            "guarda3": {"label": "👮‍♂️ 3º Guarda", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: GCM. João"},
            "guarda4": {"label": "👮‍♂️ 4º Guarda", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: GCM. Matheus"}
        }
    },
    "GCM ROMU": {
        "title": "🛡️ RSO GCM ROMU | Equipe Operacional",
        "fields": {
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "guarda2": {"label": "👮‍♂️ 2º Guarda", "required": True, "max_length": 50, "placeholder": "Ex: GCM. Kaua"},
            "guarda3": {"label": "👮‍♂️ 3º Guarda", "required": False, "max_length": 50, "placeholder": "Opcional: GCM. João"}
        }
    },
    "PCESP Delegacias e Departamentos": {
        "title": "🕵️ RSO PCESP | Equipe Operacional",
        "fields": {
            "viatura": {"label": "🚔 Viatura", "required": False, "max_length": 15, "placeholder": "Ex: VTR P-12345 (Opcional)"},
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "motorista": {"label": "🧑‍✈️ Motorista", "required": True, "max_length": 50, "placeholder": "Ex: GCM. Kaua"},
            "agente3": {"label": "👮‍♂️ 3º Agente", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. João"},
            "agente4": {"label": "👮‍♂️ 4º Agente", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. Matheus"}
        }
    },
    "PCERJ Delegacias e Departamentos": {
        "title": "🕵️ RSO PCERJ | Equipe Operacional",
        "fields": {
            "viatura": {"label": "🚔 Viatura", "required": False, "max_length": 15, "placeholder": "Ex: VTR P-12345 (Opcional)"},
            "encarregado": {"label": "👨‍✈️ Encarregado", "required": True, "max_length": 50, "placeholder": "Ex: Cb. Richard"},
            "motorista": {"label": "🧑‍✈️ Motorista", "required": True, "max_length": 50, "placeholder": "Ex: GCM. Kaua"},
            "agente3": {"label": "👮‍♂️ 3º Agente", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. João"},
            "agente4": {"label": "👮‍♂️ 4º Agente", "required": False, "max_length": 50, "placeholder": "Opcional: Ex: Sd. Matheus"}
        }
    }
}

FORMULARIO_ETAPA2 = {
    "title": "📋 Relato da Ocorrência",
    "fields": {
        "prisoes": {"label": "⚖️ Prisões", "required": False, "max_length": 100, "placeholder": "Descreva as prisões, se houver", "default": "Editar antes de finalizar RSO."},
        "apreensoes": {"label": "📦 Apreensões", "required": False, "max_length": 200, "placeholder": "Descreva as apreensões, se houver", "default": "Editar antes de finalizar RSO."},
        "observacoes": {"label": "📝 Observações", "required": False, "style": discord.TextStyle.paragraph, "max_length": 1000, "placeholder": "Informações adicionais da ocorrência", "default": "Ex: O indivíduo tentou fugir, mas foi contido pela equipe.", "default": "Editar antes de finalizar RSO."}
    }
}

# --- Estrutura de dados das unidades de RSO ---
UNIDADES_RSO_POR_CATEGORIA = {
    "PMESP": {
        "PMESP Padrão": [
            "1BPM", "3BPM", "5BPM", "11BPM", "16BPM", "18BPM", "23BPM", "28BPM", "39BPM",
        ],
        "PMESP RPMs": [
            "1RPM", "3RPM", "5RPM", "11RPM", "16RPM", "18RPM", "23RPM", "28RPM", "39RPM"
        ],
        "PMESP ROCAM": [
            "ROCAM BAEP", "ROCAM Força Tática", "ROCAM CAEP", "ROCAM CPTran", "ROCAM COE", "ROCAM GATE", "ROCAM BPTran", "ROCAM BPRv", "ROCAM BPChq"
        ],
        "PMESP Especializadas": [
            "ROTA", "BAEP", "Força Tática", "CAVPM"
        ]
    },
    "PMERJ": {
        "PMERJ Batalhões": [
            "1BPM-RJ", "2BPM-RJ", "3BPM-RJ", "4BPM-RJ", "5BPM-RJ", "6BPM-RJ", "7BPM-RJ", "8BPM-RJ",
            "9BPM-RJ", "10BPM-RJ", "11BPM-RJ", "12BPM-RJ", "13BPM-RJ", "14BPM-RJ", "15BPM-RJ", "16BPM-RJ",
            "17BPM-RJ", "18BPM-RJ", "19BPM-RJ", "20BPM-RJ"
        ],
        "PMERJ RPMs": [
            "1RPM-RJ", "2RPM-RJ", "3RPM-RJ", "4RPM-RJ", "5RPM-RJ", "6RPM-RJ", "7RPM-RJ", "8RPM-RJ",
            "9RPM-RJ", "10RPM-RJ", "11RPM-RJ", "12RPM-RJ", "13RPM-RJ", "14RPM-RJ", "15RPM-RJ", "16RPM-RJ",
            "17RPM-RJ", "18RPM-RJ", "19RPM-RJ", "20RPM-RJ"
        ],
        "PMERJ ROCAM": [
            "ROCAM BOPE", "ROCAM BPChoque-RJ", "ROCAM BPRv-RJ", "ROCAM BPGE", "ROCAM BAC",
            "ROCAM BPMERJ Ambiental", "ROCAM UPP", "ROCAM GAM", "ROCAM BTM/COE",
            "ROCAM Companhia 2º BPM (Botafogo)"
        ]
    },
    "GCM": {
        "GCM Padrão": [
            "GCM São Paulo", "GCM Rio de Janeiro", "GCM Santo André", "GCM São Caetano do Sul",
            "GCM Guarulhos", "GCM Campinas", "GCM Osasco", "GCM Diadema", "GCM Mauá",
            "GCM Ribeirão Pires", "GCM Rio Grande da Serra"
        ],
        "GCM ROMU": [
            "ROMU GCM São Paulo", "ROMU GCM Rio de Janeiro", "ROMU GCM Santo André", "ROMU GCM Guarulhos",
            "ROMU GCM Campinas", "ROMU GCM Diadema"
        ]
    },
    "PCESP": {
        "PCESP Delegacias e Departamentos": [
            "PCESP", "GARRA", "GER", "GOE", "DEIC", "DHPP", "DIG", "DISE", "Delegacia da Mulher (DDM)", "Delegacia do Idoso", "Delegacia do Meio Ambiente"
        ]
    },
    "PCERJ": {
        "PCERJ Delegacias e Departamentos": [
            "PCERJ", "DECAP", "DEAM", "DH", "DRE", "DRF", "DRIVE", "Delegacia da Criança", "Delegacia da Terceira Idade", "Delegacia do Meio Ambiente"
        ]
    }
}


# --- Modals (Formulários) Refatorados ---
class RSOFormularioEtapa1(discord.ui.Modal):
    def __init__(self, author, unidade, tipo_relatorio, organizacao):
        self.author = author
        self.unidade = unidade
        self.tipo_relatorio = tipo_relatorio
        self.organizacao = organizacao
        
        # Carrega a configuração do formulário
        config = FORMULARIO_ETAPA1.get(self.tipo_relatorio)
        super().__init__(title=config['title'])

        self.form_fields = {}
        for key, field_data in config['fields'].items():
            text_input = discord.ui.TextInput(
                label=field_data['label'],
                required=field_data['required'],
                max_length=field_data['max_length'] if 'max_length' in field_data else None,
                placeholder=field_data['placeholder']
            )
            setattr(self, key, text_input)
            self.add_item(text_input)
            self.form_fields[key] = text_input

    async def on_submit(self, interaction: discord.Interaction):
        dados = {
            "unidade": self.unidade,
            "tipo_relatorio": self.tipo_relatorio,
            "organizacao": self.organizacao
        }
        for key, text_input in self.form_fields.items():
            dados[key] = text_input.value or "Não informado"
        
        # Lógica para enviar o próximo formulário ou finalizar
        await interaction.response.send_message(
            "✅ Etapa 1 completa! Clique no botão para continuar para a próxima etapa.",
            ephemeral=True,
            view=ContinuarButtonEtapa2(interaction.channel.id, interaction.user.id, dados)
        )

class RSOFormularioEtapa2(discord.ui.Modal):
    def __init__(self, author_id, dados):
        super().__init__(title=FORMULARIO_ETAPA2['title'])
        self.author_id = author_id
        self.dados = dados
        self.form_fields = {}

        for key, field_data in FORMULARIO_ETAPA2['fields'].items():
            text_input = discord.ui.TextInput(
                label=field_data['label'],
                required=field_data['required'],
                max_length=field_data.get('max_length'),
                placeholder=field_data.get('placeholder'),
                style=field_data.get('style', discord.TextStyle.short),
                default=field_data.get('default')
            )
            setattr(self, key, text_input)
            self.add_item(text_input)
            self.form_fields[key] = text_input

    async def on_submit(self, interaction: discord.Interaction):
        for key, text_input in self.form_fields.items():
            self.dados[key] = text_input.value or "Nenhum"
        
        await interaction.response.send_message(
            "✅ Etapa 2 completa! Clique no botão para confirmar.",
            ephemeral=True,
            view=ContinuarButtonEtapa3(interaction.channel.id, self.author_id, self.dados)
        )


# --- Views e Botões ---
class RSOStartView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="📝 Iniciar Novo Relatório", style=discord.ButtonStyle.primary, custom_id="rso_start_button")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Selecione a força policial para iniciar o relatório:",
            view=OrganizationSelect(),
            ephemeral=True
        )

class OrganizationSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        options = [
            discord.SelectOption(label="PMESP", description="Polícia Militar do Estado de São Paulo", emoji="🚓"),
            discord.SelectOption(label="PMERJ", description="Polícia Militar do Estado do Rio de Janeiro", emoji="🚔"),
            discord.SelectOption(label="GCM", description="Guarda Civil Metropolitana", emoji="🛡️"),
            discord.SelectOption(label="PCESP", description="Polícia Civil do Estado de São Paulo", emoji="🕵️"),
            discord.SelectOption(label="PCERJ", description="Polícia Civil do Estado do Rio de Janeiro", emoji="🕵️")
        ]
        
        select_menu = discord.ui.Select(
            placeholder="Escolha a organização...",
            options=options,
            custom_id="organization_select_menu"
        )
        select_menu.callback = self.select_callback
        self.add_item(select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]
        unidades = list(UNIDADES_RSO_POR_CATEGORIA[selected_option].keys())
        
        if len(UNIDADES_RSO_POR_CATEGORIA[selected_option]) > 1:
            await interaction.response.edit_message(
                content=f"Selecione o tipo de relatório e a unidade da {selected_option}:",
                view=TipoRSOSelectView(selected_option)
            )
        else:
            await interaction.response.edit_message(
                content=f"Selecione a unidade para o relatório **{unidades[0]}**:",
                view=UnidadeRSOSelectView(unidades[0], selected_option, UNIDADES_RSO_POR_CATEGORIA[selected_option][unidades[0]])
            )
        self.stop()

class TipoRSOSelectView(discord.ui.View):
    def __init__(self, organizacao: str):
        super().__init__(timeout=180)
        self.organizacao = organizacao
        options = [discord.SelectOption(label=tipo, description=UNIDADES_RSO_POR_CATEGORIA[organizacao][tipo][0]) for tipo in UNIDADES_RSO_POR_CATEGORIA[organizacao]]
        
        select_menu = discord.ui.Select(placeholder="Escolha o tipo de relatório...", options=options, custom_id="tipo_rso_select_menu")
        select_menu.callback = self.select_callback
        self.add_item(select_menu)
        
    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.gray, custom_id="back_to_org")
    async def back_to_org_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Selecione a força policial para iniciar o relatório:",
            view=OrganizationSelect()
        )
        self.stop()

    async def select_callback(self, interaction: discord.Interaction):
        selected_option = interaction.data['values'][0]
        unidades = UNIDADES_RSO_POR_CATEGORIA[self.organizacao][selected_option]
        await interaction.response.edit_message(
            content=f"Selecione a unidade para o relatório **{selected_option}**:",
            view=UnidadeRSOSelectView(selected_option, self.organizacao, unidades)
        )
        self.stop()
        
class UnidadeRSOSelectView(discord.ui.View):
    def __init__(self, tipo_relatorio: str, organizacao: str, unidades: list):
        super().__init__(timeout=180)
        self.tipo_relatorio = tipo_relatorio
        self.organizacao = organizacao
        self.unidades = unidades
        
        options = [discord.SelectOption(label=unidade, value=unidade) for unidade in unidades]
        
        select_menu = discord.ui.Select(placeholder="Escolha a unidade...", options=options, custom_id="unidade_rso_select_menu")
        select_menu.callback = self.select_callback
        self.add_item(select_menu)
        
    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.gray, custom_id="back_to_tipo")
    async def back_to_tipo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content=f"Selecione o tipo de relatório e a unidade da {self.organizacao}:",
            view=TipoRSOSelectView(self.organizacao)
        )
        self.stop()

    async def select_callback(self, interaction: discord.Interaction):
        selected_unidade = interaction.data['values'][0]
        await interaction.response.send_modal(RSOFormularioEtapa1(interaction.user, selected_unidade, self.tipo_relatorio, self.organizacao))
        await interaction.message.delete()
        self.stop()

class RSOEditAndView(discord.ui.View):
    def __init__(self, author_id, dados):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.dados = dados
        self.edit_status = self.dados.get('edit_status', {'equipe_edited': False, 'relato_edited': False})
        
    @discord.ui.button(label="📝 Editar RSO", style=discord.ButtonStyle.secondary)
    async def edit_rso(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não tem permissão para editar este RSO.", ephemeral=True)
        
        await interaction.response.send_message(
            "Escolha qual etapa do RSO deseja editar:",
            view=RSOEditSelectionView(self.dados, self.author_id, interaction.message),
            ephemeral=True
        )

    @discord.ui.button(label="🔴 Encerrar RSO", style=discord.ButtonStyle.danger)
    async def end_rso(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não tem permissão para encerrar este RSO.", ephemeral=True)
        
        # Envia a mensagem de confirmação
        await interaction.response.send_message(
            "Tem certeza que deseja encerrar este RSO?",
            view=RSOConfirmationView(self.author_id, self.dados, interaction.message),
            ephemeral=True
        )

class RSOEditSelectionView(discord.ui.View):
    def __init__(self, dados, author_id, message):
        super().__init__(timeout=180)
        self.dados = dados
        self.author_id = author_id
        self.message = message
        self.edit_status = self.dados.get('edit_status', {'equipe_edited': False, 'relato_edited': False})
        
        if self.edit_status.get('equipe_edited'):
            self.edit_equipe_button.disabled = True
        
        if self.edit_status.get('relato_edited'):
            self.edit_relato_button.disabled = True

    @discord.ui.button(label="Editar Equipe", style=discord.ButtonStyle.secondary)
    async def edit_equipe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não tem permissão para editar este RSO.", ephemeral=True)
        if self.edit_status.get('equipe_edited'):
            return await interaction.response.edit_message(content="❌ A equipe já foi editada uma vez.")
        
        await interaction.response.send_modal(RSOEditFormEquipe(self.dados, self.message, interaction.message))

    @discord.ui.button(label="Editar Relato", style=discord.ButtonStyle.secondary)
    async def edit_relato_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não tem permissão para editar este RSO.", ephemeral=True)
        if self.edit_status.get('relato_edited'):
            return await interaction.response.edit_message(content="❌ O relato já foi editado uma vez.")

        await interaction.response.send_modal(RSOEditFormRelato(self.dados, self.message, interaction.message))

class RSOConfirmationView(discord.ui.View):
    def __init__(self, author_id, dados, message):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.dados = dados
        self.message = message

    @discord.ui.button(label="✅ Sim, Encerrar RSO", style=discord.ButtonStyle.green)
    async def confirm_end_rso(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não tem permissão para encerrar este RSO.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        # Registra o horário de fim
        end_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.dados['data_fim'] = end_time

        # Edita o embed original para refletir o encerramento
        embed = self.message.embeds[0]
        embed.color = 0x7f8c8d # Cor cinza para indicar finalizado
        
        # Atualiza o campo de Data Fim
        for i, field in enumerate(embed.fields):
            if field.name == "📅 Fim":
                embed.set_field_at(index=i, name="📅 Fim", value=self.dados['data_fim'], inline=True)
                break

        await self.message.edit(embed=embed, view=None) # view=None remove os botões
        await interaction.followup.send("✅ RSO encerrado com sucesso!", ephemeral=True)
        await interaction.message.delete() # Deleta a mensagem de confirmação

    @discord.ui.button(label="❌ Não, Cancelar", style=discord.ButtonStyle.red)
    async def cancel_end_rso(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Encerramento do RSO cancelado.", ephemeral=True)
        await interaction.message.delete() # Deleta a mensagem de confirmação


# --- Modals de Edição (pré-preenchidos) ---
class RSOEditFormEquipe(discord.ui.Modal, title="✏️ Editar Equipe Operacional"):
    def __init__(self, dados, message, ephemeral_message):
        super().__init__()
        self.dados = dados
        self.message = message
        self.ephemeral_message = ephemeral_message
        
        # Carrega a configuração do formulário de equipe
        config = FORMULARIO_ETAPA1.get(self.dados['tipo_relatorio'])
        for key, field_data in config['fields'].items():
            text_input = discord.ui.TextInput(
                label=field_data['label'],
                required=field_data['required'],
                max_length=field_data['max_length'],
                placeholder=field_data['placeholder'],
                default=self.dados.get(key, field_data.get('default')) or None
            )
            setattr(self, key, text_input)
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        config = FORMULARIO_ETAPA1.get(self.dados['tipo_relatorio'])
        for key in config['fields'].keys():
            self.dados[key] = getattr(self, key).value or "Não informado"
        
        embed = self.message.embeds[0]
        
        # Atualiza os campos do embed
        for key, value in self.dados.items():
            if key in config['fields']:
                for i, field in enumerate(embed.fields):
                    if field.name.startswith(config['fields'][key]['label']):
                        embed.set_field_at(i, name=field.name, value=value, inline=field.inline)
                        break

        # **NOVA LÓGICA:** Marca a edição como usada SOMENTE após o submit
        if 'edit_status' not in self.dados:
            self.dados['edit_status'] = {'equipe_edited': False, 'relato_edited': False}
        self.dados['edit_status']['equipe_edited'] = True
        
        # Atualiza a view do RSO para refletir o novo status
        new_view = RSOEditAndView(self.dados['author_id'], self.dados)
        await self.message.edit(embed=embed, view=new_view)
        
        # Edita a mensagem efêmera para desabilitar o botão
        await self.ephemeral_message.edit(view=RSOEditSelectionView(self.dados, self.dados['author_id'], self.message))
        
        await interaction.followup.send("✅ Equipe editada com sucesso!", ephemeral=True)

class RSOEditFormRelato(discord.ui.Modal, title="✏️ Editar Relato da Ocorrência"):
    def __init__(self, dados, message, ephemeral_message):
        super().__init__()
        self.dados = dados
        self.message = message
        self.ephemeral_message = ephemeral_message

        # Carrega a configuração do formulário de relato
        config = FORMULARIO_ETAPA2['fields']
        for key, field_data in config.items():
            text_input = discord.ui.TextInput(
                label=field_data['label'],
                required=field_data['required'],
                max_length=field_data['max_length'],
                placeholder=field_data['placeholder'],
                default=self.dados.get(key) or None,
                style=field_data.get('style', discord.TextStyle.short)
            )
            setattr(self, key, text_input)
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        config = FORMULARIO_ETAPA2['fields']
        for key in config.keys():
            self.dados[key] = getattr(self, key).value or "Nenhum"
        
        embed = self.message.embeds[0]
        
        # Atualiza os campos do embed
        for key, value in self.dados.items():
            if key in config:
                for i, field in enumerate(embed.fields):
                    if field.name.startswith(config[key]['label']):
                        embed.set_field_at(i, name=field.name, value=value, inline=field.inline)
                        break

        # **NOVA LÓGICA:** Marca a edição como usada SOMENTE após o submit
        if 'edit_status' not in self.dados:
            self.dados['edit_status'] = {'equipe_edited': False, 'relato_edited': False}
        self.dados['edit_status']['relato_edited'] = True

        # Atualiza a view do RSO para refletir o novo status
        new_view = RSOEditAndView(self.dados['author_id'], self.dados)
        await self.message.edit(embed=embed, view=new_view)
        
        # Edita a mensagem efêmera para desabilitar o botão
        await self.ephemeral_message.edit(view=RSOEditSelectionView(self.dados, self.dados['author_id'], self.message))

        await interaction.followup.send("✅ Relato da ocorrência editado com sucesso!", ephemeral=True)


# --- Botões de Continuação (Etapas 2 e 3) ---
class ContinuarButtonEtapa2(discord.ui.View):
    def __init__(self, channel_id, author_id, dados):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.author_id = author_id
        self.dados = dados

    @discord.ui.button(label="Continuar para Etapa 2", style=discord.ButtonStyle.primary)
    async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)
        
        await interaction.response.send_modal(RSOFormularioEtapa2(self.author_id, self.dados))
        await interaction.delete_original_response()

class ContinuarButtonEtapa3(discord.ui.View):
    def __init__(self, channel_id, author_id, dados):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.author_id = author_id
        self.dados = dados

    @discord.ui.button(label="🟢 Confirmar Abertura de RSO", style=discord.ButtonStyle.green)
    async def continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Você não pode usar este botão.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        channel = interaction.guild.get_channel(self.channel_id)
        rso_id = random.randint(1000, 9999)
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        self.dados.update({
            "rso_id": rso_id,
            "data_inicio": current_time,
            "data_fim": "-",
            "author_id": self.author_id,
            "edit_status": {'equipe_edited': False, 'relato_edited': False}
        })

        embed = discord.Embed(
            title=f"{FORMULARIO_ETAPA1[self.dados['tipo_relatorio']]['title'].split('|')[0].strip()} - #{rso_id}",
            color=self.get_embed_color(self.dados['organizacao'])
        )
        embed.set_author(name=f"Assinado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        embed.add_field(name="--- 🚔 Equipe ---", value="", inline=False)
        embed.add_field(name="**Unidade:**", value=self.dados.get('unidade', 'Não informado'), inline=False)
        
        for key, field_data in FORMULARIO_ETAPA1[self.dados['tipo_relatorio']]['fields'].items():
            value = self.dados.get(key, 'Não informado')
            if value and value != "Não informado":
                embed.add_field(name=f"**{field_data['label'].strip(' ')}:**", value=value, inline=True)
        
        embed.add_field(name="---", value="**Relato da Ocorrência**", inline=False)

        for key, field_data in FORMULARIO_ETAPA2['fields'].items():
            value = self.dados.get(key, 'Nenhum')
            embed.add_field(name=field_data['label'], value=value, inline=False)

        embed.add_field(name="---", value="**Datas e Horários**", inline=False)
        embed.add_field(name="📅 Início", value=self.dados['data_inicio'], inline=True)
        embed.add_field(name="📅 Fim", value=self.dados['data_fim'], inline=True)
        embed.set_footer(text=f"RSO registrado por {interaction.client.user.display_name} • {current_time}", icon_url=interaction.client.user.display_avatar.url)
        
        await channel.send(
            content=f"📌 Novo RSO de {self.dados['organizacao']} registrado por {interaction.user.mention}!",
            embed=embed,
            view=RSOEditAndView(self.author_id, self.dados)
        )
        await interaction.delete_original_response()
        self.stop()

    def get_embed_color(self, organizacao):
        colors = {
            "PMESP": 0x3498db, "PMERJ": 0x2980b9,
            "GCM": 0x95a5a6, "PCESP": 0x34495e, "PCERJ": 0x34495e
        }
        return colors.get(organizacao, 0x000000)

# --- Cog para o Bot ---
class RSO(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(RSOStartView(bot))

    @app_commands.command(name="rso", description="Abre o painel para iniciar um novo Relatório de Serviço Operacional (RSO).")
    async def rso(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📋 Painel de Relatórios de Serviço Operacional",
            description=(
                "Clique no botão abaixo para iniciar um novo relatório de serviço. "
                "Você poderá escolher a Força Policial e o tipo de relatório no próximo passo."
                "\n\nRelatórios são essenciais para a organização da corporação. 📈"
            ),
            color=0x3498db
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=RSOStartView(self.bot))

async def setup(bot: commands.Bot):
    await bot.add_cog(RSO(bot))