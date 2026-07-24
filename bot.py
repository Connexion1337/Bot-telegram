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
  texto_bienvenida = f"👋 ¡Hola, {nombre}! Bienvenido al bot.\n\nUsa /menu para ver los comandos disponibles, pronto vamos a agregar funciones de argentina. ."
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
    # Usamos ipwho.is que es totalmente abierta y nunca falla
    url = f"https://ipwho.is/{ip_objetivo}"
    response = requests.get(url, timeout=6)
    data = response.json()

    if not data.get("success"):
      bot.reply_to(
          message,
          f"❌ No se pudo obtener información: {data.get('message', 'IP inválida')}",
      )
      return

    ip_res = data.get("ip", ip_objetivo)
    pais = data.get("country", "N/A")
    codigo_pais = data.get("country_code", "N/A")
    region = data.get("region", "N/A")
    ciudad = data.get("city", "N/A")
    codigo_postal = data.get("postal", "N/A")
    latitud = data.get("latitude", "N/A")
    longitud = data.get("longitude", "N/A")
    zona_horaria = data.get("timezone", {}).get("id", "N/A")
    moneda = data.get("currency", {}).get("code", "N/A")
    isp = data.get("connection", {}).get("isp", "N/A")
    asn = data.get("connection", {}).get("asn", "N/A")
    org = data.get("connection", {}).get("org", "N/A")

    conexion_tipo = data.get("type", "N/A")
    seguridad_vpn = (
        "Sí (VPN/Proxy detectado)"
        if data.get("security", {}).get("vpn")
        or data.get("security", {}).get("proxy")
        else "No (Conexión limpia)"
    )
    seguridad_hosting = (
        "Sí (Datacenter / Servidor)"
        if data.get("security", {}).get("hosting")
        else "No (Residencial)"
    )

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
        f"- Organización: {org}\n"
        f"- Sistema Autónomo (ASN): {asn}\n"
        f"- Tipo de Red: {conexion_tipo}\n\n"
        f"4. SEGURIDAD:\n"
        f"- Estado VPN/Proxy: {seguridad_vpn}\n"
        f"- Infraestructura: {seguridad_hosting}"
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
