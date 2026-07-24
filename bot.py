import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(8785982545:AAH1R4BLIw4qhPlQ-UCr47BLN9tIIGRTJ-U)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    nombre = message.from_user.first_name
    texto_bienvenida = f"👋 **¡Hola, {nombre}! Bienvenido al bot.**\n\nPronto agregaremos más comandos sobre Argentina."
    bot.reply_to(message, texto_bienvenida, parse_mode="Markdown")


@bot.message_handler(commands=["menu", "help"])
def show_menu(message):
    texto = (
        "🛠 **MENÚ DE HERRAMIENTAS OSINT** 🛠\n\n"
        "Comandos disponibles:\n"
        "📍 `/ip [Direccion IP]` - Geolocaliza y obtiene datos de una IP.\n"
        "📋 `/menu` - Muestra esta lista de comandos."
    )
    bot.reply_to(message, texto, parse_mode="Markdown")


@bot.message_handler(commands=["ip"])
def track_ip(message):
    try:
        ip = message.text.split()[1]
        bot.reply_to(message, f"🔍 Buscando rastros de {ip}...")

        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url).json()

        if response["status"] == "success":
            info = (
                f"🔍 **Resultados para {ip}**\n\n"
                f"📍 **País:** {response['country']}\n"
                f"🏙 **Ciudad:** {response['city']}\n"
                f"🌐 **ISP/Organización:** {response['isp']}\n"
                f"🗺 **Coordenadas:** {response['lat']}, {response['lon']}"
            )
            bot.reply_to(message, info, parse_mode="Markdown")
        else:
            bot.reply_to(
                message,
                "❌ No se pudo obtener información. Verifica que la IP sea válida.",
            )

    except IndexError:
        bot.reply_to(
            message, "⚠️ Uso correcto: `/ip 8.8.8.8`", parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"Ocurrió un error inesperado: {e}")


print("Bot iniciando operaciones...")


def run_bot():
    bot.infinity_polling()


if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

