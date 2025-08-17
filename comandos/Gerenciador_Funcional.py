import discord

from discord.ext import commands

from discord import app_commands

import json

import os

import time

import datetime

import traceback


# --- ARQUIVOS DE DADOS E LOGS ---

SOLICITACOES_FILE = "solicitacoes_funcional.json"

CARGOS_FILE = "funcional_cargos.json"

CONFIG_FILE = "funcional_config.json"

ADMIN_ROLES_FILE = "funcional_admin_roles.json" # Novo arquivo para os cargos de admin

LOG_FILE = "funcional_log.txt"


# --- FUNÇÕES DE PERSISTÊNCIA E LOG ---

def load_json(file_path):

    if not os.path.exists(file_path):

        return {}

    try:

        with open(file_path, "r", encoding="utf-8") as f:

            return json.load(f)

    except json.JSONDecodeError:

        return {}


def save_json(file_path, data):

    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4, ensure_ascii=False)


def log_message(message: str):

    """Escreve uma mensagem de log com timestamp em um arquivo."""

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"[{timestamp}] {message}\n"

    print(log_entry.strip())  # Imprime no console também

    with open(LOG_FILE, "a", encoding="utf-8") as f:

        f.write(log_entry)


# --- VERIFICAÇÃO DE PERMISSÕES ---

def check_permissions():

    async def predicate(interaction: discord.Interaction):

        admin_roles_data = load_json(ADMIN_ROLES_FILE)

        guild_id = str(interaction.guild.id)

       

        # Se não houver cargos de admin configurados, somente quem pode gerenciar cargos pode aprovar.

        if not admin_roles_data.get(guild_id):

            return interaction.user.guild_permissions.manage_roles

           

        admin_roles_ids = set(admin_roles_data.get(guild_id, []))

        user_roles_ids = {role.id for role in interaction.user.roles}

       

        # Retorna True se o usuário tiver pelo menos um dos cargos de admin

        if not admin_roles_ids.isdisjoint(user_roles_ids):

            return True

       

        await interaction.response.send_message("❌ Você não tem permissão para aprovar ou reprovar solicitações. Apenas administradores funcionais podem fazer isso.", ephemeral=True)

        return False

    return app_commands.check(predicate)


# -----------------------------

# BOTÃO PÚBLICO DE FUNCIONAL

# -----------------------------


class FuncionalButton(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)


    @discord.ui.button(label="Solicitar Funcional", style=discord.ButtonStyle.primary, custom_id="funcional_solicitar", emoji="📄")

    async def solicitar(self, interaction: discord.Interaction, button: discord.ui.Button):

        log_message(f"Usuário {interaction.user.name} ({interaction.user.id}) clicou no botão de solicitar funcional.")

        guild_id = str(interaction.guild.id)

        cargos_data = load_json(CARGOS_FILE).get(guild_id, {})


        if not cargos_data.get('graduacao') or not cargos_data.get('guarnicao'):

            log_message(f"Erro: Cargos de guarnição ou graduação não configurados para o servidor {interaction.guild.name}.")

            await interaction.response.send_message(

                "❌ O administrador ainda não configurou os cargos para Guarnição ou Graduação. Por favor, contate a gerência.",

                ephemeral=True

            )

            return


        modal = FuncionalModal(

            guild_id=interaction.guild.id,

            usuario=interaction.user,

            cargos_ids=cargos_data

        )

        await interaction.response.send_modal(modal)


# -----------------------------

# MODAL DE SOLICITAÇÃO

# -----------------------------

