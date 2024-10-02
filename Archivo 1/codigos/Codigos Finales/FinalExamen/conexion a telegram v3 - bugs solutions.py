import urequests as requests
from machine import ADC, Pin, Timer
import machine
from time import sleep
import time
import dht
import network

# Define los tokens de los bots de Telegram
TOKEN_BOT_SUELO = "6611079948:AAH81aBvL9pmFnXA8VB4spo3INBQLESIKc4"         # https://t.me/IoT_suelo_bot
TOKEN_BOT_UV = "6739077746:AAHxCQiN3Hy0b7vgCES5YKhO6YbgzJXnM9Q"            # https://t.me/IoT_UV_bot
TOKEN_BOT_FLUJO_AGUA = "6407146772:AAFwTO-xjL225hLocDTmL28RHrkOBgqABXU"    # https://t.me/IoT_caudalimetro_bot
TOKEN_BOT_DHT22 = "6941247101:AAGNo61FBSCMwewgeHfoWMkIBlrEsf7edfY"         # https://t.me/IoT_Sensoresdht22_bot

# Define el pin para controlar la electroválvula
PIN_ELECTROVALVULA = 5
electrovalvula = Pin(PIN_ELECTROVALVULA, Pin.OUT)
electrovalvula.value(0)  # Inicialmente cerrada

# Función para conectarse a la red WiFi ---------------------------------------------------------------------
def conectar_wifi(ssid, password): 
    station = network.WLAN(network.STA_IF)

    if not station.isconnected():
        print("Conectando a la red WiFi...")
        station.active(True)
        station.connect(ssid, password)

        while not station.isconnected():
            pass

    print("Conexión WiFi exitosa")
    print("Dirección IP:", station.ifconfig()[0])
# ------------------------------------------------------------------------------------------------------------


# Función para enviar mensajes a un bot de Telegram ---------------------------------------------------------------------
def enviar_mensaje(token, mensaje):
    url = "https://api.telegram.org/bot{}/sendMessage".format(token)
    payload = {"chat_id": "-1002124461151", "text": mensaje}  # Aquí va el ID del grupo: https://t.me/testproyectoesp32
    
    try:
        response = requests.post(url, json=payload)

        # Verificar el estado de la respuesta antes de continuar
        if response.status_code == 200:
            print("Mensaje enviado exitosamente.")
        else:
            print("Error al enviar mensaje a Telegram. Código de estado:", response.status_code)
    except Exception as e:
        print("Error al enviar mensaje a Telegram:", e)
    finally:
        # Cerrar la conexión y liberar recursos
        if response:
            response.close()
# ------------------------------------------------------------------------------------------------------------------------


# Configuración de los pines de los sensores UV
uv_interior = machine.ADC(12)
uv_exterior = machine.ADC(14)

# Configuración de los sensores DHT22
sensor_i = dht.DHT22(Pin(4))
sensor_e = dht.DHT22(Pin(15))

# Pines ADC para los sensores de suelo
AOUT_PINS = [34, 35, 33, 32, 27]
adcs = [ADC(Pin(pin)) for pin in AOUT_PINS]
for adc in adcs:
    adc.atten(ADC.ATTN_11DB)

# Inicialización de variables para el sensor de flujo de agua
sf = Pin(25, Pin.IN)
np = 0
total_litros = 0
reloj = Timer(0)

# Función de interrupción para contar los pulsos
def conteo(pin):
    global np
    np += 1

# Función que se ejecuta periódicamente para calcular la frecuencia y la cantidad total de litros
def freq(timer):
    global np, total_litros
    frec = np
    Q = frec / 7.5
    total_litros += Q / 60
    np = 0

# Configuración de la interrupción para el flanco de subida (rising edge)
sf.irq(trigger=Pin.IRQ_RISING, handler=conteo)

