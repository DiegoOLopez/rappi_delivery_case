import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # cvargamos el .env
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", 
    api_key=OPENROUTER_KEY
)

# memoria para no spammear alertas
registro_alertas = {}

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensaje 
    }
    
    try:
        # lo dejamos en false por el tema del ssl en mac
        response = requests.post(url, json=payload, verify=False)
        
        if response.status_code == 200:
            print(f"Mensaje enviado correectamente")
        else:
            print(f"Error tg: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error conectando: {e}")

def generar_mensje_ai(zona, lluvia, ratio_p, earnings_sug):
    prompt_sistema = """
    Eres un Agente asistente de Operaciones en Rappi MTY. Dame alertas muy concisas.
    REQUISITOS:
    - Nivel de roesgo (Bajo/Medio/Alto/Crítico).
    - Impacto proyectado 
    - Accion recomendada: "ej. Subir bono a X MXN".
    - Ventanna de tiempo (porm x min).
    - Zonas afectdas.
    """
    
    prompt_usuario = (f"Zona: {zona}, LLuvia: {lluvia}mm/hr, "
                     f"Ratio esperado: {ratio_p}, Sugerencia earnings: {earnings_sug} MXN.")
    
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ]
    )
    return response.choices[0].message.content

def correr_agente(simulate=False):
    # cargamos centers
    base_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_path, '../data/ZONE_INFO.csv'), decimal=',')
    ahora = datetime.now()

    print(f"--- Arrancando moniitoreo: {ahora.strftime('%H:%M')} ---")

    for _, row in df.iterrows():
        zona, lat, lon = row['ZONE'], row['LATITUDE_CENTER'], row['LONGITUDE_CENTER']
        
        # open meteo data
        w_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&forecast_days=1'
        precip = max(requests.get(w_url).json()['hourly']['precipitation'][0:2])

        if simulate and zona == 'Santiago': precip = 6.5 # forzar lluvia aca

        # decision (santiago y carr nacional son mas senisbles)
        is_sensitive = zona in ['Santiago', 'Carretera Nacional']
        umbral = 1.2 if is_sensitive else 2.0 

        if precip >= umbral:
            # eviytar spam (4hrs dif)
            if zona in registro_alertas and ahora < registro_alertas[zona] + timedelta(hours=4):
                continue
            
            # generamos alert
            ratio_p = round(1.1 + (precip * 0.15), 2)
            mensaje_ai = generar_mensje_ai(zona, precip, ratio_p, 78) # probamos con 78 de bono
            
            enviar_telegram(mensaje_ai)
            registro_alertas[zona] = ahora
            print(f"Alerta enviada a > {zona}")
        else:
            # si se quita ka lluvia receteamos
            if zona in registro_alertas:
                del registro_alertas[zona]

if __name__ == "__main__":
    # True para prubar rrapido
    correr_agente(simulate=True)