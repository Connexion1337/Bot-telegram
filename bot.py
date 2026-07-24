import os
import threading
from flask import Flask
import requests
import telebot

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@app.route("/")
def home():
  return "¡El bot de Telegram está activo!"


@bot.message_handler(commands=["start"])
def send_welcome(message):
  nombre = message.from_user.first_name
  texto_bienvenida = f"👋 ¡Hola, {nombre}! Bienvenido al bot.\n\nUsa /menu para ver los comandos disponibles."
  bot.reply_to(message, texto_bienvenida)


@bot.message_handler(commands=["menu", "help"])
def show_menu(message):
  texto = (
      "🛠 MENÚ DE HERRAMIENTAS OSINT 🛠\n\n"
      "Comandos disponibles:\n"
      "📍 /ip [Direccion IP] - Dossier OSINT de una IP.\n"
      "📋 /menu - Muestra esta lista de comandos."
  )
  bot.reply_to(message, texto)


@bot.message_handler(commands=["ip"])
def consultar_ip(message):
  args = message.text.split()
  if len(args) < 2:
    bot.reply_to(message, "⚠️ Ingresa una IP válida. Ejemplo: /ip 8.8.8.8")
    return

  ip_objetivo = args[1]

  try:
    # Usamos ipapi.co que es sumamente estable en servidores en la nube
    url = f"https://ipapi.co/{ip_objetivo}/json/"
    response = requests.get(
        url, timeout=6, headers={"User-Agent": "Mozilla/5.0"}
    )
    data = response.json()

    if "error" in data:
      bot.reply_to(
          message,
          f"❌ No se pudo obtener información: {data.get('reason', 'IP inválida')}",
      )
      return

    ip_res = data.get("ip", ip_objetivo)
    pais = data.get("country_name", "N/A")
    codigo_pais = data.get("country_code", "N/A")
    region = data.get("region", "N/A")
    ciudad = data.get("city", "N/A")
    codigo_postal = data.get("postal", "N/A")
    latitud = data.get("latitude", "N/A")
    longitud = data.get("longitude", "N/A")
    zona_horaria = data.get("timezone", "N/A")
    moneda = data.get("currency", "N/A")
    isp = data.get("org", "N/A")
    asn = data.get("asn", "N/A")

    respuesta = (
        f"DOSSIER OSINT DE IP\n"
        f"IP OBJETIVO: {ip_res}\n\n"
        f"1. UBICACIÓN GEOGRÁFICA:\n"
        f"- País: {pais} ({codigo_pais})\n"
        f"- Región / Provincia: {region}\n"
        f"- Ciudad: {ciudad}\n"
        f"- Código Postal: {codigo_postal}\n"
        f"- Coordenadas GPS: {latitud}, {longitud}\n\n"
        f"2. ENTORNO Y MONEDA:\n"
        f"- Zona Horaria: {zona_horaria}\n"
        f"- Moneda oficial: {moneda}\n\n"
        f"3. RED E INFRAESTRUCTURA:\n"
        f"- Proveedor / ISP: {isp}\n"
        f"- Sistema Autónomo: {asn}"
    )

    bot.reply_to(message, respuesta)

  except Exception as e:
    bot.reply_to(message, f"❌ Ocurrió un error de conexión: {str(e)}")


def run_bot():
  bot.infinity_polling()


if __name__ == "__main__":
  t = threading.Thread(target=run_bot)
  t.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
