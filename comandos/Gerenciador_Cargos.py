import discord
from discord.ext import commands

class RoleSelectView(discord.ui.View):
    def __init__(self, target_user: discord.Member, acao: str, cargos: list):
        super().__init__(timeout=None)
        self.target_user = target_user
        self.acao = acao
        self.cargos = cargos
        self.pagina = 0
        self.max_por_pagina = 25
        self.selecionados = set()
        self.update_items()

    def update_items(self):
        self.clear_items()
        start = self.pagina * self.max_por_pagina
        end = start + self.max_por_pagina
        opcoes = []

        for role in self.cargos[start:end]:
            selected = str(role.id) in self.selecionados
            opcoes.append(discord.SelectOption(label=role.name, value=str(role.id), default=selected))

        # SelectMenu
        select = discord.ui.Select(
            placeholder="Selecione os cargos...",
            min_values=0,
            max_values=min(25, len(opcoes)),
            options=opcoes
        )
        select.callback = self.select_callback
        self.add_item(select)

        # Botões de navegação
        if self.pagina > 0:
            btn_prev = discord.ui.Button(label="◀️ Página Anterior", style=discord.ButtonStyle.primary)
            btn_prev.callback = self.prev_page
            self.add_item(btn_prev)

        if end < len(self.cargos):
            btn_next = discord.ui.Button(label="Próxima Página ▶️", style=discord.ButtonStyle.primary)
            btn_next.callback = self.next_page
            self.add_item(btn_next)

        # Botão aplicar cargos
        btn_apply = discord.ui.Button(label="✅ Aplicar Cargos", style=discord.ButtonStyle.success)
        btn_apply.callback = self.apply_roles
        self.add_item(btn_apply)

    async def select_callback(self, interaction: discord.Interaction):
        select_values = set(interaction.data["values"])
        start = self.pagina * self.max_por_pagina
        end = start + self.max_por_pagina
        for role in self.cargos[start:end]:
            if str(role.id) in self.selecionados and str(role.id) not in select_values:
                self.selecionados.remove(str(role.id))
            elif str(role.id) in select_values:
                self.selecionados.add(str(role.id))
        await interaction.response.defer(ephemeral=True)

    async def prev_page(self, interaction: discord.Interaction):
        if self.pagina > 0:
            self.pagina -= 1
            self.update_items()
            await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        if (self.pagina + 1) * self.max_por_pagina < len(self.cargos):
            self.pagina += 1
            self.update_items()
            await interaction.response.edit_message(view=self)

    async def apply_roles(self, interaction: discord.Interaction):
        if not self.selecionados:
            await interaction.response.send_message("⚠️ Nenhum cargo selecionado.", ephemeral=True)
            return

        added = []
        removed = []

        await interaction.response.defer(ephemeral=True, thinking=True)

        for role_id in self.selecionados:
            role = interaction.guild.get_role(int(role_id))
            if not role or not role.is_assignable():
                continue

            if self.acao == "adicionar":
                if role not in self.target_user.roles:
                    await self.target_user.add_roles(role, reason=f"Adicionado por {interaction.user.name}")
                    added.append(role.mention)
            elif self.acao == "remover":
                if role in self.target_user.roles:
                    await self.target_user.remove_roles(role, reason=f"Removido por {interaction.user.name}")
                    removed.append(role.mention)

        lista_cargos = ", ".join(added + removed) or "Nenhuma alteração foi necessária."
        embed = discord.Embed(
            title="✅ Gerenciamento de Cargos Concluído",
            color=0x00ff00 if self.acao == "adicionar" else 0xff0000
        )
        embed.add_field(name="Usuário", value=self.target_user.mention, inline=False)
        embed.add_field(name="Ação Realizada", value=self.acao.capitalize(), inline=False)
        embed.add_field(name="Cargos Alterados", value=lista_cargos, inline=False)
        embed.set_footer(text=f"Executado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

        await interaction.message.edit(embed=embed, view=None)

# --- COG PRINCIPAL ---
class SetCargos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="setcargos", description="Adicionar ou remover múltiplos cargos de um usuário.")
    @discord.app_commands.describe(usuario="O usuário para gerenciar os cargos.", acao="Escolha entre adicionar ou remover.")
    @discord.app_commands.choices(
        acao=[
            discord.app_commands.Choice(name="Adicionar", value="adicionar"),
            discord.app_commands.Choice(name="Remover", value="remover")
        ]
    )
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def setcargos(self, interaction: discord.Interaction, usuario: discord.Member, acao: discord.app_commands.Choice[str]):
        cargos_disponiveis = [role for role in interaction.guild.roles if role.is_assignable()]
        cargos_disponiveis.sort(key=lambda r: r.position, reverse=True)

        if not cargos_disponiveis:
            await interaction.response.send_message("⚠️ Nenhum cargo gerenciável encontrado.", ephemeral=True)
            return

        view = RoleSelectView(usuario, acao.value, cargos_disponiveis)
        embed = discord.Embed(
            title="🔧 Seleção de Cargos",
            description=f"Navegue entre páginas, selecione os cargos e clique em **Aplicar Cargos** para confirmar alterações em {usuario.mention}.",
            color=0x5865F2
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetCargos(bot))