class FuncionalModal(discord.ui.Modal):

    def __init__(self, guild_id: int, usuario: discord.Member, cargos_ids: dict):

        super().__init__(title="📋 Solicitação de Funcional")

        self.guild_id = guild_id

        self.usuario = usuario

        self.cargos_ids = cargos_ids


        # Campos do Modal

        self.nome = discord.ui.TextInput(label="👤 Nome", placeholder="Ex: Lucas Gabriel", required=True)

        self.id_usuario = discord.ui.TextInput(label="🆔 ID", placeholder="Ex: 123.456", required=True)

        self.recrutador = discord.ui.TextInput(label="📢 Recrutador", placeholder="Nome do recrutador (Opcional)", required=False)


        # Adiciona os campos à Modal

        self.add_item(self.nome)

        self.add_item(self.id_usuario)

        self.add_item(self.recrutador)


    async def on_submit(self, interaction: discord.Interaction):

        log_message(f"Modal de solicitação submetido por {self.usuario.name}. Dados recebidos: Nome='{self.nome.value}', ID='{self.id_usuario.value}', Recrutador='{self.recrutador.value}'")

       

        try:

            def build_unique_options(guild: discord.Guild, ids: list):

                seen = set()

                options = []

                for cid in ids:

                    role = guild.get_role(int(cid))

                    if role and cid not in seen:

                        options.append(discord.SelectOption(label=role.name, value=str(cid)))

                        seen.add(cid)

                return options


            guarn_options = build_unique_options(interaction.guild, self.cargos_ids.get('guarnicao', []))

            gradu_options = build_unique_options(interaction.guild, self.cargos_ids.get('graduacao', []))


            if not guarn_options or not gradu_options:

                log_message(f"Erro: Cargos de guarnição ou graduação não encontrados ou configurados incorretamente para o servidor {interaction.guild.name}.")

                await interaction.response.send_message(

                    "❌ Alguns cargos não foram encontrados. Contate um administrador para configurar os cargos corretamente.",

                    ephemeral=True

                )

                return


            view = FuncionalSelectionView(

                usuario=self.usuario,

                nome=self.nome.value,

                id_usuario=self.id_usuario.value,

                recrutador=self.recrutador.value,

                guarnicao_options=guarn_options,

                graduacao_options=gradu_options

            )

           

            await interaction.response.send_message(

                "Agora selecione sua **Guarnição** e **Graduação**:",

                view=view,

                ephemeral=True

            )

            log_message(f"Mensagem de seleção de guarnição enviada com sucesso para {self.usuario.name}.")


        except discord.errors.InteractionResponded as e:

            log_message(f"ERRO CRÍTICO DE INTERAÇÃO: A interação do modal já foi respondida. Detalhes: {e}")

            log_message(f"Traceback: {traceback.format_exc()}")

           

        except Exception as e:

            log_message(f"ERRO INESPERADO AO PROCESSAR MODAL: {e}")

            log_message(f"Traceback: {traceback.format_exc()}")

            if not interaction.response.is_done():

                await interaction.response.send_message(

                    "❌ Ocorreu um erro interno ao processar sua solicitação. Tente novamente mais tarde.",

                    ephemeral=True

                )


# -----------------------------

# VIEW QUE GERE A SEQUÊNCIA DE SELEÇÃO

# -----------------------------