def uv_i():
    try:
        lectura_i = uv_interior.read()
        if (lectura_i < 50):
            indice = "0"
            riesgo = "Ninguno"
        elif(lectura_i < 318):
            indice = "de 1 a 2"
            riesgo = "Bajo"
        elif(lectura_i < 606):
            indice = "de 3 a 5"
            riesgo = "Moderado"
        elif(lectura_i < 795):
            indice = "de 6 a 7"
            riesgo = "Alto"
        elif(lectura_i < 1079):
            indice = "de 8 a 10"
            riesgo = "Muy alto"
        else:
            indice = "11 o mas "
            riesgo = "Extremadamente alto"
        print("UV interior:", lectura_i, "Indice:", indice, "Riesgo:", riesgo)
        
        # Enviar datos a bot de Telegram para el sensor UV interior
        mensaje_uv_i = "Datos del sensor UV interior:\n"
        mensaje_uv_i += "UV interior: {}\nIndice: {}\nRiesgo: {}".format(lectura_i, indice, riesgo)
        enviar_mensaje(TOKEN_BOT_UV, mensaje_uv_i)
    except OSError as e:
        print("Error de tiempo de espera en la función uv_i:", e)
    except Exception as e:
        print("Error en la función uv_i:", e)

def uv_e():
    try:
        lectura_e = uv_exterior.read()
        if (lectura_e < 50):
            indice = "0"
            riesgo = "Ninguno"
        elif(lectura_e < 318):
            indice = "de 1 a 2"
            riesgo = "Bajo"
        elif(lectura_e < 606):
            indice = "de 3 a 5"
            riesgo = "Moderado"
        elif(lectura_e < 795):
            indice = "de 6 a 7"
            riesgo = "Alto"
        elif(lectura_e < 1079):
            indice = "de 8 a 10"
            riesgo = "Muy alto"
        else:
            indice = "11 o mas "
            riesgo = "Extremadamente alto"
        print("UV exterior:", lectura_e, "Indice:", indice, "Riesgo:", riesgo)
        
        # Enviar datos a bot de Telegram para el sensor UV exterior
        mensaje_uv_e = "Datos del sensor UV exterior:\n"
        mensaje_uv_e += "UV exterior: {}\nIndice: {}\nRiesgo: {}".format(lectura_e, indice, riesgo)
        enviar_mensaje(TOKEN_BOT_UV, mensaje_uv_e)
    except OSError as e:
        print("Error de tiempo de espera en la función uv_e:", e)
    except Exception as e:
        print("Error en la función uv_e:", e)

# En la función medir_flujo_agua
# En la función medir_flujo_agua
def medir_flujo_agua():
    try:
        global np, total_litros  # Agrega estas líneas para indicar que estás usando las variables globales np y total_litros
        frec = np
        Q = frec / 7.5
        total_litros += Q / 60

        # Enviar datos a bot de Telegram para el sensor de flujo de agua
        mensaje_flujo_agua = "Datos del sensor de flujo de agua:\n"
        mensaje_flujo_agua += "Frecuencia = {} Hz, Flujo (Q) = {} Litros/minuto, Total Litros = {} Litros".format(frec, Q, total_litros)
        enviar_mensaje(TOKEN_BOT_FLUJO_AGUA, mensaje_flujo_agua)
    except OSError as e:
        print("Error de tiempo de espera al medir el flujo de agua:", e)
    except Exception as e:
        print("Error en la función medir_flujo_agua:", e)




def dht22():
    try:
        sensor_i.measure()
        temp_i = sensor_i.temperature()
        hum_i = sensor_i.humidity()

        sensor_e.measure()
        temp_e = sensor_e.temperature()
        hum_e = sensor_e.humidity()

        # Enviar datos a bot de Telegram para el sensor DHT22
        mensaje_dht22 = "Datos de los sensores DHT22:\n"
        mensaje_dht22 += "Temperatura interior: {:.1f} C\nHumedad interior: {:.1f} %\n".format(temp_i, hum_i)
        mensaje_dht22 += "Temperatura exterior: {:.1f} C\nHumedad exterior: {:.1f} %".format(temp_e, hum_e)
        enviar_mensaje(TOKEN_BOT_DHT22, mensaje_dht22)
    except OSError as e:
        print("Error de tiempo de espera en la función dht22:", e)
    except Exception as e:
        print("Error en la función dht22:", e)

