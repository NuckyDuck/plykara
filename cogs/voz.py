import discord
from discord.ext import commands

class VoiceChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = 1321688939173515387  # ID del canal de voz específico

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Verificar si el usuario se unió al canal específico
        if after.channel and after.channel.id == self.target_channel_id:
            # Crear un nuevo canal de voz con el nombre del usuario
            guild = member.guild
            new_channel = await guild.create_voice_channel(
                name=f"Sala {member.display_name}",
                user_limit=4,
                category=after.channel.category
            )
            # Mover al usuario al nuevo canal
            await member.move_to(new_channel)

            # Eliminar el canal cuando esté vacío
            def check_empty_channel(channel):
                return len(channel.members) == 0

            while True:
                await self.bot.wait_for('voice_state_update', check=lambda m, b, a: m == member and check_empty_channel(new_channel))
                await new_channel.delete()
                break

async def setup(bot):
    await bot.add_cog(VoiceChannelManager(bot))