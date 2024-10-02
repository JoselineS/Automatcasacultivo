from machine import ADC, Pin, Timer
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

# Configuración del caudalímetro
sf = Pin(25, Pin.IN)
np = 0
reloj = Timer(0)

# Configuración de Telegram (reemplazar con tus propios valores)
TELEGRAM_BOT_TOKEN = '6796688769:AAGWD5XX1_IDgSL7ht4DFqLVFq_H30kbcVw'
TELEGRAM_CHAT_ID = '-1002124461151'

# Variable global para almacenar el mensaje del caudal
message_flow = ""

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

# Función para manejar interrupciones del caudalímetro
def conteo(pin):
    global np
    np += 1

# Función para calcular la frecuencia y enviar mensaje a Telegram
def freq(timer):
    global np, message_flow

    # Frecuencia en pulsos por segundo
    frec = np

    # Cálculo del flujo (Q) en Litros por minuto
    Q = frec / 7.5

    # Actualizar mensaje_flow
    message_flow = f"Frecuencia = {frec} Hz, Flujo (Q) = {Q} Litros/minuto"

    try:
        gc.collect()
        send_telegram_message(message_flow)
        print("Mensaje de caudal enviado a Telegram.")
        print("")
    except Exception as e:
        print("Error al enviar el mensaje de caudal a Telegram:", str(e))

    # Reiniciar el contador de pulsos
    np = 0

# Función para conectarse a la red WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    print('Conectado a la red WiFi')

    # Inicialización del temporizador para llamar a la función freq cada 1000 milisegundos (1 segundo)
    reloj.init(mode=Timer.PERIODIC, period=1000, callback=freq)

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

    # Datos del caudalímetro --------------------------------------------------------------
    # El envío del mensaje de caudal ahora se realiza dentro de la función freq

    sleep(2)  # minutos entre actualización de mediciones