class FuncionalSelectionView(discord.ui.View):

    def __init__(self, usuario: discord.Member, nome: str, id_usuario: str, recrutador: str, guarnicao_options: list, graduacao_options: list):

        super().__init__(timeout=300)

        self.usuario = usuario

        self.nome = nome

        self.id_usuario = id_usuario

        self.recrutador = recrutador

        self.guarnicao_id = None

        self.graduacao_id = None


        self.guarnicao_select = discord.ui.Select(

            placeholder="Selecione sua Guarnição",

            options=guarnicao_options,

            custom_id="guarn_select"

        )

        self.guarnicao_select.callback = self.guarnicao_callback


        self.graduacao_select = discord.ui.Select(

            placeholder="Selecione sua Graduação",

            options=graduacao_options,

            custom_id="grad_select",

        )

        self.graduacao_select.callback = self.graduacao_callback

       

        self.add_item(self.guarnicao_select)

        self.add_item(self.graduacao_select)


        self.cancel_button = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger, row=2)

        self.cancel_button.callback = self.cancel_callback

        self.add_item(self.cancel_button)


    async def guarnicao_callback(self, interaction: discord.Interaction):

        self.guarnicao_id = interaction.data['values'][0]

        await interaction.response.edit_message(content="✅ Guarnição selecionada. Agora selecione a Graduação:", view=self)


    async def graduacao_callback(self, interaction: discord.Interaction):

        self.graduacao_id = interaction.data['values'][0]

       

        self.guarnicao_select.disabled = True

        self.graduacao_select.disabled = True

        self.cancel_button.disabled = True

       

        config_data = load_json(CONFIG_FILE)

        canal_ap_id = config_data.get(str(interaction.guild.id))

        canal_ap = interaction.guild.get_channel(canal_ap_id) if canal_ap_id else None


        if not canal_ap:

            await interaction.response.edit_message(

                content="❌ O canal de aprovação não foi configurado. Contate um administrador.", view=None

            )

            return


        solicitacoes = load_json(SOLICITACOES_FILE)

        guild_id = str(interaction.guild.id)

        if guild_id not in solicitacoes:

            solicitacoes[guild_id] = []


        solicitacao_id = int(time.time() * 1000)

        nova_solicitacao = {

            "id_solicitacao": solicitacao_id,

            "usuario_id": self.usuario.id,

            "nome": self.nome,

            "id_usuario": self.id_usuario,

            "recrutador": self.recrutador,

            "guarnicao": self.guarnicao_id,

            "graduacao": self.graduacao_id,

            "status": "pendente",

            "aprovador_id": None,

            "motivo_reprovacao": None,

            "timestamp": int(time.time())

        }

        solicitacoes[guild_id].append(nova_solicitacao)

        save_json(SOLICITACOES_FILE, solicitacoes)


        # Novo embed de solicitação de aprovação

        embed = discord.Embed(

            title="✨ Nova Solicitação de Funcional",

            description=f"Solicitação ID: `{solicitacao_id}`",

            color=0xFEE75C,

            timestamp=interaction.created_at

        )

        embed.set_author(name=f"Por: {self.nome}", icon_url=self.usuario.display_avatar.url)

        embed.set_thumbnail(url=self.usuario.display_avatar.url)

        embed.add_field(name="<:user:1406006208183275697> Usuário:", value=self.usuario.mention, inline=True)

        embed.add_field(name="<:id:1269389922570020864> ID do Jogo:", value=self.id_usuario, inline=True)

        embed.add_field(name="<:recruiter:1406006227103776930> ID Discord:", value=self.usuario.id, inline=True)

        embed.add_field(name="<:star:1269389921202796584> Graduação:", value=interaction.guild.get_role(int(self.graduacao_id)).mention, inline=True)

        embed.add_field(name="<:garrisson:1406006234490077347> Guarnição:", value=interaction.guild.get_role(int(self.guarnicao_id)).mention, inline=True)

        embed.add_field(name="<:discord:1406006242945536040> Recrutador:", value=self.recrutador or "Não informado", inline=True)

        embed.set_footer(text=f"Solicitação enviada")

       

        view = FuncionalApprovalView(solicitacao=nova_solicitacao)

       

        # --- MODIFICAÇÃO: Enviando a menção @here junto com o embed ---

        await canal_ap.send(content="@here", embed=embed, view=view)

       

        log_message(f"Solicitação de {self.usuario.name} enviada para o canal de aprovação com menção @here.")

        await interaction.response.edit_message(content="✅ Solicitação enviada para aprovação!", view=None)

        self.stop()

   

    async def cancel_callback(self, interaction: discord.Interaction):

        log_message(f"Usuário {interaction.user.name} cancelou a solicitação.")

        await interaction.response.edit_message(content="✅ Solicitação de funcional cancelada.", view=None)

        self.stop()


# -----------------------------

# APROVAÇÃO / REPROVAÇÃO

# -----------------------------

