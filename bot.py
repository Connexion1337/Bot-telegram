import os
import threading
from flask import Flask
import requests
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
  texto_bienvenida = f"👋 **¡Hola, {nombre}! Bienvenido al bot.**\n\nPronto tendra mas funciones sobre cada pais Arg,peru etc,usa /menu para ver los comandos disponibles."
  bot.reply_to(message, texto_bienvenida, parse_mode="Markdown")


@bot.message_handler(commands=["menu", "help"])
def show_menu(message):
  texto = (
      "🛠 **MENÚ DE HERRAMIENTAS OSINT** 🛠\n\n"
      "Comandos disponibles:\n"
      "📍 `/ip [Direccion IP]` - Dossier OSINT completo de una IP.\n"
      "📋 `/menu` - Muestra esta lista de comandos."
  )
  bot.reply_to(message, texto, parse_mode="Markdown")


@bot.message_handler(commands=["ip"])
def consultar_ip(message):
  args = message.text.split()
  if len(args) < 2:
    bot.reply_to(
        message,
        "⚠️ Ingresa una IP válida. Ejemplo: `/ip 8.8.8.8`",
        parse_mode="Markdown",
    )
    return

  ip_objetivo = args[1]

  try:
    url = f"https://api.ipapi.is/?q={ip_objetivo}"
    response = requests.get(url, timeout=10)
    data = response.json()

    if "error" in data:
      bot.reply_to(
          message,
          f"❌ No se pudo obtener información: {data.get('error', 'Desconocido')}",
      )
      return

    ubicacion = data.get("location", {})
    empresa = data.get("company", {})
    asn = data.get("asn", {})
    tipo_red = data.get("is", {})
    abuse = data.get("abuse", {})

    respuesta = (
        f"🕵️‍♂️ **DOSSIER OSINT COMPLETO DE IP:** `{ip_objetivo}`\n\n"
        f"🌍 **UBICACIÓN GEOGRÁFICA:**\n"
        f"🏳️ **País:** {ubicacion.get('country', 'N/A')} ({ubicacion.get('country_code', 'N/A')})\n"
        f"🏙️ **Estado / Región:** {ubicacion.get('state', 'N/A')}\n"
        f"🏘️ **Ciudad:** {ubicacion.get('city', 'N/A')}\n"
        f"📮 **Código Postal:** {ubicacion.get('zip', 'N/A')}\n"
        f"⏰ **Zona Horaria:** {ubicacion.get('timezone', 'N/A')}\n"
        f"📍 **Coordenadas:** {ubicacion.get('latitude', 'N/A')}, {ubicacion.get('longitude', 'N/A')}\n"
        f"☀️ **¿Es de día/noche?:** {'Noche 🌙' if ubicacion.get('is_dst') else 'Día ☀️'}\n\n"
        f"🏢 **INFRAESTRUCTURA Y RED:**\n"
        f"📡 **Nombre de la Compañía:** {empresa.get('name', 'N/A')}\n"
        f"🌐 **Dominio Web:** {empresa.get('domain', 'N/A')}\n"
        f"🔌 **Tipo de Red (Route):** {asn.get('route', 'N/A')}\n"
        f"🔢 **ASN (Autonomous System):** AS{asn.get('asn', 'N/A')}\n"
        f"🏛️ **Organización del AS:** {asn.get('org', 'N/A')}\n\n"
        f"🛡️ **SEGURIDAD Y ANONIMATO:**\n"
        f"🔹 **¿Es VPN?:** {'Sí ⚠️' if tipo_red.get('vpn') else 'No ✅'}\n"
        f"🔹 **¿Es Proxy?:** {'Sí ⚠️' if tipo_red.get('proxy') else 'No ✅'}\n"
        f"🔹 **¿Es Red Tor?:** {'Sí ⚠️' if tipo_red.get('tor') else 'No ✅'}\n"
        f"🔹 **¿Es Datacenter / Hosting?:** {'Sí (Servidor Cloud)' if tipo_red.get('datacenter') else 'No (Conexión Residencial/Móvil)'}\n"
        f"🔹 **¿Es Abusiva / Reportada?:** {'Sí 🚨' if tipo_red.get('abuser') else 'No (Limpia) ✅'}\n\n"
        f"📞 **CONTACTO DE ABUSOS (ISP):**\n"
        f"📧 **Email:** {abuse.get('email', 'N/A')}\n"
        f"☎️ **Teléfono:** {abuse.get('phone', 'N/A')}"
    )

    bot.reply_to(message, respuesta, parse_mode="Markdown")

  except Exception as e:
    bot.reply_to(message, f"❌ Ocurrió un error al consultar la IP: {str(e)}")


def run_bot():
  bot.infinity_polling()


if __name__ == "__main__":
  t = threading.Thread(target=run_bot)
  t.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
