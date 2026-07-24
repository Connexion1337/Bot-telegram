import os
import threading
from flask import Flask
import telebot

# Inicializamos Flask para que Render mantenga el servicio web activo
app = Flask(__name__)

# Toma el token de forma segura desde las variables de entorno de Render
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@app.route("/")
def home():
  return "¡El bot de Telegram está activo!"


@bot.message_handler(commands=["start"])
def send_welcome(message):
  nombre = message.from_user.first_name
  texto_bienvenida = f"👋 **¡Hola, {nombre}! Bienvenido al bot.**\n\nPronto agregaremos más comandos sobre Argentina y mas paises etc , pon /menu para ver los comandos disponibles."
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


def run_bot():
  bot.infinity_polling()


if __name__ == "__main__":
  # Corre el bot en segundo plano
  t = threading.Thread(target=run_bot)
  t.start()

  # Levanta el servidor Flask en el puerto que exige Render
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)

