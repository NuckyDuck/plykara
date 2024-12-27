import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta
import telegram

from cogs.telegram import telegram_bot, TELEGRAM_CHAT_ID


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_regex = re.compile(r"(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/[a-zA-Z0-9]+")
        self.url_regex = re.compile(r"https?://[^\s]+")
        self.bad_words = ["estafa", "scam", "farsa", "ladrón", "ladrones", "ratas", "ladron", "nukathosting", "nukat", "nuka", "netbliss", "netbliss", "3stafa", "₤$tafa"]
        self.sanction_log = []

    async def notify_moderators(self, guild, message, reason):
        """Notifica a los moderadores sobre una sanción aplicada."""
        mod_channel_id = 1321690357074755735  # Reemplaza con el ID del canal para moderadores
        mod_channel = guild.get_channel(mod_channel_id)
        if mod_channel:
            embed = discord.Embed(
                title="🔔 Alerta de Moderación",
                description="Se ha aplicado una sanción automática.",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="👤 Usuario", value=message.author.mention, inline=True)
            embed.add_field(name="🆔 ID del Usuario", value=message.author.id, inline=True)
            embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
            embed.add_field(name="📄 Contenido del Mensaje", value=message.content, inline=False)
            embed.add_field(name="⚠️ Razón", value=reason, inline=False)
            embed.set_footer(text="Sistema de Moderación Automática", icon_url=guild.icon.url if guild.icon else None)
            await mod_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        soporte_role_id = self.bot.config.get('soporte_role_id')  # Configuración externa
        soporte_role = discord.utils.get(message.guild.roles, id=int(soporte_role_id))

        # Excluir al rol de soporte
        if soporte_role and soporte_role in message.author.roles:
            return

        # Detectar infracción
        reason = None
        if self.invite_regex.search(message.content):
            reason = "Enlace de invitación detectado."
        elif self.url_regex.search(message.content):
            reason = "Enlace no permitido detectado."
        elif any(bad_word in message.content.lower() for bad_word in self.bad_words):
            reason = "Palabra prohibida detectada."
        elif message.content.isupper() and len(message.content) > 10:
            reason = "Uso excesivo de mayúsculas (CAPS LOCK)."

        if reason:
            await message.delete()
            timeout_duration = timedelta(minutes=1)

            # Aplicar sanción
            try:
                await message.author.edit(
                    timed_out_until=discord.utils.utcnow() + timeout_duration,
                    reason="Automoderación: " + reason
                )
            except discord.Forbidden:
                reason += " (No se pudo aplicar el timeout debido a permisos insuficientes)."

            # Enviar mensaje al usuario sancionado
            embed = discord.Embed(
                title="📘 `|` Sanción Automática Aplicada",
                description="Hemos detectado un mensaje que incumple las normas del servidor.",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )
            embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
            embed.add_field(name="⚠️ Razón", value=reason, inline=False)
            embed.add_field(name="⏳ Duración", value="1 minuto", inline=True)
            embed.set_footer(text="Sistema de Moderación Automática")

            try:
                await message.author.send(embed=embed)
            except discord.Forbidden:
                await self.notify_moderators(message.guild, message, f"No se pudo notificar al usuario sancionado. {reason}")

            # Registrar sanción
            self.sanction_log.append({
                "user": message.author.name,
                "user_id": message.author.id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Notificar a los moderadores
            await self.notify_moderators(message.guild, message, reason)
# En la función que maneja las sanciones automáticas
            await telegram_bot.send_message(
    chat_id=TELEGRAM_CHAT_ID,
    text=(
        "📘 | Sanción Automática Aplicada\n\n"
        "Hemos detectado un mensaje que incumple las normas del servidor.\n\n"
        f"👤 Usuario: {message.author.name}\n"
        f"🆔 ID del Usuario: {message.author.id}\n"
        f"📍 Canal: {message.channel.mention}\n"
        f"📄 Contenido del Mensaje: {message.content}\n"
        f"⚠️ Razón: {reason}\n"
    ),
)


            # Liberar el timeout después de la duración
            await discord.utils.sleep_until(message.author.timed_out_until)
            try:
                await message.author.edit(timed_out_until=None, reason="Timeout completado")
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                title="✏️ Cambio de Apodo Detectado",
                description=f"**Usuario:** {before.mention}\n\n**Antes:** {before.nick or before.name}\n**Ahora:** {after.nick or after.name}",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow(),
            )
            mod_channel_id = 1321690357074755735  # Reemplaza con tu canal de moderación
            mod_channel = after.guild.get_channel(mod_channel_id)
            if mod_channel:
                await mod_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))