import json
import logging
from telegram import Bot
from datetime import datetime, timedelta, timezone
from discord.ext import tasks, commands

# Load the configuration file
with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

# Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = config['telegram_bot_token']
TELEGRAM_CHAT_ID = config['telegram_chat_id']

# Initialize the Telegram bot
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

class TelegramReports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_report.start()

    def cog_unload(self):
        self.daily_report.cancel()

    @tasks.loop(hours=12)
    async def daily_report(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(config['guild_id'])
        if not guild:
            logging.error("Guild not found")
            return

        # Gather data for the report
        now = datetime.now(tz=timezone.utc)
        new_members = sum(1 for member in guild.members if member.joined_at and member.joined_at > now - timedelta(days=1))
        tickets_opened = sum(1 for ticket in self.bot.tickets["abiertos"].values() if datetime.strptime(ticket["fecha_creado"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) > now - timedelta(days=1))
        sanctions = len(self.bot.get_cog('AutoMod').sanction_log)
        total_members = guild.member_count

        # Load previous day's member count
        try:
            with open('previous_member_count.json', 'r') as f:
                previous_data = json.load(f)
                previous_member_count = previous_data.get('member_count', total_members)
        except FileNotFoundError:
            previous_member_count = total_members

        # Calculate percentage change
        if previous_member_count > 0:
            percentage_change = ((total_members - previous_member_count) / previous_member_count) * 100
        else:
            percentage_change = 0.0

        # Save current member count for the next report
        with open('previous_member_count.json', 'w') as f:
            json.dump({'member_count': total_members}, f)

        # Create the report message
        report_message = (
            f"❗ Reporte Diario \n"
            f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \n"
            f"--------------------------- \n"
            f"🔹 Nuevos usuarios hoy: {new_members} \n"
            f"🔸 Cambio desde ayer: {percentage_change:.2f}% \n"
            f"🔹 Tickets Abiertos: {tickets_opened}\n"
            f"🔸 Sanciones Automáticas: {sanctions}\n"
            f"🔹 Total de miembros: {total_members} \n"
            f"--------------------------- \n"
        )

        # Send the report to Telegram
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report_message)

    @daily_report.before_loop
    async def before_daily_report(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TelegramReports(bot))