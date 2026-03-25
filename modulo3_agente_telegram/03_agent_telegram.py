import pandas as pd
import requests
import os
import time
import sys
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() 
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", 
    api_key=OPENROUTER_KEY
)

# ─── INTELIGENCIA POR ZONA (datos del notebook 01_operational_diagnosis) ───
# Beta = coeficiente de sensibilidad lluvia→ratio (regresión lineal)
# fleet_avg = repartidores promedio conectados
# demand_surge / supply_surge = % incremento bajo lluvia vs seco
ZONE_INTELLIGENCE = {
    "Santiago": {
        "beta": 0.27, "fleet_avg": 4.58,
        "demand_surge": 110.6, "supply_surge": 8.7,
        "threshold": 1.2,
        "adjacent": ["Carretera Nacional", "Santa Catarina"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 85, "ALTO": 78, "MEDIO": 70},
        "historical": "Ratio alcanza 2.8 en seco. Solo 4.58 repartidores base, demanda sube 110% con lluvia pero oferta solo 8.7%."
    },
    "Carretera Nacional": {
        "beta": 0.21, "fleet_avg": 5.72,
        "demand_surge": 115.5, "supply_surge": 19.5,
        "threshold": 1.2,
        "adjacent": ["Santiago", "MTY_Guadalupe"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 85, "ALTO": 78, "MEDIO": 70},
        "historical": "Mayor surge de demanda en la ciudad (+115.5%), oferta reacciona solo 19.5%. Corredor abierto con clusters fast-food."
    },
    "MTY_Apodaca_Huinalá": {
        "beta": 0.16, "fleet_avg": 4.68,
        "demand_surge": 108.1, "supply_surge": 33.7,
        "threshold": 2.0,
        "adjacent": ["Apodaca Centro", "Escobedo"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Tercera zona más vulnerable (β=0.16). Flota baja (4.68), zona industrial/logística norte."
    },
    "Escobedo": {
        "beta": 0.10, "fleet_avg": 7.34,
        "demand_surge": 107.5, "supply_surge": 39.6,
        "threshold": 2.0,
        "adjacent": ["MTY_Apodaca_Huinalá", "San Nicolás"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Suburbio norte residencial. Oferta reacciona bien (+39.6%) pero demanda sube 107%."
    },
    "Santa Catarina": {
        "beta": 0.08, "fleet_avg": 8.02,
        "demand_surge": 99.4, "supply_surge": 28.0,
        "threshold": 2.0,
        "adjacent": ["San Pedro", "Cumbres Poniente"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Suburbio oeste en terreno elevado (~150m). Oferta limitada (+28%) comparada con otras zonas estándar."
    },
    "San Pedro": {
        "beta": 0.07, "fleet_avg": 13.21,
        "demand_surge": 106.9, "supply_surge": 38.6,
        "threshold": 2.0,
        "adjacent": ["Centro", "Santa Catarina"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Zona con ticket alto y buena flota (13.21). Riesgo moderado, surge equilibrado."
    },
    "Centro": {
        "beta": 0.06, "fleet_avg": 15.63,
        "demand_surge": 106.0, "supply_surge": 39.5,
        "threshold": 2.0,
        "adjacent": ["Independencia", "Mitras Centro"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Flota más grande (15.63). Alta densidad comercial/residencial, absorbe bien los picos."
    },
    "San Nicolás": {
        "beta": 0.06, "fleet_avg": 12.00,
        "demand_surge": 106.8, "supply_surge": 44.8,
        "threshold": 2.0,
        "adjacent": ["Escobedo", "La Fe"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Mejor reacción de oferta (+44.8%). Municipio residencial grande con flota robusta."
    },
    "La Fe": {
        "beta": 0.07, "fleet_avg": 7.52,
        "demand_surge": 106.9, "supply_surge": 41.6,
        "threshold": 2.0,
        "adjacent": ["San Nicolás", "MTY_Guadalupe"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Zona residencial este, oferta reacciona bien (+41.6%)."
    },
    "Independencia": {
        "beta": 0.07, "fleet_avg": 8.68,
        "demand_surge": 106.4, "supply_surge": 35.4,
        "threshold": 2.0,
        "adjacent": ["Centro", "MTY_Guadalupe"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Barrio obrero con alta densidad de órdenes. Oferta responde moderadamente (+35.4%)."
    },
    "MTY_Guadalupe": {
        "beta": 0.09, "fleet_avg": 10.91,
        "demand_surge": 109.1, "supply_surge": 40.5,
        "threshold": 2.0,
        "adjacent": ["La Fe", "Independencia"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Municipio este mixto. Surge de demanda notable (+109.1%) pero oferta compensa (+40.5%)."
    },
    "Apodaca Centro": {
        "beta": 0.08, "fleet_avg": 9.14,
        "demand_surge": 102.1, "supply_surge": 39.1,
        "threshold": 2.0,
        "adjacent": ["MTY_Apodaca_Huinalá", "Escobedo"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Suburbio industrial. Surge de demanda moderado (+102.1%), oferta responde bien."
    },
    "Mitras Centro": {
        "beta": 0.06, "fleet_avg": 10.93,
        "demand_surge": 101.6, "supply_surge": 42.5,
        "threshold": 2.0,
        "adjacent": ["Centro", "Cumbres Poniente"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Barrio tradicional con buen balance oferta/demanda. Menor surge de demanda (+101.6%)."
    },
    "Cumbres Poniente": {
        "beta": 0.06, "fleet_avg": 9.64,
        "demand_surge": 100.0, "supply_surge": 38.3,
        "threshold": 2.0,
        "adjacent": ["Mitras Centro", "Santa Catarina"],
        "earnings_base": 55,
        "earnings_map": {"CRÍTICO": 78, "ALTO": 70, "MEDIO": 65},
        "historical": "Zona residencial nueva oeste (~80m elevación). Demanda estable bajo lluvia (+100%)."
    },
}

# ─── CLASIFICADOR DE RIESGO ───
def clasificar_riesgo(precip, zona):
    """Clasifica el riesgo en 4 niveles basado en precipitación y sensibilidad de zona."""
    intel = ZONE_INTELLIGENCE.get(zona)
    is_sensitive = zona in ["Santiago", "Carretera Nacional"]

    if precip >= 5.0 or (is_sensitive and precip >= 3.0):
        return "CRÍTICO", "🚨"
    elif precip >= 3.0 or (is_sensitive and precip >= 1.5):
        return "ALTO", "⚠️"
    elif precip >= (intel["threshold"] if intel else 2.0):
        return "MEDIO", "⚡"
    else:
        return "BAJO", "📋"


def calcular_ventana(ahora):
    """Calcula la ventana de actuación basada en proximidad a picos de saturación."""
    hora = ahora.hour
    minuto = ahora.minute
    hora_decimal = hora + minuto / 60

    # Picos de saturación: 12:00-14:00 (almuerzo) y 19:00-21:00 (cena)
    if 10 <= hora_decimal < 12:
        mins_al_pico = int((12 - hora_decimal) * 60)
        return f"Ejecutar en los próximos {min(mins_al_pico, 30)} min — pico almuerzo (12:00) inicia en {mins_al_pico} min"
    elif 12 <= hora_decimal < 14:
        return "Ejecutar AHORA — ventana de saturación almuerzo ACTIVA (12:00-14:00)"
    elif 17 <= hora_decimal < 19:
        mins_al_pico = int((19 - hora_decimal) * 60)
        return f"Ejecutar en los próximos {min(mins_al_pico, 30)} min — pico cena (19:00) inicia en {mins_al_pico} min"
    elif 19 <= hora_decimal < 21:
        return "Ejecutar AHORA — ventana de saturación cena ACTIVA (19:00-21:00)"
    else:
        return "Ejecutar en los próximos 30 min antes de que la precipitación impacte la operación"


# ─── MEMORIA ANTI-SPAM E HISTORIAL ───
registro_alertas = {}
historial_eventos = []


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, verify=False)
        if response.status_code == 200:
            print("Mensaje enviado a Telegram")
        else:
            print(f"Error TG: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error conectando: {e}")


def generar_mensaje_ai(zona, lluvia, nivel, emoji, ratio_p, earnings_base, earnings_sug, timing, zonas_sec, historical, demand_surge, supply_surge, fleet_avg):
    """Genera el mensaje con el LLM. Todos los datos ya están calculados, el LLM solo formatea."""
    prompt_sistema = """
    Eres un formateador de alertas operacionales para Rappi Monterrey.
    Tu ÚNICO trabajo es tomar los datos pre-calculados y generar un mensaje de Telegram en HTML.

    REGLAS ESTRICTAS:
    1. NO inventes datos. Usa EXCLUSIVAMENTE los números que te doy.
    2. NO saludes, NO uses introducciones, NO agregues despedidas.
    3. Usa HTML: <b> para negritas. NO uses Markdown.
    4. El mensaje COMPLETO debe leerse en menos de 10 segundos.
    5. Usa saltos de línea entre cada sección para legibilidad.

    FORMATO EXACTO (respeta orden y emojis):

    [EMOJI] <b>ALERTA [NIVEL]: [ZONA]</b>

    <b>Contexto histórico:</b> [HISTORICAL]. Efecto Tijera: demanda +[DEMAND_SURGE]% vs oferta +[SUPPLY_SURGE]% (flota base: [FLEET_AVG] repartidores).

    <b>Previsión:</b> [LLUVIA] mm/hr en próximas 2h → ratio proyectado ~[RATIO_P].

    <b>ACCIÓN:</b> Subir earnings de <b>$[EARNINGS_BASE] → $[EARNINGS_SUG] MXN</b>.

    <b>Timing:</b> [TIMING].

    <b>Monitorear:</b> [ZONAS_SEC].
    """
    
    prompt_usuario = (
        f"Zona: {zona}\n"
        f"Nivel: {nivel}\n"
        f"Emoji: {emoji}\n"
        f"Lluvia: {lluvia} mm/hr\n"
        f"Ratio proyectado: {ratio_p}\n"
        f"Earnings base: ${earnings_base} MXN\n"
        f"Earnings sugerido: ${earnings_sug} MXN\n"
        f"Timing: {timing}\n"
        f"Zonas secundarias: {', '.join(zonas_sec)}\n"
        f"Contexto histórico: {historical}\n"
        f"Demand surge: {demand_surge}%\n"
        f"Supply surge: {supply_surge}%\n"
        f"Flota promedio: {fleet_avg}"
    )
    
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ]
    )
    return response.choices[0].message.content


def correr_agente(simulate=False):
    base_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_path, '../data/ZONE_INFO.csv'), decimal=',')
    ahora = datetime.now()

    print(f"--- Monitoreo operacional: {ahora.strftime('%H:%M')} ---\n")

    for _, row in df.iterrows():
        zona, lat, lon = row['ZONE'], row['LATITUDE_CENTER'], row['LONGITUDE_CENTER']
        
        # Verificar que la zona tiene inteligencia
        intel = ZONE_INTELLIGENCE.get(zona)
        if not intel:
            print(f"Zona {zona} sin inteligencia configurada, saltando...")
            continue

        # Open-Meteo: precipitación próximas 2 horas
        w_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&forecast_days=1'
        try:
            precip = max(requests.get(w_url).json()['hourly']['precipitation'][0:2])
        except Exception:
            precip = 0

        # Simulación para pruebas
        if simulate and zona == 'Santiago': precip = 6.5

        # Clasificar riesgo
        nivel, emoji = clasificar_riesgo(precip, zona)

        # Solo alertar si el nivel es MEDIO o superior
        if nivel == "BAJO":
            if zona in registro_alertas:
                del registro_alertas[zona]
            continue

        # Anti-spam: Evitar enviar alertas repetidas si ya hay una activa en la misma hora 
        # (o dentro de la ventana de enfriamiento de 4 horas)
        if zona in registro_alertas:
            ultima_alerta = registro_alertas[zona]
            misma_hora = (ahora.date() == ultima_alerta.date() and ahora.hour == ultima_alerta.hour)
            
            if misma_hora or ahora < ultima_alerta + timedelta(hours=4):
                print(f"Saltando {zona}: ya hay una alerta activa reciente.")
                continue

        # Calcular datos enriquecidos
        ratio_p = round(1.1 + (precip * intel["beta"]), 2)
        earnings_base = intel["earnings_base"]
        earnings_sug = intel["earnings_map"].get(nivel, 70)
        timing = calcular_ventana(ahora)
        zonas_sec = intel["adjacent"]

        # Generar y enviar mensaje
        print(f"{'='*50}")
        print(f"Generando alerta {nivel} para {zona} (precip: {precip} mm/hr)")

        mensaje = generar_mensaje_ai(
            zona=zona,
            lluvia=precip,
            nivel=nivel,
            emoji=emoji,
            ratio_p=ratio_p,
            earnings_base=earnings_base,
            earnings_sug=earnings_sug,
            timing=timing,
            zonas_sec=zonas_sec,
            historical=intel["historical"],
            demand_surge=intel["demand_surge"],
            supply_surge=intel["supply_surge"],
            fleet_avg=intel["fleet_avg"]
        )
        
        print(f"\nMensaje generado:\n{mensaje}\n")
        enviar_telegram(mensaje)
        registro_alertas[zona] = ahora
        historial_eventos.append({
            "zona": zona,
            "hora": ahora.strftime('%H:%M'),
            "nivel": nivel,
            "ratio_p": ratio_p,
            "earnings_base": earnings_base,
            "earnings_sug": earnings_sug
        })
        print(f"Alerta registrada para {zona}")

    print(f"\n--- Monitoreo completado ---")

def generar_resumen_diario():
    if not historial_eventos:
        print("No hubo eventos operativos registrados hoy.")
        return

    print("\nGenerando resumen diario con IA")
    eventos_str = "\n".join([
        f"- {e['hora']} | Zona: {e['zona']} | Nivel: {e['nivel']} | Ratio: {e['ratio_p']} | Earnings: ${e['earnings_base']} -> ${e['earnings_sug']}"
        for e in historial_eventos
    ])

    prompt_sistema = """
    Eres el Operations Manager de Rappi Monterrey reportando el final del día.
    Genera un informe ejecutivo conciso (max 10 segundos de lectura) en formato HTML para Telegram.

    REGLAS:
    1. Comienza con: <b>Resumen de Operaciones - Cierre de Día</b>
    2. Menciona la cantidad de zonas afectadas y el nivel de severidad.
    3. Resume las acciones económicas tomadas (cambio de earnings).
    4. Cierra con una breve conclusión sobre la estabilidad lograda.
    5. NO inventes eventos, limítate a los datos proporcionados.
    6. PROHIBIDO usar la etiqueta <br> o <br/>. Usa saltos de línea normales (Enter/Newline).
    7. PROHIBIDO encerrar tu respuesta en bloques de código (```html). Devuelve únicamente el texto con sus etiquetas <b> directamente.
    """

    prompt_usuario = f"A continuación los eventos operativos de hoy:\n{eventos_str}"

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ]
    )
    
    resumen = response.choices[0].message.content
    print("\nResumen enviado a Telegram:\n", resumen)
    enviar_telegram(resumen)



if __name__ == "__main__":
    print("Iniciando servicio de monitoreo...")
    try:
        while True:
            try:
                # Cambia a simulate=True para probar el modo simulado
                correr_agente(simulate=True)
            except Exception as e:
                print(f"Error en el ciclo principal: {e}")
                
            print("10 minutos de espera\n")
            time.sleep(600)
    except KeyboardInterrupt:
        print("\nInterrupción manual (Ctrl+C) detectada.")
        generar_resumen_diario()
        print("Sistema cerrado gracefully.")
        sys.exit(0)