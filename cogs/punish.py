import discord
from discord.ext import commands

class Reglas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reglas", help="Muestra las reglas del servidor.")
    async def reglas(self, ctx):
        embed = discord.Embed(
            title="📘 `|` Reglas del Servidor - Tienda de Robux y Productos Digitales",
            description=(
                "¡Bienvenido a nuestra tienda! Para garantizar un entorno seguro y ordenado, te pedimos que sigas las reglas "
                "enumeradas a continuación. Estas están diseñadas para proteger a los compradores, garantizar la transparencia y "
                "mantener un ambiente agradable para todos.\n\n"
                "El incumplimiento de estas normas resultará en sanciones como advertencias, restricciones temporales o permanentes."
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        reglas = [
            "Mantén el respeto hacia todos los miembros del servidor, incluidos los clientes y el personal. No toleraremos insultos ni faltas de respeto.",
            "Está prohibido compartir contenido NSFW, ilegal, fraudulento o que promueva actividades ilícitas.",
            "No hagas spam en ningún canal, ya sea en texto o menciones excesivas a los administradores o vendedores.",
            "Evita publicar enlaces externos o invitaciones a otros servidores sin el permiso del equipo administrativo.",
            "No promociones productos o servicios ajenos a la tienda sin autorización previa.",
            "Usa cada canal según su propósito. Por ejemplo, las consultas de compra van en el canal de soporte.",
            "Queda estrictamente prohibido intentar realizar transacciones fuera del servidor para evitar estafas.",
            "No se permite el uso de lenguaje engañoso para intentar obtener productos gratuitos o descuentos indebidos.",
            "No uses múltiples cuentas para beneficiarte de promociones, eventos o para evadir sanciones.",
            "Respeta los tiempos y procedimientos de entrega de los productos. El equipo trabaja para garantizar que tu compra se complete de manera eficiente.",
            "Queda prohibido cualquier tipo de comportamiento fraudulento, como estafas, suplantación de identidad o uso de métodos de pago ilegítimos.",
            "No uses nombres de usuario o fotos de perfil que puedan ser ofensivos o engañosos en el contexto del servidor.",
            "Cualquier intento de hackeo, exploits o daño al servidor resultará en la expulsión inmediata y el bloqueo permanente.",
            "Las quejas o problemas con un producto deben tratarse directamente en los canales de soporte designados.",
            "Cumple con los [Términos de Servicio de Discord](https://discord.com/terms) y nuestras políticas internas.",
        ]

        for i, regla in enumerate(reglas, start=1):
            embed.add_field(name=f"Regla {i}", value=regla, inline=False)

        # Apartado adicional
        embed.add_field(
            name="📌 Nota Importante",
            value=(
                "Nos reservamos el derecho de añadir o remover reglas según sea necesario. Además, si detectamos comportamientos "
                "que no estén explícitamente mencionados aquí, pero que consideremos inapropiados o que vayan en contra de la "
                "moral de nuestra comunidad, tomaremos las medidas correspondientes."
            ),
            inline=False,
        )

        embed.set_thumbnail(url=ctx.guild.icon.url)  # Icono opcional
        embed.set_footer(
            text="Gracias por confiar en nuestra tienda. ¡Esperamos que tengas una gran experiencia!",
            icon_url=self.bot.user.avatar.url
        )

        await ctx.send(embed=embed)

    @commands.command(name="tos", help="Muestra los Términos de Servicio del servidor.")
    async def tos(self, ctx):
        embed = discord.Embed(
            title="📘 `|` Términos de Servicio",
            description=(
                "Los siguientes Términos de Servicio (ToS) regulan el uso de este servidor y las transacciones realizadas en él. "
                "Al participar en nuestra comunidad y adquirir productos, aceptas cumplir con estos términos y condiciones."
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        tos_list = [
            "Todos los usuarios deben actuar con respeto y profesionalismo al interactuar con el personal y otros miembros.",
            "Queda prohibido realizar discusiones públicas sobre problemas con productos o transacciones. Todo conflicto debe ser tratado mediante un ticket en los canales designados.",
            "Nos reservamos el derecho de decidir si una solicitud de reembolso tiene justificación. Cada caso será evaluado de forma individual.",
            "El tiempo de entrega puede variar dependiendo del producto. Pedimos paciencia y comprensión durante este proceso.",
            "No nos hacemos responsables por errores derivados de información incorrecta proporcionada por el cliente.",
            "Cualquier intento de fraude, abuso o mal uso de nuestros servicios resultará en la expulsión inmediata del servidor y la posible prohibición permanente.",
            "No ofrecemos soporte fuera de los canales oficiales del servidor. Abstente de contactar al personal por medios no autorizados.",
            "Todos los pagos son finales. Los reembolsos sólo se procesarán en circunstancias excepcionales, y únicamente mediante el sistema de tickets.",
            "No está permitido compartir información sensible, como comprobantes de pago, capturas de pantalla o datos personales, en los canales públicos.",
            "Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios se anunciarán en el servidor, y es responsabilidad del usuario mantenerse informado."
        ]

        for i, tos_item in enumerate(tos_list, start=1):
            embed.add_field(name=f"Término {i}", value=tos_item, inline=False)

        # Nota adicional
        embed.add_field(
            name="📌 Nota Importante",
            value=(
                "Al utilizar nuestros servicios, aceptas estos términos y condiciones. Si tienes dudas o problemas, por favor "
                "abre un ticket y nuestro equipo estará encantado de ayudarte."
            ),
            inline=False,
        )

        embed.set_thumbnail(url=ctx.guild.icon.url)  # Icono opcional
        embed.set_footer(
            text="Gracias por confiar en nuestra tienda. Tu satisfacción es nuestra prioridad.",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url,
        )

        await ctx.send(embed=embed)

    @commands.command(name="importante", help="Muestra información importante sobre la tienda.")
    async def importante(self, ctx):
        embed = discord.Embed(
            title="⚠️ `|` IMPORTANTE",
            description=(
                "Por favor, lee detenidamente esta información general sobre nuestra tienda para evitar inconvenientes."
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        # Información general
        embed.add_field(
            name="Métodos de Pago",
            value="Aceptamos los siguientes métodos de pago:\n- **PayPal**\n- **Nequi**",
            inline=False,
        )

        embed.add_field(
            name="Garantía de Productos",
            value=(
                "Nuestros productos cuentan con una **garantía de 24 horas** desde el momento de la compra. "
                "Pasado este tiempo, no se realizarán reembolsos."
            ),
            inline=False,
        )

        embed.add_field(
            name="Contactos y Reembolsos",
            value=(
                "Todo contacto relacionado con reembolsos o problemas debe realizarse a través de un **ticket** "
                "en el canal <#1321704873913221201>. No se atenderán problemas en público."
            ),
            inline=False,
        )

        embed.set_thumbnail(
            url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.set_footer(
            text="Gracias por confiar en nuestra tienda.",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reglas(bot))