class FuncionalApprovalView(discord.ui.View):

    def __init__(self, solicitacao: dict):

        super().__init__(timeout=None)

        self.solicitacao = solicitacao


    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.success, custom_id="aprov_btn", emoji="👍")

    @check_permissions()

    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):

        log_message(f"Aprovação iniciada por {interaction.user.name} para solicitação {self.solicitacao['id_solicitacao']}.")

        await interaction.response.defer(ephemeral=True, thinking=True)

        guild = interaction.guild

        member = guild.get_member(self.solicitacao['usuario_id'])

        if not member:

            log_message(f"Erro: Membro {self.solicitacao['usuario_id']} não encontrado no servidor para aprovação.")

            await interaction.followup.send("❌ Membro não encontrado no servidor.", ephemeral=True)

            return


        cargos_data = load_json(CARGOS_FILE).get(str(guild.id), {})

        adicionais = [guild.get_role(int(cid)) for cid in cargos_data.get("adicionais", []) if guild.get_role(int(cid))]

        guarn_role = guild.get_role(int(self.solicitacao['guarnicao']))

        grad_role = guild.get_role(int(self.solicitacao['graduacao']))

       

        roles_to_add = [r for r in [guarn_role, grad_role] if r]

        roles_to_add.extend(adicionais)


        if roles_to_add:

            try:

                await member.add_roles(*roles_to_add, reason=f"Aprovado por {interaction.user.name}")

            except discord.Forbidden:

                await interaction.followup.send("❌ Não tenho permissão para adicionar os cargos.", ephemeral=True)

                return


        try:

            await member.edit(nick=f"{self.solicitacao['nome']} | {self.solicitacao['id_usuario']}", reason=f"Aprovado por {interaction.user.name}")

        except (discord.Forbidden, discord.HTTPException):

            pass


        try:

            await member.send(f"✅ Sua solicitação de funcional foi aprovada por {interaction.user.name} no servidor {guild.name}.")

        except discord.Forbidden:

            pass


        solicitacoes = load_json(SOLICITACOES_FILE)

        guild_id = str(guild.id)

        if guild_id in solicitacoes:

            for s in solicitacoes[guild_id]:

                if s['id_solicitacao'] == self.solicitacao['id_solicitacao']:

                    s['status'] = "aprovado"

                    s['aprovador_id'] = interaction.user.id

                    s['aprovacao_timestamp'] = int(time.time())

                    save_json(SOLICITACOES_FILE, solicitacoes)

                    break


        embed = interaction.message.embeds[0]

        embed.color = discord.Color.green()

        embed.title = "✅ Solicitação Aprovada"

        embed.description = "Os cargos foram aplicados e o apelido foi atualizado."

        embed.set_footer(text=f"Aprovado por {interaction.user.name}")

        await interaction.message.edit(embed=embed, view=None)

        await interaction.followup.send("✅ Solicitação aprovada, cargos aplicados e apelido atualizado!", ephemeral=True)


    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.danger, custom_id="reprov_btn", emoji="👎")

    @check_permissions()

    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        log_message(f"Reprovação iniciada por {interaction.user.name} para solicitação {self.solicitacao['id_solicitacao']}.")

        modal = RejectionReasonModal(self.solicitacao)

        await interaction.response.send_modal(modal)


class RejectionReasonModal(discord.ui.Modal):

    def __init__(self, solicitacao: dict):

        super().__init__(title="Motivo da Reprovação")

        self.solicitacao = solicitacao

        self.motivo = discord.ui.TextInput(label="Motivo", placeholder="Digite o motivo da reprovação", required=True)

        self.add_item(self.motivo)


    async def on_submit(self, interaction: discord.Interaction):

        log_message(f"Modal de reprovação submetido por {interaction.user.name} para solicitação {self.solicitacao['id_solicitacao']}.")

        await interaction.response.defer(ephemeral=True, thinking=True)

        solicitacoes = load_json(SOLICITACOES_FILE)

        guild_id = str(interaction.guild.id)

        if guild_id in solicitacoes:

            for s in solicitacoes[guild_id]:

                if s['id_solicitacao'] == self.solicitacao['id_solicitacao']:

                    s['status'] = "reprovado"

                    s['aprovador_id'] = interaction.user.id

                    s['motivo_reprovacao'] = self.motivo.value

                    s['reprovacao_timestamp'] = int(time.time())

                    save_json(SOLICITACOES_FILE, solicitacoes)

                    break

       

        guild = interaction.guild

        member = guild.get_member(self.solicitacao['usuario_id'])

        if member:

            try:

                await member.send(

                    f"❌ Sua solicitação de funcional foi reprovada por {interaction.user.name} no servidor {guild.name}.\n"

                    f"Motivo: {self.motivo.value}"

                )

            except discord.Forbidden:

                pass

       

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.red()

        embed.title = "❌ Solicitação Reprovada"

        embed.description = "A solicitação foi rejeitada e o usuário foi notificado."

        embed.add_field(name="Motivo da Reprovação:", value=self.motivo.value, inline=False)

        embed.set_footer(text=f"Reprovado por {interaction.user.name}")

        await interaction.message.edit(embed=embed, view=None)

        await interaction.followup.send("✅ Solicitação reprovada e usuário notificado!", ephemeral=True)


# -----------------------------

# PAGINAÇÃO DE CARGOS (FUNCIONALCARGOS)

# -----------------------------

