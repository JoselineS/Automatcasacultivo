import network
import time
import os
import machine
from machine import Pin, SoftSPI, ADC, Timer

import sys
from machine import Pin
from time import sleep
import dht

#---------------------------------------------------------------------
# funcion para lectura de los sensores del suelo
# Pines ADC para cada sensor
AOUT_PINS = [34, 35, 36, 39, 32]  # Ejemplo, ajusta según tus conexiones
#			  1   2  3   4    5
adcs = [ADC(Pin(pin)) for pin in AOUT_PINS]
for adc in adcs:
    adc.atten(ADC.ATTN_11DB)

def calcular_porcentaje_humedad(valor, valor_min, valor_max):
    porcentaje = (valor - valor_max) / (valor_min - valor_max) * 100.0
    return max(0, min(100, porcentaje))

def determinar_estado_suelo(porcentaje):
    if porcentaje > 70:
        return "Suelo húmedo"
    elif 30 <= porcentaje <= 70:
        return "Suelo moderado"
    else:
        return "Suelo seco"

def calcular_estado_general(porcentajes):
    promedio = sum(porcentajes) / len(porcentajes)
    if promedio > 70:
        estado_general = "Suelo generalmente húmedo"
    elif 30 <= promedio <= 70:
        estado_general = "Suelo generalmente moderado"
    else:
        estado_general = "Suelo generalmente seco"
    return estado_general, promedio

#-------------------------------------------------------------------------------------------------------
# Definición del pin de entrada para el sensor de flujo
sf = Pin(25, Pin.IN)
# Inicialización de variables
np = 0  # Número de pulsos
total_litros = 0  # Variable para almacenar la cantidad total de litros
# Creación de un objeto Timer para manejar el reloj
reloj = Timer(0)

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
    #print(f"Frecuencia = {frec} Hz, Flujo (Q) = {Q} Litros/minuto, Total Litros = {total_litros} Litros")
    #print(f"Total Litros Consumidos = {total_litros} Litros")

    # Reiniciar el contador de pulsos
    np = 0

# Configuración de la interrupción para el flanco de subida (rising edge)
sf.irq(trigger=Pin.IRQ_RISING, handler=conteo)

# Inicialización del temporizador para llamar a la función freq cada 1000 milisegundos (1 segundo)
reloj.init(mode=Timer.PERIODIC, period=1000, callback=freq)


#---------------------------------------------------------------------------------------------------------------
# funcion para lectura de los sensores de rayos ultravioletas 
def uv_i():
    # Configuración de los pines de los sensores UV del interior
    uv_interior = machine.ADC(12)  #conectado al pin 12 de la esp32
    lectura_i = uv_interior.read() # Asignación a variable y lectura
    if (lectura_i < 50):
        indice = "0"
        riesgo = "Ninguno"
    elif(lectura_i < 318):
        indice = "de 1 a 2"
        riesgo = "Bajo"
    elif(lectura_i < 606):
        indice = "de 3 a 5"
        riesgo = "Moderadp"
    elif(lectura_i < 795):
        indice = "de 6 a 7"
        riesgo = "Alto"
    elif(lectura_i < 1079):
        indice = "de 8 a 10"
        riesgo = "Muy alto"
    else:
        indice = "11 o mas "
        riesgo = "Extremadamente alto"
    print("UV interior:", lectura_i, "Indice:", indice, "Riesgo:", riesgo) # impresion en consola
    uv_stri = f"UV interior: {lectura_i}, Indice: {indice}, Riesgo: {riesgo}"

def uv_e():
    # Configuración de los pines de los sensores UV del eterior 
    uv_exterior = machine.ADC(14)  #conectado al pin 4 de la esp32
    lectura_e = uv_exterior.read() # Asignación a variable y lectura
    if (lectura_e < 50):
        indice = "0"
        riesgo = "Ninguno"
    elif(lectura_e < 318):
        indice = "de 1 a 2"
        riesgo = "Bajo"
    elif(lectura_e < 606):
        indice = "de 3 a 5"
        riesgo = "Moderadp"
    elif(lectura_e < 795):
        indice = "de 6 a 7"
        riesgo = "Alto"
    elif(lectura_e < 1079):
        indice = "de 8 a 10"
        riesgo = "Muy alto"
    else:
        indice = "11 o mas "
        riesgo = "Extremadamente alto"
    print("UV interior:", lectura_e, "Indice:", indice, "Riesgo:", riesgo) # impresion en consola
    uv_stre = f"UV interior: {lectura_e}, Indice: {indice}, Riesgo: {riesgo}"
    

#--------------------------------------------------------------------------------------------------
# Funcion para la lectura de los sensores de temperatura y humedad del ambiente
def read_dht22(sensor, label):
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print(f'Temperatura {label}: {temp:.1f} C')
        print(f'Humedad {label}: {hum:.1f} %')
    except OSError as e:
        print(f'Error al leer el sensor {label}: {e}')

def dht22():
    sensor_i = dht.DHT22(Pin(4))
    sensor_e = dht.DHT22(Pin(15))
    
    # Leer datos del sensor interior
    read_dht22(sensor_i, 'interior')
    
    # Leer datos del sensor exterior
    read_dht22(sensor_e, 'exterior')
#---------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------
# bucle principal
tiempo_esp = 10
while True:
    porcentajes = []

    for i, adc in enumerate(adcs):
        valor = adc.read()

        # Ajusta estos valores según la calibración de tu sensor
        valor_min = 1000  # Valor mínimo de lectura del sensor
        valor_max = 4095  # Valor máximo de lectura del sensor

        porcentaje_humedad = calcular_porcentaje_humedad(valor, valor_min, valor_max)
        porcentajes.append(porcentaje_humedad)

    estado_general, porcentaje_general = calcular_estado_general(porcentajes)

    # Obtener lecturas de temperatura, humedad y radiación UV
    temp_i, hum_i = read_dht22(sensor_i, 'interior')
    temp_e, hum_e = read_dht22(sensor_e, 'exterior')
    uv_stri = uv_i()
    uv_stre = uv_e()

    # Crear instancias de los sensores DHT22
    sensor_i = dht.DHT22(Pin(4))
    sensor_e = dht.DHT22(Pin(15))

    # Leer datos del sensor interior DHT22
    sensor_i.measure()
    temp_i = sensor_i.temperature()
    hum_i = sensor_i.humidity()

    # Leer datos del sensor exterior DHT22
    sensor_e.measure()
    temp_e = sensor_e.temperature()
    hum_e = sensor_e.humidity()

    # Leer datos de los sensores UV
    uv_stri = uv_i()
    uv_stre = uv_e()

    # Envío de datos a Telegram
    message = f'Datos de sensores:\nTemperatura Interior: {temp_i:.1f}°C\nHumedad Interior: {hum_i:.1f}%\nTemperatura Exterior: {temp_e:.1f}°C\nHumedad Exterior: {hum_e:.1f}%\nUV Interior: {uv_stri}\nUV Exterior: {uv_stre}\n'
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)

    # Esperar antes de la próxima lectura
    time.sleep(tiempo_esp)