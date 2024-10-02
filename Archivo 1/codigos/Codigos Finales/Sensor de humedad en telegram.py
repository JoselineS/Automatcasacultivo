from machine import ADC, Pin
from time import sleep
import network
from utime import localtime
from urequests import post
from ujson import dumps
import gc

# Configuración de la conexión WiFi
WIFI_SSID = 'test'
WIFI_PASSWORD = 'server00001'

# Configuración del sensor de humedad
AOUT_PIN = 36
adc = ADC(Pin(AOUT_PIN))
adc.atten(ADC.ATTN_11DB)

# Configuración de Telegram (reemplazar con tus propios valores)
TELEGRAM_BOT_TOKEN = '6796688769:AAGWD5XX1_IDgSL7ht4DFqLVFq_H30kbcVw'
TELEGRAM_CHAT_ID = '-1002124461151'

def read_moisture_sensor():
    value = adc.read()
    return value

def calculate_humidity_percentage(value, min_value, max_value):
    percentage = (value - max_value) / (min_value - max_value) * 100.0
    return max(0, min(100, percentage))

def determine_soil_state(percentage):
    if percentage > 70:
        return "Húmedo"
    elif 30 <= percentage <= 70:
        return "Moderado"
    else:
        return "Seco"

def send_telegram_message(message):
    url = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_BOT_TOKEN)
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
    }
    headers = {'Content-Type': 'application/json'}
    response = post(url, data=dumps(payload), headers=headers)
    return response

# Función para conectarse a la red WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    print('Conectado a la red WiFi', WIFI_SSID)
    print("")

# Conectar a la red WiFi al inicio del programa
connect_to_wifi()

while True:
    # Ahora puedes medir y enviar datos sabiendo que la conexión WiFi está establecida
    # sensor de suelo -------------------------------------------------------------------
    moisture_value = read_moisture_sensor()
    min_sensor_value = 240
    max_sensor_value = 600
    humidity_percentage = calculate_humidity_percentage(moisture_value, min_sensor_value, max_sensor_value)
    soil_state = determine_soil_state(humidity_percentage)

    message_soil = ("Datos de humedad del suelo\n"
                    "Lectura del sensor de humedad en el suelo: {}\n"
                    "Porcentaje de humedad en el suelo: {:.2f}%\n"
                    "Estado del suelo: {}").format(moisture_value, humidity_percentage, soil_state)

    print(message_soil)

    try:
        gc.collect()
        response = send_telegram_message(message_soil)
        response_json = response.json()
        if response_json.get('ok', False):
            print("Mensaje de humedad enviado a Telegram correctamente.")
            print("")
        else:
            print("Error al enviar el mensaje de humedad a Telegram. Respuesta de la API:", response_json)
    except Exception as e:
        print("Error general al enviar el mensaje de humedad a Telegram:", str(e))

    sleep(2)  # segundos entre actualización de mediciones
    #sleep(10*60)  # minutos entre actualización de mediciones