class PaginatedSelectView(discord.ui.View):

    def __init__(self, interaction: discord.Interaction, options: list, tipo: str):

        super().__init__(timeout=300)

        self.interaction = interaction

        self.options = options

        self.tipo = tipo

        self.page = 0

        self.max_per_page = 25

        self.all_selected_values = set(load_json(CARGOS_FILE).get(str(interaction.guild.id), {}).get(tipo, []))

        self.update_select()


    def update_select(self):

        self.clear_items()

       

        start = self.page * self.max_per_page

        end = start + self.max_per_page

        page_options = self.options[start:end]


        for option in page_options:

            option.default = option.value in self.all_selected_values


        select = discord.ui.Select(

            placeholder=f"Selecione os cargos ({self.tipo}) - Página {self.page + 1}/{(len(self.options) - 1) // self.max_per_page + 1}",

            options=page_options,

            min_values=0,

            max_values=len(page_options)

        )

        select.callback = self.select_callback

        self.add_item(select)


        if self.page > 0:

            btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="prev_page_btn", row=1)

            btn_prev.callback = self.prev_page_btn

            self.add_item(btn_prev)


        if end < len(self.options):

            btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="next_page_btn", row=1)

            btn_next.callback = self.next_page_btn

            self.add_item(btn_next)

       

        btn_save = discord.ui.Button(label="Salvar", style=discord.ButtonStyle.success, custom_id="save_selection_btn", row=2)

        btn_save.callback = self.save_selection_btn

        self.add_item(btn_save)


        btn_cancel = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger, custom_id="cancel_selection_btn", row=2)

        btn_cancel.callback = self.cancel_selection_btn

        self.add_item(btn_cancel)


    async def select_callback(self, interaction: discord.Interaction):

        current_page_options = {opt.value for opt in self.children[0].options}

        current_selection_on_page = set(interaction.data.get("values", []))

       

        self.all_selected_values.difference_update(current_page_options)

        self.all_selected_values.update(current_selection_on_page)

       

        self.update_select()

        await interaction.response.edit_message(view=self)


    async def prev_page_btn(self, interaction: discord.Interaction):

        if self.page > 0:

            self.page -= 1

            self.update_select()

            await interaction.response.edit_message(view=self)


    async def next_page_btn(self, interaction: discord.Interaction):

        if (self.page + 1) * self.max_per_page < len(self.options):

            self.page += 1

            self.update_select()

            await interaction.response.edit_message(view=self)


    async def save_selection_btn(self, interaction: discord.Interaction):

        log_message(f"Salvando cargos de {self.tipo} para o servidor {interaction.guild.name}.")

       

        # O arquivo de destino muda dependendo do tipo

        if self.tipo == "admin":

            file_path = ADMIN_ROLES_FILE

        else:

            file_path = CARGOS_FILE

           

        data = load_json(file_path)

        guild_id = str(interaction.guild.id)

        if guild_id not in data:

            data[guild_id] = {} if file_path == CARGOS_FILE else []

       

        if file_path == CARGOS_FILE:

            data[guild_id][self.tipo] = list(self.all_selected_values)

        else:

            data[guild_id] = list(self.all_selected_values)

           

        save_json(file_path, data)

        log_message(f"Cargos de {self.tipo} salvos com sucesso. Total de {len(self.all_selected_values)} cargos.")

       

        for item in self.children:

            item.disabled = True

       

        await interaction.response.edit_message(

            content=f"✅ Cargos de **{self.tipo}** atualizados. Foram salvos {len(self.all_selected_values)} cargos.",

            view=self

        )

        self.stop()

       

    async def cancel_selection_btn(self, interaction: discord.Interaction):

        log_message(f"Seleção de cargos de {self.tipo} para o servidor {interaction.guild.name} foi cancelada.")

        for item in self.children:

            item.disabled = True

        await interaction.response.edit_message(

            content="❌ A seleção de cargos foi cancelada.",

            view=self

        )

        self.stop()


# -----------------------------

# COG PRINCIPAL

# -----------------------------

