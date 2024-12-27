import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime
import uuid
from cogs.utils import update_ticket_embed, log_event  # Importar la función y clase desde utils.py
from cogs.telegram import telegram_bot, TELEGRAM_CHAT_ID
class TicketSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label=f"{product['emoji']} {product['nombre']}", 
                value=product_id, 
                description=product.get('descripcion', 'No hay descripción disponible')
            ) for product_id, product in self.bot.products.items()
        ]
        if not options:
            options.append(discord.SelectOption(label="No hay productos disponibles", value="no_product", description="No hay productos para mostrar"))
        placeholder = "No hay productos para mostrar" if len(options) == 0 else "Selecciona un producto para el ticket"
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, custom_id="ticket_select")

    def update_options(self):
        options = [
            discord.SelectOption(
                label=f"{product['emoji']} {product['nombre']}", 
                value=product_id, 
                description=product.get('descripcion', 'No hay descripción disponible')
            ) for product_id, product in self.bot.products.items()
        ]
        if not options:
            options.append(discord.SelectOption(label="No hay productos disponibles", value="no_product", description="No hay productos para mostrar"))
        placeholder = "No hay productos para mostrar" if len(options) == 0 else "Selecciona un producto para el ticket"
        self.options = options
        self.placeholder = placeholder

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "no_product":
            await interaction.response.send_message("No hay productos disponibles para crear un ticket.", ephemeral=True)
            return

        user_tickets = [ticket for ticket in self.bot.tickets["abiertos"].values() if ticket["creado_por"] == interaction.user.name]
        if user_tickets:
            embed = discord.Embed(title="⚠️ Ticket Abierto", description="Ya tienes un ticket abierto.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        product_id = self.values[0]
        product = self.bot.products[product_id]
        ticket_id = str(uuid.uuid4())[:4].replace('-', '').lower()
        guild = interaction.guild
        categoria = self.bot.config.get('ticket_categoria', None)
        category = discord.utils.get(guild.categories, id=int(categoria))
        if category is None:
            embed = discord.Embed(title="❌ Error", description="No se encontró la categoría para crear el ticket.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        soporte_role_id = self.bot.config.get('soporte_role_id')
        role = guild.get_role(int(soporte_role_id))
        if role is None:
            embed = discord.Embed(title="❌ Error", description="No se encontró el rol de soporte.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"ticket-{ticket_id}", category=category, overwrites=overwrites)
        embed = discord.Embed(
            title="🎫 **Ticket Creado Exitosamente**",
            description=(
                f"¡Gracias por tu solicitud, {interaction.user.mention}! Has seleccionado el producto **{product['nombre']}**.\n\n"
                "Nuestro equipo revisará tu solicitud y se pondrá en contacto contigo lo antes posible. "
                "Por favor, asegúrate de leer los detalles adicionales y seguir las instrucciones para agilizar el proceso."
            ),
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3500/3500833.png")  # Imagen para decorar el embed
        embed.set_footer(
            text="Sistema de Tickets | Plykara Store 💙",
        )

        embed.add_field(
            name="📄 **Detalles del Producto**",
            value=(
                f"- **Nombre:** {product['nombre']}\n"
                f"- **Descripción:** {product.get('descripcion', 'No hay descripción disponible')}"
            ),
            inline=False
        )

        embed.add_field(
            name="📋 **Siguiente Paso**",
            value=(
                "1. Un miembro del equipo revisará tu ticket.\n"
                "2. Recibirás una respuesta en este canal.\n"
                "3. Sigue las instrucciones para completar tu compra."
            ),
            inline=False
        )

        embed.add_field(
            name="❓ **¿Dudas o Problemas?**",
            value=(
                "Si tienes alguna consulta adicional, no dudes en mencionarlo aquí. "
                "Nuestro equipo estará encantado de ayudarte."
            ),
            inline=False
        )
        await ticket_channel.send(embed=embed, view=TicketActionView(self.bot, ticket_id))
        self.bot.tickets["abiertos"][ticket_id] = {
            "id": ticket_channel.id,
            "producto": product['nombre'],
            "creado_por": interaction.user.name,
            "fecha_creado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mensajes": []
        }
        save_tickets(self.bot.tickets)
        embed = discord.Embed(title="🎫 Ticket Creado", description=f"Ticket creado: {ticket_channel.mention}", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Reinicia el menú desplegable
        await interaction.message.edit(view=TicketView(self.bot))
        await log_event(self.bot, guild, f"Ticket creado por {interaction.user.name} para el producto {product['nombre']} en {ticket_channel.mention}")
# En la función que maneja la creación de tickets
        await telegram_bot.send_message(
    chat_id=TELEGRAM_CHAT_ID,
    text=(
        "🎫 | Ticket Creado\n\n"
        f"📄 Producto: {product['nombre']}\n"
        f"👤 Creado por: {interaction.user.name}\n"
        f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
)
# Clase para manejar las acciones dentro de un ticket
class TicketActionView(discord.ui.View):
    def __init__(self, bot, ticket_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_id = ticket_id
        self.add_item(TicketActionSelect(bot, ticket_id))

class TicketActionSelect(discord.ui.Select):
    def __init__(self, bot, ticket_id):
        self.bot = bot
        self.ticket_id = ticket_id
        options = [
            discord.SelectOption(label="📝 Reclamar Ticket", value="reclamar"),
            discord.SelectOption(label="❌ Cerrar Ticket", value="cerrar"),
            discord.SelectOption(label="⏸️ Poner en Espera", value="espera")
        ]
        super().__init__(placeholder="Selecciona una acción", min_values=1, max_values=1, options=options, custom_id=f"ticket_action_select_{ticket_id}")

    async def callback(self, interaction: discord.Interaction):
        action = self.values[0]
        if action == "reclamar":
            await reclamar_ticket(interaction, self.ticket_id, self.bot)
        elif action == "cerrar":
            await cerrar_ticket(interaction, self.ticket_id, self.bot)
        elif action == "espera":
            await poner_en_espera(interaction, self.ticket_id, self.bot)

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_select = TicketSelect(bot)
        self.add_item(self.ticket_select)

    def update_view(self):
        self.ticket_select.update_options()
        self.clear_items()
        self.add_item(self.ticket_select)

# Clase principal del sistema de tickets
class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="setup_ticket", description="Envía el menú desplegable para crear un ticket.")
    async def setup_ticket(self, interaction: discord.Interaction):
        await update_ticket_embed(interaction.guild, self.bot, TicketView)
        embed = discord.Embed(title="✅ Sistema de Tickets Configurado", description="El sistema de tickets ha sido configurado correctamente.", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="reopen", description="Reabre un ticket cerrado.")
    @app_commands.describe(ticket_id="El UUID del ticket cerrado que deseas reabrir.")
    async def reopen(self, interaction: discord.Interaction, ticket_id: str):
        ticket = self.bot.tickets["cerrados"].get(ticket_id)
        if not ticket:
            await interaction.response.send_message(f"No se encontró el ticket con UUID: {ticket_id}", ephemeral=True)
            return

        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=1321689972536905738)
        if category is None:
            await interaction.response.send_message("No se encontró la categoría para crear el canal de recuperación.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        recovery_channel = await guild.create_text_channel(name=f"recuperación-{ticket_id}", category=category, overwrites=overwrites)

        if ticket["mensajes"]:
            for msg in ticket["mensajes"]:
                user_id = msg.get("user_id")
                user_name = msg.get("user_name", "Usuario desconocido")
                contenido = msg.get("contenido", "Sin contenido")
                if user_id:
                    user = guild.get_member(user_id)
                    if user:
                        await recovery_channel.send(f"**{user.name}**: {contenido}")
                    else:
                        await recovery_channel.send(f"**{user_name}**: {contenido}")
                else:
                    await recovery_channel.send(f"**{user_name}**: {contenido}")
        else:
            await recovery_channel.send("El ticket no tiene mensajes.")

        embed = discord.Embed(
            title="Opciones de Recuperación",
            description="Selecciona una opción:",
            color=discord.Color.blue()
        )
        embed.add_field(name="🔄 Reintegrar Usuario", value="Reintegra al usuario al ticket y mueve el canal a la categoría de tickets.", inline=False)
        embed.add_field(name="❌ Cerrar Transcripción", value="Cierra la transcripción y elimina este canal.", inline=False)

        view = RecoveryOptionsView(self.bot, ticket_id, recovery_channel)
        await recovery_channel.send(embed=embed, view=view)

        await interaction.response.send_message(f"Ticket {ticket_id} reabierto en {recovery_channel.mention}", ephemeral=True)
        await log_event(self.bot, guild, f"🔄 Ticket Reabierto: {interaction.user.name} ha reabierto el ticket {ticket_id} en {recovery_channel.mention}")

        # Programar la eliminación del canal después de 5 minutos
        self.bot.loop.call_later(300, lambda: self.bot.loop.create_task(recovery_channel.delete()))

    @reopen.autocomplete('ticket_id')
    async def reopen_autocomplete(self, interaction: discord.Interaction, current: str):
        tickets_cerrados = self.bot.tickets["cerrados"]
        return [
            app_commands.Choice(name=ticket_id, value=ticket_id)
            for ticket_id in tickets_cerrados.keys()
            if current.lower() in ticket_id.lower()
        ]

class RecoveryOptionsView(discord.ui.View):
    def __init__(self, bot, ticket_id, recovery_channel):
        super().__init__(timeout=None)  # Asegúrate de que no haya timeout
        self.bot = bot
        self.ticket_id = ticket_id
        self.recovery_channel = recovery_channel
        self.delete_task = self.bot.loop.call_later(300, lambda: self.bot.loop.create_task(recovery_channel.delete()))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("No tienes permisos para interactuar con este botón.", ephemeral=True)
        return False

    @discord.ui.button(label="Reintegrar Usuario", style=discord.ButtonStyle.primary, custom_id="reintegrar_usuario")
    async def reintegrar_usuario(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket = self.bot.tickets["cerrados"].get(self.ticket_id)
        if not ticket:
            await interaction.response.send_message(f"No se encontró el ticket con UUID: {self.ticket_id}", ephemeral=True)
            return

        guild = interaction.guild
        categoria = self.bot.config.get('ticket_categoria', None)
        category = discord.utils.get(guild.categories, id=int(categoria))
        if category is None:
            await interaction.response.send_message("No se encontró la categoría para mover el ticket.", ephemeral=True)
            return

        author_name = ticket.get("creado_por")
        author = discord.utils.get(guild.members, name=author_name)
        if not author:
            await interaction.response.send_message(f"No se encontró al autor del ticket: {author_name}", ephemeral=True)
            return

        overwrites = self.recovery_channel.overwrites
        overwrites[author] = discord.PermissionOverwrite(read_messages=True)
        await self.recovery_channel.edit(category=category, overwrites=overwrites)
        await interaction.response.send_message(f"El ticket {self.ticket_id} ha sido movido a la categoría de tickets y el usuario {author.mention} ha sido reintegrado.", ephemeral=True)

        # Cancelar la tarea de eliminación automática
        self.delete_task.cancel()
        await log_event(self.bot, guild, f"🔄 Usuario Reintegrado: {author.mention} ha sido reintegrado al ticket {self.ticket_id} y el canal ha sido movido a la categoría de tickets.")

    @discord.ui.button(label="Cerrar Transcripción", style=discord.ButtonStyle.danger, custom_id="cerrar_transcripcion")
    async def cerrar_transcripcion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.recovery_channel.delete()
        await interaction.response.send_message(f"El canal de recuperación {self.recovery_channel.name} ha sido eliminado.", ephemeral=True)
        await log_event(self.bot, interaction.guild, f"❌ Canal Eliminado: {interaction.user.name} ha eliminado el canal de recuperación {self.recovery_channel.name}")

async def reclamar_ticket(interaction: discord.Interaction, ticket_id: str, bot):
    ticket = bot.tickets["abiertos"].get(ticket_id)
    if not ticket:
        await interaction.response.send_message("Ticket no encontrado.", ephemeral=True)
        return

    ticket["estado"] = "reclamado"
    ticket["reclamado_por"] = interaction.user.name
    save_tickets(bot.tickets)
    await interaction.response.send_message(f"Ticket {ticket_id} reclamado por {interaction.user.name}.", ephemeral=True)
    await log_event(bot, interaction.guild, f"📝 Ticket Reclamado: {interaction.user.name} ha reclamado el ticket {ticket_id}")
async def cerrar_ticket(interaction: discord.Interaction, ticket_id: str, bot):
    ticket = bot.tickets["abiertos"].pop(ticket_id, None)
    if not ticket:
        await interaction.response.send_message("Ticket no encontrado.", ephemeral=True)
        return

    channel = discord.utils.get(interaction.guild.channels, id=ticket["id"])
    await log_event(bot, interaction.guild, f"❌ Ticket Cerrado: {interaction.user.name} ha cerrado el ticket {ticket_id}")
    if channel:
        await channel.delete()

    bot.tickets["cerrados"][ticket_id] = ticket
    save_tickets(bot.tickets)
    await interaction.response.send_message(f"Ticket {ticket_id} cerrado y canal eliminado.", ephemeral=True)

async def poner_en_espera(interaction: discord.Interaction, ticket_id: str, bot):
    ticket = bot.tickets["abiertos"].pop(ticket_id, None)
    if not ticket:
        await interaction.response.send_message("Ticket no encontrado.", ephemeral=True)
        return

    bot.tickets["en_espera"][ticket_id] = ticket
    save_tickets(bot.tickets)
    await log_event(bot, interaction.guild, f"⏸️ Ticket en Espera: {interaction.user.name} ha puesto en espera el ticket {ticket_id}")
    await interaction.response.send_message(f"Ticket {ticket_id} puesto en espera.", ephemeral=True)

def save_tickets(tickets):
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))
    bot.add_view(TicketView(bot))
    bot.add_view(RecoveryOptionsView(bot, "default_id", None))  # Asegúrate de que la vista tenga un custom_id y no tenga timeout