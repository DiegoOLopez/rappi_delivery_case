import pandas as pd
import requests
from shapely.wkt import loads
from shapely.geometry import Point
import time
from datetime import datetime, timedelta

PATH_CENTERS = '../data/ZONE_INFO.csv'
PATH_POLYGONS = '../data/ZONE_POLYGONS.csv'



alertas_activas = {} 

def get_forecast(lat, lon):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&forecast_days=1'
    try:
        response = requests.get(url).json()
        return response['hourly']['precipitation']
    except Exception:
        return [0] * 24
    
def run_alert_engine(simulate_rain=False):
    df_centers = pd.read_csv(PATH_CENTERS, decimal=',')
    ahora = datetime.now()
    
    print(f"Iniciando monitoreo operacional - {ahora.strftime('%H:%M')}")

    for _, row in df_centers.iterrows():
        zone = row['ZONE']
        lat, lon = row['LATITUDE_CENTER'], row['LONGITUDE_CENTER']

        precip_data = get_forecast(lat, lon)
        max_precip = max(precip_data[0:2])

        if simulate_rain and zone == 'Santiago':
            max_precip = 7.2

        is_sensitive = zone in ['Santiago', 'Carretera Nacional']
        umbral = 1.2 if is_sensitive else 2.0

        if max_precip >= umbral:
            # --- LÓGICA DE DEDUPLICACIÓN Y ENFRIAMIENTO (2b) ---
            if zone in alertas_activas:
                ultima_alerta = alertas_activas[zone]
                # Si han pasado menos de 4 horas, saltamos esta zona
                if ahora < ultima_alerta + timedelta(hours=4):
                    continue
            
            ratio_proj = round(1.1 + (max_precip * 0.15 if is_sensitive else 0.10), 2)
            secundarias = "Carretera Nacional, Santa Catarina" if zone == "Santiago" else "Zonas colindantes"
            
            print(f"\nZona: {zone}")
            print(f"Precipitación esperada: {max_precip} mm/hr en las próximas 2 horas")
            print(f"Riesgo: ALTO (ratio proyectado ~{ratio_proj} basado en histórico)")
            print(f"Acción recomendada: subir earnings de 55 a 78 MXN en los próximos 30 min")
            print(f"Zonas secundarias a monitorear: {secundarias}")
            print("-" * 30)
            
            # Registramos la hora de esta alerta
            alertas_activas[zone] = ahora 

        else:
            # --- REGRESO A LA NORMALIDAD ---
            # Si deja de llover, eliminamos el registro para que pueda alertar de nuevo si vuelve a llover
            if zone in alertas_activas:
                del alertas_activas[zone]
            
            if not simulate_rain:
                print(f"Zona {zone}: OK ({max_precip} mm/hr)")

if __name__ == '__main__':
    # Simular lluvia
    #run_alert_engine(simulate_rain=True)

    # Ejecucion basada en datos reales
    run_alert_engine()
