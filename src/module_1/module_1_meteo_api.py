# Importamos las librerías necesarias
import requests  # Para hacer peticiones HTTP a la API
import time      # Para manejar reintentos con pausas
import pandas as pd  # Para manipular datos tabulares
import matplotlib.pyplot as plt  # Para crear gráficos

# URL base de la API de datos meteorológicos históricos
API_URL = "https://archive-api.open-meteo.com/v1/archive?"

# Coordenadas geográficas de las ciudades que queremos analizar
COORDINATES = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}

# Variables meteorológicas que vamos a consultar
VARIABLES = [
    "temperature_2m_mean",      # Temperatura media diaria a 2 metros
    "precipitation_sum",        # Suma diaria de precipitaciones
    "wind_speed_10m_max"        # Velocidad máxima del viento a 10 metros
]

def call_api(url, params, retries=3, sleep_time=1):
    """
    Realiza una llamada a la API con reintentos en caso de error.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Received status code {response.status_code}")
        except requests.RequestException as e:
            print(f"Connection error: {e}")
        time.sleep(sleep_time)  # Espera antes de volver a intentar
    raise Exception("Failed to fetch data after retries.")

def get_data_meteo_api(city_name):
    """
    Obtiene datos meteorológicos diarios para una ciudad específica.
    """
    coords = COORDINATES[city_name]
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "start_date": "2010-01-01",
        "end_date": "2020-12-31",
        "daily": ",".join(VARIABLES),
        "timezone": "auto",
    }
    data = call_api(API_URL, params)

    # Validamos que la respuesta contiene la clave esperada
    if "daily" not in data:
        raise ValueError("API response schema has changed.")

    # Convertimos los datos en un DataFrame de pandas
    df = pd.DataFrame(data["daily"])
    df["time"] = pd.to_datetime(df["time"])  # Convertimos la columna de tiempo
    df.set_index("time", inplace=True)       # Usamos el tiempo como índice
    return df

def plot_city_weather(city_name, df):
    """
    Genera gráficos de temperatura, precipitación y viento para una ciudad.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Temperatura media mensual
    df.resample('M').mean()["temperature_2m_mean"].plot(ax=axes[0])
    axes[0].set_title(f"{city_name} - Monthly Mean Temperature (°C)")
    axes[0].set_ylabel("°C")

    # Precipitación total mensual
    df.resample('M').sum()["precipitation_sum"].plot(ax=axes[1])
    axes[1].set_title(f"{city_name} - Monthly Total Precipitation (mm)")
    axes[1].set_ylabel("mm")

    # Velocidad máxima del viento mensual
    df.resample('M').max()["wind_speed_10m_max"].plot(ax=axes[2])
    axes[2].set_title(f"{city_name} - Monthly Max Wind Speed (km/h)")
    axes[2].set_ylabel("km/h")

    plt.tight_layout()
    plt.show()

def main():
    """
    Itera sobre las ciudades definidas, obtiene los datos y genera los gráficos.
    """
    for city in COORDINATES.keys():
        print(f"Fetching data for {city}...")
        df = get_data_meteo_api(city)
        plot_city_weather(city, df)

# Punto de entrada del script
if __name__ == "__main__":
    main()