def medir_sensores_humedad_suelo():
    try:
        porcentajes = []
        suelo_seco_count = 0  # Contador de sensores que marcan "Suelo seco"

        for i, adc in enumerate(adcs):
            valor = adc.read()
            valor_min = 1000
            valor_max = 4095

            porcentaje_humedad = (valor - valor_max) / (valor_min - valor_max) * 100.0
            porcentajes.append(porcentaje_humedad)

            estado_suelo = ""
            if porcentaje_humedad > 70:
                estado_suelo = "Suelo húmedo"
            elif 30 <= porcentaje_humedad <= 70:
                estado_suelo = "Suelo moderado"
            else:
                estado_suelo = "Suelo seco"

            if estado_suelo == "Suelo seco":
                suelo_seco_count += 1

            # Mejora en la impresión de mensajes
            print(f"Sensor {i + 1}:")
            print(f"  - Lectura: {valor}")
            print(f"  - Porcentaje de humedad: {porcentaje_humedad:.2f}%")
            print(f"  - Estado del suelo: {estado_suelo}\n")

        promedio = sum(porcentajes) / len(porcentajes)
        estado_general = ""
        if promedio > 70:
            estado_general = "Suelo generalmente húmedo"
            print("Estado general: No es necesario abrir la válvula.")
        elif 30 <= promedio <= 70:
            estado_general = "Suelo generalmente moderado"
            print("Estado general: No es necesario abrir la válvula.")
        else:
            estado_general = "Suelo generalmente seco"
            print("Estado general: Se requiere agua.")

        # Control de la electroválvula
        if suelo_seco_count > 4:
            if electrovalvula.value() == 0:
                # Válvula se abre
                electrovalvula.value(1)
                print("Electroválvula abierta")
                enviar_mensaje(TOKEN_BOT_SUELO, "La electroválvula se ha abierto.")
        else:
            if electrovalvula.value() == 1:
                # Válvula se cierra
                electrovalvula.value(0)
                print("Electroválvula cerrada")
                enviar_mensaje(TOKEN_BOT_SUELO, "La electroválvula se ha cerrado.")

        # Enviar datos a bot de Telegram para el sensor de suelo
        mensaje_suelo = "Datos de Sensores de humedad en el suelo:\n"
        for i, porcentaje in enumerate(porcentajes):
            mensaje_suelo += f"Sensor {i + 1}: {porcentaje:.2f}%\n"
        mensaje_suelo += f"Estado general: {estado_general}\n"
        enviar_mensaje(TOKEN_BOT_SUELO, mensaje_suelo)

        sleep(10)  # Dado en segundos
        print("Fin de la medición de Sensores de humedad en el suelo.")
    except Exception as e:
        print("Error en la función medir_sensores_humedad_suelo:", e)


# Función principal
def main():
    try:
        # Conectar a la red WiFi
        conectar_wifi("HUAWEI P30 lite", "pastorita22")  # Credenciales correspondientes a la red

        while True:
            # Llama a todas las funciones para obtener datos de los sensores
            dht22()  # Obtener datos de los sensores DHT22 (temperatura y humedad)
            #uv_i()   # Obtener datos del sensor UV interior
            #uv_e()   # Obtener datos del sensor UV exterior
            #medir_flujo_agua()  # Obtener datos del sensor de flujo de agua
            #medir_sensores_humedad_suelo()  # Obtener datos de los sensores de humedad en el suelo

    except Exception as e:
        # Manejar cualquier excepción que ocurra durante la ejecución
        error_message = f"Error en el programa principal: {type(e).__name__}: {str(e)}"
        print(error_message)

        # Aquí puedes agregar lógica adicional según el tipo de excepción
        if isinstance(e, OSError):
            # Manejar excepciones específicas de OSError (si es necesario)
            print("OSError: Verifica la conexión a los dispositivos hardware.")
        elif isinstance(e, network.AuthenticationError):
            # Manejar excepciones específicas de errores de autenticación en la red WiFi
            print("Error de autenticación en la red WiFi. Verifica las credenciales.")
        else:
            # Manejar otras excepciones no específicas
            print("Ocurrió una excepción no manejada. Revisa el código y los datos de entrada.")


if __name__ == "__main__":
    # Si este script se ejecuta como el programa principal, llamar a la función main
    main()

