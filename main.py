import discord
from discord.ext import commands
import json
from rich.console import Console
from rich.table import Table

console = Console()

# Cargar el archivo JSON con codificación utf-8
with open('config.json', encoding='utf-8') as f:
    config = json.load(f)

# Cargar el archivo de tickets
try:
    with open('tickets.json', encoding='utf-8') as f:
        tickets = json.load(f)
except FileNotFoundError:
    tickets = {"abiertos": {}, "cerrados": {}, "en_espera": {}, "setup_message_id": None}

products = config.get('products', {})

color = 0x4287f5

bot = commands.Bot(command_prefix="s1!", intents=discord.Intents.all())

bot.config = config
bot.products = products
bot.tickets = tickets

async def load_cogs():
    await bot.load_extension("cogs.products")
    await bot.load_extension("cogs.tickets")
    await bot.load_extension("cogs.events")
    await bot.load_extension("cogs.voz")
    await bot.load_extension("cogs.automod")
    await bot.load_extension("cogs.registros")
    await bot.load_extension("cogs.punish")
    await bot.load_extension("cogs.telegram")
@bot.event
async def on_ready():
    await load_cogs()
    tickets_abiertos = len(bot.tickets["abiertos"])
    compras_realizadas = sum(1 for product in bot.products.values() if "ventas" in product for _ in product["ventas"])
    productos_totales = len(bot.products)
    categorias_productos = ", ".join({config["categoria"] for categoria in bot.config.values()})
    
    # Obtener datos del servidor
    guild_id = 1304230407092572241
    cliente_rol_id = 1321371192019652668
    guild = bot.get_guild(guild_id)
    
    if guild:
        clientes_con_rol = len([member for member in guild.members if cliente_rol_id in [role.id for role in member.roles]])
        usuarios_en_servidor = guild.member_count
    else:
        clientes_con_rol = "Servidor no encontrado"
        usuarios_en_servidor = "Servidor no encontrado"
    
    # Sincronizar comandos
    try:
        synced_commands = await bot.tree.sync()
        comandos_sincronizados = len(synced_commands)
    except Exception as e:
        comandos_sincronizados = f"Error: {str(e)}"

    # Crear tabla
    table = Table(title="Plykara Shop System v1", title_style="bold cyan", show_header=True, header_style="bold magenta")
    table.add_column("Información", justify="center")
    table.add_column("Valor", justify="center")
    
    # Agregar filas a la tabla
    table.add_row("Tickets Abiertos", str(tickets_abiertos))
    table.add_row("Compras Realizadas", str(compras_realizadas))
    table.add_row("Productos Totales", str(productos_totales))
    table.add_row("Categorías de Productos", categorias_productos or "Ninguna")
    table.add_row("Clientes con Rol", str(clientes_con_rol))
    table.add_row("Usuarios en el Servidor", str(usuarios_en_servidor))
    table.add_row("Comandos Sincronizados", str(comandos_sincronizados))

    # Mostrar la tabla
    console.print(table)
    
    from cogs.tickets import TicketView, TicketActionView  # Importar las vistas desde el módulo de tickets
    bot.add_view(TicketView(bot))  # Registrar la vista persistente
    for ticket_id in bot.tickets["abiertos"]:
        bot.add_view(TicketActionView(bot, ticket_id))  # Registrar las vistas de acciones de tickets abiertos
    
    print(f"Bot conectado como: {bot.user}")

bot.run(config["token"])