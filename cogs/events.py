import discord
from discord.ext import commands
from rich.console import Console
from rich.table import Table
import json
from datetime import datetime

console = Console()

class EventHandlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        for ticket_id, ticket in self.bot.tickets["abiertos"].items():
            if message.channel.id == ticket["id"]:
                ticket["mensajes"].append({
                    "autor": message.author.name,
                    "user_id": message.author.id,
                    "contenido": message.content,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                with open('tickets.json', 'w') as f:
                    json.dump(self.bot.tickets, f)
                break

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(EventHandlers(bot))