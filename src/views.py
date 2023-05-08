import discord
import sqlite3
from src import log
from .sql import *



logger = log.setup_logger(__name__)

conn = create_connection()
create_table(conn)


class PineoupasView(discord.ui.View):
    def __init__(self, timeout, user_clicks, client):
        super().__init__(timeout=timeout)
        self.cliked = False
        self.conn = create_connection()
        self.user_clicks = user_clicks
        self.client = client

    async def on_timeout(self):
        # if not self.clicked:
        #     for child in self.children:
        #         child.disabled = True
        #     await self.message.edit(content="Votes terminés !", view=self)
        for child in self.children:
            child.disabled = True
        current_embed = self.message.embeds[0]
        current_embed.title = "Votes terminés !🔒"
        
        lines = []
        for user_id, click in self.user_clicks.items():
            user = await self.client.fetch_user(user_id)
            line = f"{user.name} - {click}"
            lines.append(line)
        text = "\n".join(lines)
        current_embed.description = f"***Votes:***\n{text}"
        await self.message.edit(embed=current_embed, view=self)

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.green)
    async def oui_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id in self.user_clicks:
            await interaction.response.send_message("Vous avez déjà voté !", ephemeral=True)
            return

        self.user_clicks[interaction.user.id] = '✅'

        # for child in self.children:
        #     child.disabled = True
        #     self.clicked = True
        # await self.message.edit(view=self) # update the message with disabled buttons

        update_user_count(conn, interaction.user.id, oui=1, non=0, rep=3)
        oui_count, non_count, rep = get_user_count(conn, interaction.user.id)

        rank = get_rank(rep)

        embed = discord.Embed(title=f"**{interaction.user.name}'s answer:** ✅", color=0x3ad426, description=f"**Total rep:** {rep-3} (+3)\n**Current rank:** {rank} *({rep} rep)*")
        embed.set_thumbnail(url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed, ephemeral=False)
        logger.info(f"\x1b[31m{interaction.user.name}\x1b[0m : Answered ✅ to /pineoupas")
        

    @discord.ui.button(label="Non", style=discord.ButtonStyle.red)
    async def non_button(self, interaction: discord.Interaction,button: discord.ui.Button):

        if interaction.user.id in self.user_clicks:
            await interaction.response.send_message("Vous avez déjà voté !", ephemeral=True)
            return

        self.user_clicks[interaction.user.id] = '❌'

        # for child in self.children:
        #     child.disabled = True
        #     self.clicked = True
        # await self.message.edit(view=self)

        update_user_count(conn, interaction.user.id, oui=0, non=1, rep=-1)
        oui_count, non_count, rep = get_user_count(conn, interaction.user.id)

        rank = get_rank(rep)

        embed = discord.Embed(title=f"**{interaction.user.name}'s answer:** ❌", color=0xd6132d ,description=f"**Total rep:** {rep+1} (-1)\n**Current rank:** {rank} *({rep} rep)*")
        embed.set_thumbnail(url=interaction.user.display_avatar)
        await interaction.response.send_message(embed=embed, ephemeral=False)
        logger.info(f"\x1b[31m{interaction.user.name}\x1b[0m : Answered ❌ to /pineoupas")
        