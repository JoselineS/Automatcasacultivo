import network
import time
from machine import Pin, ADC, Timer
import urequests
import dht

# Configuración de la red WiFi
WIFI_SSID = 'test'
WIFI_PASSWORD = 'server00001'

# Configuración del bot de Telegram
TELEGRAM_BOT_TOKEN = '6796688769:AAGWD5XX1_IDgSL7ht4DFqLVFq_H30kbcVw'
TELEGRAM_CHAT_ID = '-1002124461151'

# Definición de variables
adcs = [ADC(0), ADC(25)]  # Ajusta los pines según tus conexiones
total_litros = 0
np = 0

# Función para conectarse a la red WiFi
def connect_wifi(ssid, password):
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        print('Conectando a WiFi...')
        wifi.active(True)
        wifi.connect(ssid, password)
        while not wifi.isconnected():
            pass
        print('Conexión exitosa a WiFi')
    return wifi

# Función para enviar mensajes a Telegram
def send_telegram_message(bot_token, chat_id, message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    try:
        response = urequests.post(url, json=params)
        response.raise_for_status()  # Lanza una excepción en caso de error HTTP
        print('Mensaje enviado a Telegram con éxito')
    except Exception as e:
        print(f'Error al enviar mensaje a Telegram: {e}')
MAX_RETRIES = 3

def send_telegram_message_with_retry(bot_token, chat_id, message):
    for _ in range(MAX_RETRIES):
        try:
            send_telegram_message(bot_token, chat_id, message)
            break
        except Exception as e:
            print(f'Error al enviar mensaje a Telegram: {e}')
            time.sleep(1)  # Espera un segundo antes de volver a intentar


# Función para leer los sensores de suelo
def read_soil_sensors(adcs):
    porcentajes = []
    for i, adc in enumerate(adcs):
        valor = adc.read()
        valor_min = 1000  # Ajusta estos valores según la calibración de tu sensor
        valor_max = 4095
        porcentaje_humedad = calcular_porcentaje_humedad(valor, valor_min, valor_max)
        porcentajes.append(porcentaje_humedad)
        print(f"Sensor {i + 1} - Lectura: {valor}, Porcentaje de humedad: {porcentaje_humedad:.2f}%, Estado del suelo: {determinar_estado_suelo(porcentaje_humedad)}")
    estado_general, porcentaje_general = calcular_estado_general(porcentajes)
    print(f"Estado general de la humedad del suelo: {estado_general}, Porcentaje general de humedad del suelo: {porcentaje_general:.2f}%")
    return porcentajes

# Función para calcular el porcentaje de humedad
def calcular_porcentaje_humedad(valor, valor_min, valor_max):
    porcentaje = (valor - valor_max) / (valor_min - valor_max) * 100.0
    return max(0, min(100, porcentaje))

# Función para determinar el estado del suelo
def determinar_estado_suelo(porcentaje):
    if porcentaje > 70:
        return "Suelo húmedo"
    elif 30 <= porcentaje <= 70:
        return "Suelo moderado"
    else:
        return "Suelo seco"

# Función para calcular el estado general de la humedad del suelo
def calcular_estado_general(porcentajes):
    promedio = sum(porcentajes) / len(porcentajes)
    if promedio > 70:
        estado_general = "Suelo generalmente húmedo"
    elif 30 <= promedio <= 70:
        estado_general = "Suelo generalmente moderado"
    else:
        estado_general = "Suelo generalmente seco"
    return estado_general, promedio

# Función de interrupción que cuenta los pulsos
def conteo(pin):
    global np
    np += 1

# Función que se ejecuta periódicamente para calcular la frecuencia y la cantidad total de litros
def freq(timer):
    global np, total_litros

    # Frecuencia en pulsos por segundo
    frec = np

    # Cálculo del flujo (Q) en Litros por minuto
    Q = frec / 7.5

    # Acumular la cantidad total de litros
    total_litros += Q / 60  # Convertir de litros por minuto a litros por segundo

    # Imprimir resultados
    print(f"Frecuencia = {frec} Hz, Flujo (Q) = {Q} Litros/minuto, Total Litros = {total_litros} Litros")

    # Reiniciar el contador de pulsos
    np = 0

# Configuración de la interrupción para el flanco de subida (rising edge)
sf = Pin(25, Pin.IN)
sf.irq(trigger=Pin.IRQ_RISING, handler=conteo)

# Configuración de los pines de los sensores UV del interior y exterior
uv_interior = ADC(12)  # Ajusta los pines según tus conexiones
uv_exterior = ADC(14)  # Ajusta los pines según tus conexiones

# Función para la lectura de los sensores UV
def uv_i():
    lectura_i = uv_interior.read()
    return lectura_i

def uv_e():
    lectura_e = uv_exterior.read()
    return lectura_e

# Función para la lectura de los sensores de temperatura y humedad del ambiente
def read_dht22(sensor, label):
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print(f'Temperatura {label}: {temp:.1f} C, Humedad {label}: {hum:.1f} %')
        return temp, hum
    except OSError as e:
        print(f'Error al leer el sensor {label}: {e}')
        return None, None

# Crear instancias de los sensores DHT22
sensor_i = dht.DHT22(Pin(4))   # Ajusta el pin según tus conexiones
sensor_e = dht.DHT22(Pin(15))  # Ajusta el pin según tus conexiones

# Configuración de la red WiFi
wifi = connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# Bucle principal
tiempo_esp = 10
while True:
    try:
        # Leer sensores de suelo
        porcentajes = read_soil_sensors(adcs)

        # Obtener lecturas de temperatura, humedad y radiación UV
        temp_i, hum_i = read_dht22(sensor_i, 'interior')
        temp_e, hum_e = read_dht22(sensor_e, 'exterior')
        uv_stri = uv_i()
        uv_stre = uv_e()

        # Enviar datos a Telegram
        message = f'Datos de sensores:\nTemperatura Interior: {temp_i:.1f}°C\nHumedad Interior: {hum_i:.1f}%\nTemperatura Exterior: {temp_e:.1f}°C\nHumedad Exterior: {hum_e:.1f}%\nUV Interior: {uv_stri}\nUV Exterior: {uv_stre}\n'
        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

        # Esperar antes de la próxima lectura
        time.sleep(tiempo_esp)
    except Exception as e:
        print(f'Error en el bucle principal: {e}')
        time.sleep(tiempo_esp)
