import discord
from discord.ext import commands
from datetime import datetime

class Registros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_event(self, guild: discord.Guild, embed: discord.Embed):
        """
        Envía el embed de log a un canal específico del servidor.
        Configura el ID del canal de logs aquí.
        """
        log_channel_id = 1321690357074755735  # Cambia este ID al del canal de logs de tu servidor
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(
            title="👤 Nuevo Miembro",
            description=f"¡Un nuevo usuario ha llegado al servidor! 🎉",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="📅 Fecha de Creación de la Cuenta", value=member.created_at.strftime('%d/%m/%Y %H:%M:%S'), inline=True)
        embed.add_field(name="🆔 ID del Usuario", value=member.id, inline=True)
        embed.set_footer(text="Sistema de Registro", icon_url=member.guild.icon.url if member.guild.icon else None)
        await self.log_event(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = discord.Embed(
            title="🚪 Miembro Retirado",
            description=f"Un usuario ha abandonado el servidor. 😔",
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="🆔 ID del Usuario", value=member.id, inline=True)
        embed.add_field(name="📛 Nombre de Usuario", value=str(member), inline=True)
        embed.set_footer(text="Sistema de Registro", icon_url=member.guild.icon.url if member.guild.icon else None)
        await self.log_event(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="🗑️ Mensaje Eliminado",
            description="Se ha eliminado un mensaje en el servidor.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="👤 Autor", value=message.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=message.channel.mention, inline=True)
        embed.add_field(
            name="📄 Contenido del Mensaje",
            value=message.content if message.content else "No había contenido de texto.",
            inline=False,
        )
        embed.set_footer(text="Sistema de Registro", icon_url=message.guild.icon.url if message.guild.icon else None)
        await self.log_event(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Mensaje Editado",
            description="Un mensaje ha sido modificado en el servidor.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="👤 Autor", value=before.author.mention, inline=True)
        embed.add_field(name="📍 Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="Antes", value=before.content or "Sin contenido", inline=False)
        embed.add_field(name="Después", value=after.content or "Sin contenido", inline=False)
        embed.set_footer(text="Sistema de Registro", icon_url=before.guild.icon.url if before.guild.icon else None)
        await self.log_event(before.guild, embed)

async def setup(bot):
    await bot.add_cog(Registros(bot))