class FuncionalCog(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        self.bot.add_view(FuncionalButton())

        self.bot.add_view(FuncionalApprovalView(solicitacao={}))


    @app_commands.command(name="setfuncional", description="Envia embed público para solicitar funcional")

    @app_commands.describe(canal="Canal onde o embed será enviado")

    @app_commands.checks.has_permissions(manage_channels=True)

    async def setfuncional(self, interaction: discord.Interaction, canal: discord.TextChannel):

        log_message(f"Comando /setfuncional executado por {interaction.user.name} em {interaction.guild.name}.")

        embed = discord.Embed(

            title="📄 Sistema de Emissão de Funcional",

            description="Clique no botão abaixo para preencher o formulário e solicitar sua funcional. Sua solicitação será enviada para a gerência aprovar.",

            color=0x5865F2

        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await canal.send(embed=embed, view=FuncionalButton())

        await interaction.response.send_message(f"✅ Embed de funcional enviado em {canal.mention}", ephemeral=True)

        log_message(f"Embed de solicitação enviado com sucesso para o canal {canal.name}.")


    @app_commands.command(name="funcionalcargos", description="Definir cargos disponíveis")

    @app_commands.choices(tipo=[

        app_commands.Choice(name="Guarnição", value="guarnicao"),

        app_commands.Choice(name="Graduação", value="graduacao"),

        app_commands.Choice(name="Adicionais", value="adicionais")

    ])

    @app_commands.checks.has_permissions(manage_roles=True)

    async def funcionalcargos(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):

        log_message(f"Comando /funcionalcargos ({tipo.name}) executado por {interaction.user.name} em {interaction.guild.name}.")

        cargos_disponiveis = [role for role in interaction.guild.roles if role.is_assignable() and role.name != "@everyone"]

        if not cargos_disponiveis:

            log_message(f"Aviso: Nenhum cargo gerenciável encontrado para o servidor {interaction.guild.name}.")

            await interaction.response.send_message("⚠️ Nenhum cargo gerenciável encontrado.", ephemeral=True)

            return

        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in cargos_disponiveis]

        view = PaginatedSelectView(interaction, options, tipo.value)

        await interaction.response.send_message(f"Selecione os cargos de **{tipo.name}**:", view=view, ephemeral=True)


    @app_commands.command(name="setfuncionalap", description="Definir canal de aprovação")

    @app_commands.describe(canal="Canal onde solicitações serão enviadas")

    @app_commands.checks.has_permissions(manage_channels=True)

    async def setfuncionalap(self, interaction: discord.Interaction, canal: discord.TextChannel):

        log_message(f"Comando /setfuncionalap executado por {interaction.user.name} em {interaction.guild.name}.")

        config_data = load_json(CONFIG_FILE)

        config_data[str(interaction.guild.id)] = canal.id

        save_json(CONFIG_FILE, config_data)

        await interaction.response.send_message(f"✅ Canal de aprovação definido: {canal.mention}", ephemeral=True)

        log_message(f"Canal de aprovação definido para {canal.name} no servidor {interaction.guild.name}.")


    # --- NOVO COMANDO: /setfuncionaladmin ---

    @app_commands.command(name="setadminfuncional", description="Define os cargos que podem aprovar/reprovar funcionais.")

    @app_commands.checks.has_permissions(administrator=True) # Apenas administradores do servidor podem usar este comando.

    async def setfuncionaladmin(self, interaction: discord.Interaction):

        log_message(f"Comando /setadminfuncional executado por {interaction.user.name} em {interaction.guild.name}.")

       

        cargos_disponiveis = [role for role in interaction.guild.roles if not role.is_assignable() and role.name != "@everyone" or interaction.guild.owner.top_role.position > role.position]

        if not cargos_disponiveis:

            log_message(f"Aviso: Nenhum cargo gerenciável encontrado para o servidor {interaction.guild.name}.")

            await interaction.response.send_message("⚠️ Nenhum cargo gerenciável encontrado para adicionar como admin. Certifique-se de que os cargos do bot estão acima deles.", ephemeral=True)

            return

        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in cargos_disponiveis]

       

        view = PaginatedSelectView(interaction, options, "admin")

       

        await interaction.response.send_message("Selecione os cargos que poderão **aprovar/reprovar** solicitações. Membros com esses cargos, ou permissão de `Gerenciar cargos`, poderão usar os botões de aprovação. Se nenhum cargo for selecionado, apenas quem tiver a permissão `Gerenciar cargos` poderá aprovar/reprovar.", view=view, ephemeral=True)

        log_message(f"Embed de seleção de cargos de admin enviado para {interaction.user.name}.")

       

# -----------------------------

# SETUP

# -----------------------------

async def setup(bot: commands.Bot):

    await bot.add_cog(FuncionalCog(bot)) 