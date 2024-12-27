import discord
import json

async def update_ticket_embed(guild, bot, TicketView):
    ticket_channel_id = bot.config.get("ticket_channel_id")
    if not ticket_channel_id:
        return  # No se ha configurado el canal de tickets, no hacer nada

    ticket_channel = discord.utils.get(guild.channels, id=ticket_channel_id)
    if not ticket_channel:
        return  # El canal configurado no existe en el servidor

    embed = discord.Embed(
        title="🎫 `|` Sistema de Tickets",
        description="¡Bienvenido a nuestra tienda virtual, el lugar perfecto para adquirir tus productos digitales favoritos de forma rápida y segura! Estamos encantados de tenerte aquí y queremos asegurarnos de que disfrutes al máximo tu experiencia. Por favor, selecciona el producto que deseas adquirir para comenzar con el proceso de compra. ¡Tenemos opciones increíbles esperándote!\n\n",
        color=discord.Color.blue(),
    )
    embed.set_footer(text="Selecciona un producto del menú desplegable.")
    embed.set_image(url="https://media.discordapp.net/attachments/1321630085421338714/1321660800712314971/SISTEMA_DE_TICKETS.png?ex=676e0c0a&is=676cba8a&hm=7862ea34d421470ffccac7d4035c82e1262f85679c29448cf66f2a68ca1903ab&=&format=webp&quality=lossless")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1321690633047642122/1321690693315596298/plykara-high-resolution-logo.png?ex=676e27e1&is=676cd661&hm=f3ba45709566cec07b9316b5bb1d7479d9c00835c9914d888839076b56f9c1f4&=&format=webp&quality=lossless&width=901&height=676")

    message = None
    if bot.tickets.get("setup_message_id"):
        try:
            message = await ticket_channel.fetch_message(bot.tickets["setup_message_id"])
        except discord.NotFound:
            message = None

    if message:
        # Si el mensaje ya existe, se actualiza el embed
        await message.edit(embed=embed, view=TicketView(bot))
    else:
        # Si no existe el mensaje, lo creamos
        message = await ticket_channel.send(embed=embed, view=TicketView(bot))
        bot.tickets["setup_message_id"] = message.id
        save_tickets(bot.tickets)  # Asegúrate de guardar los cambios en el archivo de configuración


async def log_event(bot, guild, description):
    log_channel_id = bot.config.get('log_channel_id')
    if not log_channel_id:
        return

    log_channel = guild.get_channel(int(log_channel_id))
    if log_channel:
        embed = discord.Embed(
            title="🔭 | Nuevo Registro",
            description=description,
            color=discord.Color.blue()
        )
        await log_channel.send(embed=embed)

def save_tickets(tickets):
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)