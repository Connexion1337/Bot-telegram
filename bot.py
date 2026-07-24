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
  texto_bienvenida = f"👋 **¡Hola, {nombre}! Bienvenido al bot.**\n\nUsa `/menu` para ver los comandos disponibles."
  bot.reply_to(message, texto_bienvenida, parse_mode="Markdown")


@bot.message_handler(commands=["menu", "help"])
def show_menu(message):
  texto = (
      "🛠 **MENÚ DE HERRAMIENTAS OSINT** 🛠\n\n"
      "Comandos disponibles:\n"
      "📍 `/ip [Direccion IP]` - Dossier OSINT máximo y total de una IP.\n"
      "📋 `/menu` - Muestra esta lista de comandos."
  )
  bot.reply_to(message, texto, parse_mode="Markdown")


@bot.message_handler(commands=["ip"])
def consultar_ip(message):
  args = message.text.split()
  if len(args) < 2:
    bot.reply_to(message, "⚠️ Ingresa una IP válida. Ejemplo: `/ip 8.8.8.8`")
    return

  ip_objetivo = args[1]

  try:
    # Solicitud con absolutamente todos los campos permitidos por la red
    url = f"http://ip-api.com/json/{ip_objetivo}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    response = requests.get(url, timeout=5)
    data = response.json()

    if data.get("status") == "fail":
      bot.reply_to(
          message,
          f"❌ No se pudo obtener información: {data.get('message', 'Desconocido')}",
      )
      return

    # Extracción total de cada variable
    ip_res = data.get("query", ip_objetivo)
    continente = data.get("continent", "N/A")
    codigo_cont = data.get("continentCode", "N/A")
    pais = data.get("country", "N/A")
    codigo_pais = data.get("countryCode", "N/A")
    region_codigo = data.get("region", "N/A")
    region_nombre = data.get("regionName", "N/A")
    ciudad = data.get("city", "N/A")
    distrito = data.get("district", "N/A")
    codigo_postal = data.get("zip", "N/A")
    latitud = data.get("lat", "N/A")
    longitud = data.get("lon", "N/A")
    zona_horaria = data.get("timezone", "N/A")
    desplazamiento = data.get("offset", "N/A")
    moneda = data.get("currency", "N/A")
    isp = data.get("isp", "N/A")
    org = data.get("org", "N/A")
    asn = data.get("as", "N/A")
    as_nombre = data.get("asname", "N/A")
    reverse_dns = data.get("reverse", "N/A")

    es_movil = (
        "Sí 📱 (Red Celular / Móvil)"
        if data.get("mobile")
        else "No (Red Fija / Cable) 💻"
    )
    es_proxy = (
        "Sí ⚠️ (VPN, Proxy o Tor detectado)"
        if data.get("proxy")
        else "No ✅ (Conexión limpia)"
    )
    es_hosting = (
        "Sí ☁️ (Servidor / Datacenter / Cloud)"
        if data.get("hosting")
        else "No (Conexión Residencial o de Usuario)"
    )

    respuesta = (
        f"🚨 [DOSSIER OSINT MÁXIMO GLOBAL] 🚨\n"
        f"IP OBJETIVO: `{ip_res}`\n\n"
        f"🌍 1. UBICACIÓN GEOGRÁFICA Y ESPACIAL:\n"
        f"🌐 Continente: {continente} ({codigo_cont})\n"
        f"🏳️ País: {pais} ({codigo_pais})\n"
        f"🗺️ Región / Provincia: {region_nombre} (Código: {region_codigo})\n"
        f"🏙️ Ciudad: {ciudad}\n"
        f"🏘️ Distrito / Localidad: {distrito}\n"
        f"📮 Código Postal: {codigo_postal}\n"
        f"📍 Coordenadas GPS: {latitud}, {longitud}\n\n"
        f"⏰ 2. ENTORNO, TIEMPO Y ECONOMÍA:\n"
        f"⌛ Zona Horaria: {zona_horaria} (Offset temporal: {desplazamiento})\n"
        f"💵 Moneda oficial: {moneda}\n\n"
        f"🏢 3. INFRAESTRUCTURA Y RED PROFUNDA:\n"
        f"📡 Proveedor de Internet (ISP): {isp}\n"
        f"🏛️ Organización Titular: {org}\n"
        f"🔢 Sistema Autónomo (ASN completo): {asn}\n"
        f"🏷️ Nombre del AS: {as_nombre}\n"
        f"🔗 DNS Inverso (Hostname): {reverse_dns}\n\n"
        f"🛡️ 4. SEGURIDAD, DISPOSITIVO Y TIPO DE NODO:\n"
        f"📱 Tipo de Red: {es_movil}\n"
        f"⚠️ Estado de Anonimato: {es_proxy}\n"
        f"☁️ Infraestructura de Servidor: {es_hosting}"
    )

    bot.reply_to(message, respuesta, parse_mode="Markdown")

  except Exception as e:
    bot.reply_to(message, f"❌ Ocurrió un error al procesar la IP: {str(e)}")


def run_bot():
  bot.infinity_polling()


if __name__ == "__main__":
  t = threading.Thread(target=run_bot)
  t.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
