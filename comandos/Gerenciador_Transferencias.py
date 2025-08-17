import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import time
import datetime
import traceback

# --- ARQUIVOS DE DADOS E LOGS ---
TRANSFERENCIAS_FILE = "transferencias.json"
CARGOS_FILE = "transferencia_cargos.json"
CONFIG_FILE = "transferencia_config.json"
ADMIN_ROLES_FILE = "transferencia_admin_roles.json"  # Novo arquivo para cargos de admin
LOG_FILE = "transferencia_log.txt"

# --- FUNÇÕES DE PERSISTÊNCIA E LOG (Reutilizadas e adaptadas) ---
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

def log_message(message: str, log_file: str):
    """Escreve uma mensagem de log com timestamp em um arquivo."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

# -----------------------------
# BOTÃO PÚBLICO DE TRANSFERÊNCIA
# -----------------------------
class TransferenciaButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Solicitar Transferência", style=discord.ButtonStyle.primary, custom_id="transferencia_solicitar", emoji="🔄")
    async def solicitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_message(f"Usuário {interaction.user.name} ({interaction.user.id}) clicou no botão de solicitar transferência.", LOG_FILE)
        guild_id = str(interaction.guild.id)
        cargos_data = load_json(CARGOS_FILE).get(guild_id, {})
        
        if not cargos_data.get('guarnicao') or not cargos_data.get('graduacao'):
            log_message(f"Erro: Cargos de guarnição ou graduação para transferência não configurados.", LOG_FILE)
            await interaction.response.send_message(
                "❌ O administrador ainda não configurou os cargos para Guarnição ou Graduação. Por favor, contate a gerência.",
                ephemeral=True
            )
            return
            
        guarnicao_atual = "Não Encontrado"
        graduacao_atual = "Não Encontrado"

        guarn_ids = cargos_data.get('guarnicao', [])
        for role in interaction.user.roles:
            if str(role.id) in guarn_ids:
                guarnicao_atual = role.name
                break
        
        gradu_ids = cargos_data.get('graduacao', [])
        for role in interaction.user.roles:
            if str(role.id) in gradu_ids:
                graduacao_atual = role.name
                break
            
        modal = TransferenciaModal(
            guild_id=interaction.guild.id,
            usuario=interaction.user,
            cargos_ids=cargos_data,
            guarnicao_atual=guarnicao_atual,
            graduacao_atual=graduacao_atual
        )
        await interaction.response.send_modal(modal)

# -----------------------------
# MODAL DE SOLICITAÇÃO
# -----------------------------
class TransferenciaModal(discord.ui.Modal):
    def __init__(self, guild_id: int, usuario: discord.Member, cargos_ids: dict, guarnicao_atual: str, graduacao_atual: str):
        super().__init__(title="📋 Solicitação de Transferência")
        self.guild_id = guild_id
        self.usuario = usuario
        self.cargos_ids = cargos_ids
        self.guarnicao_atual = guarnicao_atual
        self.graduacao_atual = graduacao_atual
        
        self.nome = discord.ui.TextInput(label="👤 Nome", placeholder="Ex: Lucas Gabriel", required=True)
        self.id_usuario = discord.ui.TextInput(label="🆔 ID", placeholder="Ex: 123.456", required=True)
        
        self.add_item(self.nome)
        self.add_item(self.id_usuario)

    async def on_submit(self, interaction: discord.Interaction):
        log_message(f"Modal de transferência submetido por {self.usuario.name}.", LOG_FILE)
        
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
                log_message(f"Erro: Cargos de guarnição ou graduação para transferência não encontrados.", LOG_FILE)
                await interaction.response.send_message(
                    "❌ Alguns cargos não foram encontrados. Contate um administrador para configurar os cargos corretamente.",
                    ephemeral=True
                )
                return

            view = TransferenciaSelectionView(
                usuario=self.usuario,
                nome=self.nome.value,
                id_usuario=self.id_usuario.value,
                antiga_guarnicao=self.guarnicao_atual,
                antiga_graduacao=self.graduacao_atual,
                guarnicao_options=guarn_options,
                graduacao_options=gradu_options
            )

            await interaction.response.send_message(
                "Selecione sua **nova Guarnição**:",
                view=view,
                ephemeral=True
            )
            log_message(f"Mensagem de seleção de novos cargos enviada para {self.usuario.name}.", LOG_FILE)

        except Exception as e:
            log_message(f"ERRO INESPERADO AO PROCESSAR MODAL DE TRANSFERÊNCIA: {e}", LOG_FILE)
            log_message(f"Traceback: {traceback.format_exc()}", LOG_FILE)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocorreu um erro interno ao processar sua solicitação. Tente novamente mais tarde.",
                    ephemeral=True
                )

# -----------------------------
# VIEW QUE GERE A SEQUÊNCIA DE SELEÇÃO
# -----------------------------
class TransferenciaSelectionView(discord.ui.View):
    def __init__(self, usuario: discord.Member, nome: str, id_usuario: str, antiga_guarnicao: str, antiga_graduacao: str, guarnicao_options: list, graduacao_options: list):
        super().__init__(timeout=300)
        self.usuario = usuario
        self.nome = nome
        self.id_usuario = id_usuario
        self.antiga_guarnicao = antiga_guarnicao
        self.antiga_graduacao = antiga_graduacao
        self.guarnicao_options = guarnicao_options
        self.graduacao_options = graduacao_options
        self.nova_guarnicao_id = None
        self.nova_graduacao_id = None
        
        self.add_guarnicao_select()

    def add_guarnicao_select(self):
        self.clear_items()
        
        guarnicao_select = discord.ui.Select(
            placeholder="Selecione a nova Guarnição",
            options=self.guarnicao_options[:25],
            custom_id="nova_guarn_select"
        )
        guarnicao_select.callback = self.guarnicao_callback
        self.add_item(guarnicao_select)
        
        cancel_button = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger, row=2)
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)

    async def guarnicao_callback(self, interaction: discord.Interaction):
        self.nova_guarnicao_id = interaction.data['values'][0]
        self.clear_items()
        graduacao_select = discord.ui.Select(
            placeholder="Selecione a nova Graduação",
            options=self.graduacao_options[:25],
            custom_id="nova_grad_select",
        )
        graduacao_select.callback = self.graduacao_callback
        self.add_item(graduacao_select)
        back_button = discord.ui.Button(label="Voltar", style=discord.ButtonStyle.secondary, row=2)
        back_button.callback = self.back_to_guarnicao_callback
        self.add_item(back_button)
        cancel_button = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger, row=2)
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
        await interaction.response.edit_message(content="✅ Nova Guarnição selecionada. Agora selecione a nova Graduação:", view=self)

    async def graduacao_callback(self, interaction: discord.Interaction):
        self.nova_graduacao_id = interaction.data['values'][0]
        self.clear_items()
        
        config_data = load_json(CONFIG_FILE)
        canal_ap_id = config_data.get(str(interaction.guild.id))
        canal_ap = interaction.guild.get_channel(canal_ap_id) if canal_ap_id else None

        if not canal_ap:
            await interaction.response.edit_message(
                content="❌ O canal de aprovação não foi configurado. Contate um administrador.", view=None
            )
            return

        transferencias = load_json(TRANSFERENCIAS_FILE)
        guild_id = str(interaction.guild.id)
        if guild_id not in transferencias:
            transferencias[guild_id] = []

        solicitacao_id = int(time.time() * 1000)
        nova_transferencia = {
            "id_solicitacao": solicitacao_id,
            "usuario_id": self.usuario.id,
            "nome": self.nome,
            "id_usuario": self.id_usuario,
            "antiga_guarnicao": self.antiga_guarnicao,
            "antiga_graduacao": self.antiga_graduacao,
            "nova_guarnicao": self.nova_guarnicao_id,
            "nova_graduacao": self.nova_graduacao_id,
            "status": "pendente",
            "aprovador_id": None,
            "motivo_reprovacao": None,
            "timestamp": int(time.time())
        }
        transferencias[guild_id].append(nova_transferencia)
        save_json(TRANSFERENCIAS_FILE, transferencias)

        # --- MODIFICAÇÃO: Mencionar os cargos de admin no embed ---
        admin_roles_data = load_json(ADMIN_ROLES_FILE).get(guild_id, [])
        admin_mentions = [interaction.guild.get_role(int(role_id)).mention for role_id in admin_roles_data if interaction.guild.get_role(int(role_id))]
        mentions_text = " ".join(admin_mentions)
        # --- FIM MODIFICAÇÃO ---
        
        embed = discord.Embed(
            title="🔄 Nova Solicitação de Transferência",
            description=f"Solicitação ID: `{solicitacao_id}`",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        embed.set_author(name=f"Por: {self.nome}", icon_url=self.usuario.display_avatar.url)
        embed.set_thumbnail(url=self.usuario.display_avatar.url)
        embed.add_field(name="<:user:1406006208183275697> Usuário:", value=self.usuario.mention, inline=True)
        embed.add_field(name="<:id:1269389922570020864> ID do Jogo:", value=self.id_usuario, inline=True)
        embed.add_field(name="<:recruiter:1406006227103776930> ID Discord:", value=self.usuario.id, inline=True)
        embed.add_field(name="<:garrisson:1406006234490077347> Antiga Guarnição:", value=self.antiga_guarnicao, inline=True)
        embed.add_field(name="<:star:1269389921202796584> Antiga Graduação:", value=self.antiga_graduacao, inline=True)
        embed.add_field(name="<:garrisson:1406006234490077347> Nova Guarnição:", value=interaction.guild.get_role(int(self.nova_guarnicao_id)).mention, inline=True)
        embed.add_field(name="<:star:1269389921202796584> Nova Graduação:", value=interaction.guild.get_role(int(self.nova_graduacao_id)).mention, inline=True)
        embed.set_footer(text=f"Solicitação enviada")
        
        view = TransferenciaApprovalView(solicitacao=nova_transferencia)
        # --- MODIFICAÇÃO: Enviando as menções de admin junto com o embed ---
        await canal_ap.send(content="@here", embed=embed, view=view)
        # --- FIM MODIFICAÇÃO ---
        log_message(f"Solicitação de transferência de {self.usuario.name} enviada para o canal de aprovação.", LOG_FILE)
        await interaction.response.edit_message(content="✅ Solicitação de transferência enviada para aprovação!", view=None)
        self.stop()
    
    async def back_to_guarnicao_callback(self, interaction: discord.Interaction):
        self.nova_guarnicao_id = None
        self.add_guarnicao_select()
        await interaction.response.edit_message(content="Selecione a nova **Guarnição** e **Graduação**:", view=self)

    async def cancel_callback(self, interaction: discord.Interaction):
        log_message(f"Usuário {interaction.user.name} cancelou a solicitação de transferência.", LOG_FILE)
        await interaction.response.edit_message(content="✅ Solicitação de transferência cancelada.", view=None)
        self.stop()

# -----------------------------
# APROVAÇÃO / REPROVAÇÃO
# -----------------------------
class TransferenciaApprovalView(discord.ui.View):
    def __init__(self, solicitacao: dict):
        super().__init__(timeout=None)
        self.solicitacao = solicitacao
        
    def check_permissions(self, user: discord.Member) -> bool:
        guild_id = str(user.guild.id)
        admin_roles_data = load_json(ADMIN_ROLES_FILE).get(guild_id, [])
        if not admin_roles_data:
            return user.guild_permissions.administrator
        
        admin_role_ids = [int(role_id) for role_id in admin_roles_data]
        user_role_ids = [role.id for role in user.roles]
        
        return any(role_id in admin_role_ids for role_id in user_role_ids)

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.success, custom_id="aprov_btn_transf", emoji="👍")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # --- MODIFICAÇÃO: Verificação de permissão ---
        if not self.check_permissions(interaction.user):
            await interaction.response.send_message("❌ Você não tem permissão para aprovar esta solicitação.", ephemeral=True)
            return
        # --- FIM MODIFICAÇÃO ---

        log_message(f"Aprovação de transferência iniciada por {interaction.user.name} para solicitação {self.solicitacao['id_solicitacao']}.", LOG_FILE)
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        member = guild.get_member(self.solicitacao['usuario_id'])
        if not member:
            log_message(f"Erro: Membro {self.solicitacao['usuario_id']} não encontrado no servidor para aprovação de transferência.", LOG_FILE)
            await interaction.followup.send("❌ Membro não encontrado no servidor.", ephemeral=True)
            return
            
        cargos_data_funcional = load_json("funcional_cargos.json").get(str(guild.id), {})
        old_roles_ids = cargos_data_funcional.get("guarnicao", []) + cargos_data_funcional.get("graduacao", []) + cargos_data_funcional.get("adicionais", [])
        old_roles = [guild.get_role(int(cid)) for cid in old_roles_ids if guild.get_role(int(cid))]
        
        roles_to_remove = [r for r in old_roles if r in member.roles]
        
        if roles_to_remove:
            try:
                await member.remove_roles(*roles_to_remove, reason=f"Transferência aprovada por {interaction.user.name}")
            except discord.Forbidden:
                await interaction.followup.send("❌ Não tenho permissão para remover os cargos antigos.", ephemeral=True)
                return

        cargos_data_transferencia = load_json(CARGOS_FILE).get(str(guild.id), {})
        adicionais = [guild.get_role(int(cid)) for cid in cargos_data_transferencia.get("adicionais", []) if guild.get_role(int(cid))]
        nova_guarn_role = guild.get_role(int(self.solicitacao['nova_guarnicao']))
        nova_grad_role = guild.get_role(int(self.solicitacao['nova_graduacao']))
        
        roles_to_add = [r for r in [nova_guarn_role, nova_grad_role] if r]
        roles_to_add.extend(adicionais)
        
        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason=f"Transferência aprovada por {interaction.user.name}")
            except discord.Forbidden:
                await interaction.followup.send("❌ Não tenho permissão para adicionar os novos cargos.", ephemeral=True)
                return

        try:
            await member.edit(nick=f"{self.solicitacao['nome']} | {self.solicitacao['id_usuario']}", reason=f"Transferência aprovada por {interaction.user.name}")
        except (discord.Forbidden, discord.HTTPException):
            pass

        try:
            await member.send(f"✅ Sua solicitação de transferência foi aprovada por {interaction.user.name} no servidor {guild.name}.")
        except discord.Forbidden:
            pass

        transferencias = load_json(TRANSFERENCIAS_FILE)
        guild_id = str(guild.id)
        if guild_id in transferencias:
            for s in transferencias[guild_id]:
                if s['id_solicitacao'] == self.solicitacao['id_solicitacao']:
                    s['status'] = "aprovado"
                    s['aprovador_id'] = interaction.user.id
                    s['aprovacao_timestamp'] = int(time.time())
                    save_json(TRANSFERENCIAS_FILE, transferencias)
                    break

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Solicitação de Transferência Aprovada"
        embed.description = "Os cargos foram atualizados e o apelido foi modificado."
        embed.set_footer(text=f"Aprovado por {interaction.user.name}")
        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send("✅ Solicitação de transferência aprovada, cargos atualizados e apelido modificado!", ephemeral=True)

    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.danger, custom_id="reprov_btn_transf", emoji="👎")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        # --- MODIFICAÇÃO: Verificação de permissão ---
        if not self.check_permissions(interaction.user):
            await interaction.response.send_message("❌ Você não tem permissão para reprovar esta solicitação.", ephemeral=True)
            return
        # --- FIM MODIFICAÇÃO ---
        
        log_message(f"Reprovação de transferência iniciada por {interaction.user.name} para solicitação {self.solicitacao['id_solicitacao']}.", LOG_FILE)
        modal = TransferenciaRejectionReasonModal(self.solicitacao)
        await interaction.response.send_modal(modal)

class TransferenciaRejectionReasonModal(discord.ui.Modal):
    def __init__(self, solicitacao: dict):
        super().__init__(title="Motivo da Reprovação de Transferência")
        self.solicitacao = solicitacao
        self.motivo = discord.ui.TextInput(label="Motivo", placeholder="Digite o motivo da reprovação", required=True)
        self.add_item(self.motivo)

    async def on_submit(self, interaction: discord.Interaction):
        log_message(f"Modal de reprovação de transferência submetido por {interaction.user.name} para solicitacao {self.solicitacao['id_solicitacao']}.", LOG_FILE)
        await interaction.response.defer(ephemeral=True, thinking=True)
        transferencias = load_json(TRANSFERENCIAS_FILE)
        guild_id = str(interaction.guild.id)
        if guild_id in transferencias:
            for s in transferencias[guild_id]:
                if s['id_solicitacao'] == self.solicitacao['id_solicitacao']:
                    s['status'] = "reprovado"
                    s['aprovador_id'] = interaction.user.id
                    s['motivo_reprovacao'] = self.motivo.value
                    s['reprovacao_timestamp'] = int(time.time())
                    save_json(TRANSFERENCIAS_FILE, transferencias)
                    break
        
        guild = interaction.guild
        member = guild.get_member(self.solicitacao['usuario_id'])
        if member:
            try:
                await member.send(
                    f"❌ Sua solicitação de transferência foi reprovada por {interaction.user.name} no servidor {guild.name}.\n"
                    f"Motivo: {self.motivo.value}"
                )
            except discord.Forbidden:
                pass
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ Solicitação de Transferência Reprovada"
        embed.description = "A solicitação foi rejeitada e o usuário foi notificado."
        embed.add_field(name="Motivo da Reprovação:", value=self.motivo.value, inline=False)
        embed.set_footer(text=f"Reprovado por {interaction.user.name}")
        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send("✅ Solicitação de transferência reprovada e usuário notificado!", ephemeral=True)

# -----------------------------
# PAGINAÇÃO DE CARGOS PARA ADMIN (NOVA)
# -----------------------------
class PaginatedSelectViewAdmin(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, options: list):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.options = options
        self.page = 0
        self.max_per_page = 25
        self.all_selected_values = set(load_json(ADMIN_ROLES_FILE).get(str(interaction.guild.id), []))
        self.update_select()

    def update_select(self):
        self.clear_items()
        
        start = self.page * self.max_per_page
        end = start + self.max_per_page
        page_options = self.options[start:end]
        
        for option in page_options:
            option.default = option.value in self.all_selected_values

        select = discord.ui.Select(
            placeholder=f"Selecione os cargos - Página {self.page + 1}/{(len(self.options) - 1) // self.max_per_page + 1}",
            options=page_options,
            min_values=0,
            max_values=len(page_options)
        )
        select.callback = self.select_callback
        self.add_item(select)
        
        if self.page > 0:
            btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="prev_page_btn_admin", row=1)
            btn_prev.callback = self.prev_page_btn
            self.add_item(btn_prev)

        if end < len(self.options):
            btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="next_page_btn_admin", row=1)
            btn_next.callback = self.next_page_btn
            self.add_item(btn_next)
        
        btn_save = discord.ui.Button(label="Salvar", style=discord.ButtonStyle.success, custom_id="save_selection_btn_admin", row=2)
        btn_save.callback = self.save_selection_btn
        self.add_item(btn_save)

        btn_cancel = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger, custom_id="cancel_selection_btn_admin", row=2)
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
        log_message(f"Salvando cargos de admin para o servidor {interaction.guild.name}.", LOG_FILE)
        admin_roles_data = load_json(ADMIN_ROLES_FILE)
        guild_id = str(interaction.guild.id)
        admin_roles_data[guild_id] = list(self.all_selected_values)
        save_json(ADMIN_ROLES_FILE, admin_roles_data)
        log_message(f"Cargos de admin salvos com sucesso.", LOG_FILE)
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(
            content=f"✅ Cargos de **Administrador de Transferência** atualizados. Foram salvos {len(self.all_selected_values)} cargos.",
            view=self
        )
        self.stop()
        
    async def cancel_selection_btn(self, interaction: discord.Interaction):
        log_message(f"Seleção de cargos de admin para o servidor {interaction.guild.name} foi cancelada.", LOG_FILE)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="❌ A seleção de cargos foi cancelada.",
            view=self
        )
        self.stop()

# -----------------------------
# PAGINAÇÃO DE CARGOS DE TRANSFERÊNCIA
# -----------------------------
class PaginatedSelectViewTransferencia(discord.ui.View):
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
            btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="prev_page_btn_transf", row=1)
            btn_prev.callback = self.prev_page_btn
            self.add_item(btn_prev)

        if end < len(self.options):
            btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="next_page_btn_transf", row=1)
            btn_next.callback = self.next_page_btn
            self.add_item(btn_next)
        
        btn_save = discord.ui.Button(label="Salvar", style=discord.ButtonStyle.success, custom_id="save_selection_btn_transf", row=2)
        btn_save.callback = self.save_selection_btn
        self.add_item(btn_save)

        btn_cancel = discord.ui.Button(label="Cancelar", style=discord.ButtonStyle.danger, custom_id="cancel_selection_btn_transf", row=2)
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
        log_message(f"Salvando cargos de {self.tipo} para o servidor {interaction.guild.name}.", LOG_FILE)
        cargos_data = load_json(CARGOS_FILE)
        guild_id = str(interaction.guild.id)
        if guild_id not in cargos_data:
            cargos_data[guild_id] = {}
        
        cargos_data[guild_id][self.tipo] = list(self.all_selected_values)
        save_json(CARGOS_FILE, cargos_data)
        log_message(f"Cargos de {self.tipo} salvos com sucesso.", LOG_FILE)
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(
            content=f"✅ Cargos de **{self.tipo}** atualizados. Foram salvos {len(self.all_selected_values)} cargos.",
            view=self
        )
        self.stop()
        
    async def cancel_selection_btn(self, interaction: discord.Interaction):
        log_message(f"Seleção de cargos de {self.tipo} para o servidor {interaction.guild.name} foi cancelada.", LOG_FILE)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content="❌ A seleção de cargos foi cancelada.",
            view=self
        )
        self.stop()
        
# -----------------------------
# COG PRINCIPAL DE TRANSFERÊNCIA
# -----------------------------
class TransferenciaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(TransferenciaButton())
        self.bot.add_view(TransferenciaApprovalView(solicitacao={}))

    @app_commands.command(name="settransferencia", description="Envia embed público para solicitar transferência")
    @app_commands.describe(canal="Canal onde o embed será enviado")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def settransferencia(self, interaction: discord.Interaction, canal: discord.TextChannel):
        log_message(f"Comando /settransferencia executado por {interaction.user.name} em {interaction.guild.name}.", LOG_FILE)
        embed = discord.Embed(
            title="🔄 Sistema de Transferência",
            description="Clique no botão abaixo para preencher o formulário e solicitar sua transferência.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await canal.send(embed=embed, view=TransferenciaButton())
        await interaction.response.send_message(f"✅ Embed de transferência enviado em {canal.mention}", ephemeral=True)
        log_message(f"Embed de solicitação de transferência enviado para o canal {canal.name}.", LOG_FILE)
    
    @app_commands.command(name="transferenciacargos", description="Definir cargos para transferência")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Guarnição", value="guarnicao"),
        app_commands.Choice(name="Graduação", value="graduacao"),
        app_commands.Choice(name="Adicionais", value="adicionais")
    ])
    @app_commands.checks.has_permissions(manage_roles=True)
    async def transferenciacargos(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):
        log_message(f"Comando /transferenciacargos ({tipo.name}) executado por {interaction.user.name} em {interaction.guild.name}.", LOG_FILE)
        cargos_disponiveis = [role for role in interaction.guild.roles if role.is_assignable() and role.name != "@everyone"]
        if not cargos_disponiveis:
            log_message(f"Aviso: Nenhum cargo gerenciável encontrado para o servidor {interaction.guild.name}.", LOG_FILE)
            await interaction.response.send_message("⚠️ Nenhum cargo gerenciável encontrado.", ephemeral=True)
            return
        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in cargos_disponiveis]
        view = PaginatedSelectViewTransferencia(interaction, options, tipo.value)
        await interaction.response.send_message(f"Selecione os cargos de **{tipo.name}** para transferência:", view=view, ephemeral=True)

    @app_commands.command(name="settransferenciaap", description="Definir canal de aprovação de transferências")
    @app_commands.describe(canal="Canal onde solicitações de transferência serão enviadas")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def settransferenciaap(self, interaction: discord.Interaction, canal: discord.TextChannel):
        log_message(f"Comando /settransferenciaap executado por {interaction.user.name} em {interaction.guild.name}.", LOG_FILE)
        config_data = load_json(CONFIG_FILE)
        config_data[str(interaction.guild.id)] = canal.id
        save_json(CONFIG_FILE, config_data)
        await interaction.response.send_message(f"✅ Canal de aprovação de transferências definido: {canal.mention}", ephemeral=True)
        log_message(f"Canal de aprovação para transferência definido para {canal.name} no servidor {interaction.guild.name}.", LOG_FILE)

    @app_commands.command(name="setadmintransferencia", description="Definir cargos de aprovação de transferência")
    @app_commands.checks.has_permissions(administrator=True)
    async def setadmintransferencia(self, interaction: discord.Interaction):
        log_message(f"Comando /setadmintransferencia executado por {interaction.user.name} em {interaction.guild.name}.", LOG_FILE)
        cargos_disponiveis = [role for role in interaction.guild.roles if role.is_assignable() and role.name != "@everyone"]
        if not cargos_disponiveis:
            log_message(f"Aviso: Nenhum cargo gerenciável encontrado para o servidor {interaction.guild.name}.", LOG_FILE)
            await interaction.response.send_message("⚠️ Nenhum cargo gerenciável encontrado.", ephemeral=True)
            return
        
        options = [discord.SelectOption(label=r.name, value=str(r.id)) for r in cargos_disponiveis]
        view = PaginatedSelectViewAdmin(interaction, options)
        await interaction.response.send_message("Selecione os cargos que poderão aprovar/negar solicitações de transferência:", view=view, ephemeral=True)

# -----------------------------
# SETUP
# -----------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(TransferenciaCog(bot))