import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime
from cogs.utils import update_ticket_embed  # Importar la función desde utils.py
from cogs.tickets import TicketView

color = discord.Color.blue()

class ProductDescriptionModal(discord.ui.Modal, title="Configuración del Producto"):
    titulo = discord.ui.TextInput(label="Título del producto", placeholder="Ingrese el título del producto")
    descripcion = discord.ui.TextInput(label="Descripción del producto", placeholder="Ingrese la descripción del producto")
    imagen_url = discord.ui.TextInput(label="URL de la imagen del producto", placeholder="Ingrese la URL de la imagen del producto", required=False)

    def __init__(self, bot, channel_name, config_message, tipo_producto, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.channel_name = channel_name
        self.config_message = config_message
        self.tipo_producto = tipo_producto

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.titulo.value, description=self.descripcion.value, color=color)
        if self.imagen_url.value:
            embed.set_image(url=self.imagen_url.value)

        # Detalles del producto
        if self.tipo_producto == "moneda_virtual":
            embed.add_field(
                name="📦 Detalles del Producto",
                value=(
                    "• **Cantidad de Robux:** Desde 100 hasta 10,000 Robux.\n"
                    "• **Entrega:** Instantánea o en menos de 24 horas.\n"
                    "• **Garantía:** 24 horas después de la compra."
                ),
                inline=False,
            )
            embed.add_field(
                name="📜 Instrucciones de Compra",
                value=(
                    "1️⃣ Abre un ticket en el canal correspondiente: <#{}>.\n"
                    "2️⃣ Indica la cantidad de Robux que deseas adquirir.\n"
                    "3️⃣ Realiza el pago utilizando uno de nuestros métodos aceptados.\n"
                    "4️⃣ Proporciona el comprobante del pago en el ticket.\n"
                    "5️⃣ Recibe tus Robux en tu cuenta de Roblox. 🎮"
                ).format(self.bot.config.get("ticket_channel_id")),
                inline=False,
            )
        elif self.tipo_producto == "cuenta_streaming":
            embed.add_field(
                name="📦 Detalles del Producto",
                value=(
                    "• **Tipo de Cuenta:** Netflix, Spotify, Disney+, etc.\n"
                    "• **Entrega:** Instantánea o en menos de 24 horas.\n"
                    "• **Garantía:** 24 horas después de la compra."
                ),
                inline=False,
            )
            embed.add_field(
                name="📜 Instrucciones de Compra",
                value=(
                    "1️⃣ Abre un ticket en el canal correspondiente: <#{}>.\n"
                    "2️⃣ Indica el tipo de cuenta que deseas adquirir.\n"
                    "3️⃣ Realiza el pago utilizando uno de nuestros métodos aceptados.\n"
                    "4️⃣ Proporciona el comprobante del pago en el ticket.\n"
                    "5️⃣ Recibe los detalles de tu cuenta de streaming. 🎬"
                ).format(self.bot.config.get("ticket_channel_id")),
                inline=False,
            )

        # Métodos de pago
        embed.add_field(
            name="💳 Métodos de Pago",
            value="Aceptamos los siguientes métodos:\n- **PayPal**\n- **Nequi**",
            inline=False,
        )

        # Nota importante
        embed.add_field(
            name="📌 Nota Importante",
            value=(
                "⚠️ **La garantía es válida únicamente durante las primeras 24 horas después de la compra.**\n"
                "⚠️ **Nos reservamos el derecho de rechazar cualquier solicitud de reembolso sin motivo válido.**\n"
                "Si tienes dudas, contáctanos mediante un ticket."
            ),
            inline=False,
        )

        # Debugging: Print the channel name to ensure it's correct
        print(f"Channel name: {self.channel_name}")

        channel = discord.utils.get(interaction.guild.channels, name=self.channel_name)
        if channel:
            view = BuyNowView(bot=self.bot)
            await channel.send(embed=embed, view=view)
            await self.config_message.delete()
            embed = discord.Embed(title="✅ Configuración Completada", description=f"La configuración del producto ha sido completada y enviada al canal {self.channel_name}.", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="❌ Error", description="No se encontró el canal para enviar la configuración.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ProductTypeSelect(discord.ui.View):
    def __init__(self, bot, channel_name, config_message):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_name = channel_name
        self.config_message = config_message

    @discord.ui.select(
        placeholder="Selecciona el tipo de producto",
        options=[
            discord.SelectOption(label="Moneda Virtual", value="moneda_virtual"),
            discord.SelectOption(label="Cuenta de Streaming", value="cuenta_streaming")
        ],
        custom_id="product_type_select"
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(ProductDescriptionModal(self.bot, self.channel_name, self.config_message, select.values[0]))

class ProductModal(discord.ui.Modal, title="Crear Producto"):
    nombre = discord.ui.TextInput(label="Nombre del producto", placeholder="Ingrese el nombre del producto")
    emoji = discord.ui.TextInput(label="Emoji del producto", placeholder="Ingrese el emoji del producto")

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        categoria = self.bot.config.get('categoria', None)
        if not categoria or not categoria.isdigit():
            embed = discord.Embed(title="⚠️ Categoría no encontrada", description=f"No existe una categoría con el nombre `{categoria}`.", color=discord.Color.red())
            embed.set_footer(text="Crea la categoría primero para proceder.")
            await interaction.response.send_message(embed=embed)
            return

        guild = interaction.guild
        channel_name = f"{self.emoji.value}│{self.nombre.value.lower()}"
        existing_channel = discord.utils.get(guild.channels, name=channel_name.lower())  # Comparar en minúsculas
        if existing_channel is None:
            new_channel = await guild.create_text_channel(name=channel_name, category=discord.utils.get(guild.categories, id=int(categoria)))
            embed = discord.Embed(
                title="🎉 Producto Creado",
                description=f"¡El canal **{self.nombre.value}** ha sido creado exitosamente!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Usa el botón de abajo para completar la configuración.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            view = ProductTypeSelect(self.bot, channel_name, config_message=None)
            config_message = await new_channel.send(embed=discord.Embed(title="Canal creado", description=f"El canal {channel_name} ha sido creado. Por favor, selecciona el tipo de producto para continuar con la configuración.", color=color), view=view)
            view.config_message = config_message

            # Almacenar la información del producto
            self.bot.products[channel_name] = {
                "id": new_channel.id,
                "nombre": self.nombre.value,
                "emoji": self.emoji.value,
                "creado_por": interaction.user.name,
                "fecha_creado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ventas": []  # Agregar el campo ventas
            }
            self.bot.config["products"] = self.bot.products
            with open('config.json', 'w') as f:
                json.dump(self.bot.config, f)
            await update_ticket_embed(guild, self.bot, TicketView)
        else:
            embed = discord.Embed(title="❌ Error", description=f"El canal para el producto {self.nombre.value} ya existe", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

class BuyNowView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    @discord.ui.button(label="Comprar Ahora! 🛒", style=discord.ButtonStyle.primary, custom_id="buy_now_button")
    async def buy_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.guild.get_channel(self.bot.config.get("ticket_channel_id"))
        if channel:
            await interaction.response.send_message(f"Por favor, dirígete al canal {channel.mention} para completar tu compra.", ephemeral=True)
        else:
            await interaction.response.send_message("No se encontró el canal de compras.", ephemeral=True)

class ProductCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def product_choices(self):
        return [
            app_commands.Choice(name=product["nombre"], value=product_id) 
            for product_id, product in self.bot.products.items()
        ]

    @app_commands.command(name="crear_producto", description="Crea un nuevo producto y su canal correspondiente.")
    async def c_product(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ProductModal(self.bot))

    @app_commands.command(name="eliminar_producto", description="Elimina un producto existente y su canal.")
    @app_commands.describe(product="El producto que deseas eliminar (selección de la lista).")
    async def d_product(self, interaction: discord.Interaction, product: str):
        choices = {choice.value: choice.name for choice in self.product_choices}
        if product not in choices:
            embed = discord.Embed(title="❌ Error", description="Producto no encontrado.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        product_info = self.bot.products.pop(product, None)
        if product_info:
            channel = discord.utils.get(interaction.guild.channels, id=product_info["id"])
            if channel:
                await channel.delete()
                embed = discord.Embed(title="🗑️ Producto Eliminado", description=f"El canal para el producto **{product_info['nombre']}** ha sido eliminado.", color=discord.Color.red())
                embed.set_footer(text="Producto eliminado correctamente.")
            else:
                embed = discord.Embed(title="❌ Error", description=f"No se encontró el canal para el producto **{product_info['nombre']}**.", color=discord.Color.red())
        else:
            embed = discord.Embed(title="❌ Error", description="Producto no encontrado.", color=discord.Color.red())
        
        self.bot.config["products"] = self.bot.products
        with open('config.json', 'w') as f:
            json.dump(self.bot.config, f)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await update_ticket_embed(interaction.guild, self.bot, TicketView)

    @d_product.autocomplete('product')
    async def product_autocomplete(self, interaction: discord.Interaction, current: str):
        return self.product_choices

async def setup(bot):
    await bot.add_cog(ProductCommands(bot))
    bot.add_view(ProductTypeSelect(bot, "default_channel", None))
    bot.add_view(BuyNowView(bot))