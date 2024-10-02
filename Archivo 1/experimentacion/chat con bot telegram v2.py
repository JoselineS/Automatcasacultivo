from machine import ADC, Pin, Timer
from utime import localtime, sleep
import network
from urequests import post
from ujson import dumps

# Configuración de la conexión WiFi
WIFI_SSID = 'test'
WIFI_PASSWORD = 'server00001'

# Configuración del sensor de humedad
MOISTURE_SENSOR_PIN = 36
adc_moisture = ADC(Pin(MOISTURE_SENSOR_PIN))
adc_moisture.atten(ADC.ATTN_11DB)

# Configuración del caudalímetro
FLOW_SENSOR_PIN = 25
sf = Pin(FLOW_SENSOR_PIN, Pin.IN)
np = 0
reloj = Timer(0)

# Configuración de Telegram (reemplazar con tus propios valores)
TELEGRAM_BOT_TOKEN = '6796688769:AAGWD5XX1_IDgSL7ht4DFqLVFq_H30kbcVw'
TELEGRAM_CHAT_ID = '-1002124461151'

def read_moisture_sensor():
    value = adc_moisture.read()
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
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    headers = {'Content-Type': 'application/json'}

    try:
        response = post(url, data=dumps(payload), headers=headers)
        response_data = response.json()

        # Imprimir la respuesta completa de Telegram
        print("Respuesta completa de Telegram:", response_data)

        # Verificar si 'chat_id' está presente en la respuesta
        if 'chat_id' not in response_data.get('result', {}):
            raise ValueError("La respuesta de Telegram no contiene 'chat_id'.")

        if not response_data.get('ok', False):
            print("Error en la respuesta de Telegram:", response_data.get('description', ''))
        else:
            print("Mensaje combinado enviado a Telegram correctamente.")

    except ValueError as ve:
        print("Error en la respuesta de Telegram:", str(ve))
        raise  # Propagar la excepción para interrumpir el flujo del programa
    except Exception as e:
        print("Error al enviar el mensaje combinado a Telegram:", str(e))
        raise  # Propagar la excepción para interrumpir el flujo del programa




def freq(timer):
    global np
    np += 1

def calculate_flow():
    global np
    frec = np
    np = 0  # Reiniciar el contador
    Q = frec / 7.5
    return frec, Q

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        sleep(1)
    print('Conectado a la red WiFi:', wlan.ifconfig())

# Conectar a la red WiFi al inicio del programa
connect_to_wifi()

while True:
    sleep(5)  # Esperar 5 segundos después de la conexión a la red WiFi

    # Medición de humedad del suelo
    moisture_value = read_moisture_sensor()
    min_sensor_value = 240
    max_sensor_value = 600
    humidity_percentage = calculate_humidity_percentage(moisture_value, min_sensor_value, max_sensor_value)
    soil_state = determine_soil_state(humidity_percentage)

    # Medición de caudal
    frec, Q = calculate_flow()

    current_time = localtime()
    formatted_time = "{:02d}:{:02d}:{:02d}".format(current_time[3], current_time[4], current_time[5])

    # Construir mensaje para Telegram
    message_soil = "Datos de humedad del suelo:\n"\
                   "Lectura del sensor de humedad en el suelo: {}\n"\
                   "Porcentaje de humedad en el suelo: {:.2f}%\n"\
                   "Estado del suelo: {}\n".format(moisture_value, humidity_percentage, soil_state)

    mensaje_completo = "{}\n"\
                   "Mediciones del caudalímetro:\n"\
                   "Frecuencia = {} Hz y Flujo (Q) = {:.2f} Litros/minuto\n"\
                   "Hora de la medición: {}".format(message_soil, frec, Q, formatted_time)

    print(mensaje_completo)
    
    # Imprimir el TELEGRAM_CHAT_ID antes de enviar el mensaje
    print("TELEGRAM_CHAT_ID:", TELEGRAM_CHAT_ID)

    try:
        send_telegram_message(mensaje_completo)
    except Exception as e:
        print("Error al enviar el mensaje combinado a Telegram:", str(e))

    sleep(15)
