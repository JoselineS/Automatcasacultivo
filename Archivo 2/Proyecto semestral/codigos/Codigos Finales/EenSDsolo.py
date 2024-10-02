import network
import time
from machine import RTC
import os
import machine
from machine import Pin, SoftSPI, ADC, Timer
from sdcard import SDCard
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
def dht22():
    sensor_i = dht.DHT22(Pin(23)) #conectado al pin 23 de la esp32 - sensor interior
    sensor_e = dht.DHT22(Pin(22)) #conectado al pin 22 de la esp32 - sensor exterior
    try:
        sensor_i.measure()
        sensor_e.measure()
        temp_i = sensor_i.temperature()
        hum_i = sensor_i.humidity()
        print('Temperatura interior: %3.1f C' %temp_i)
        print('Humedad interior: %3.1f %%' %hum_i)
        temp_e = sensor_e.temperature()
        hum_e = sensor_e.humidity()
        print('Temperatura exterior: %3.1f C' %temp_e)
        print('Humedad exterior: %3.1f %%' %hum_e)
    except OSError as e:
        print('Error al leer los sensores')
    return None, None, None, None
#---------------------------------------------------------------------------------------------------


# Obtener la fecha y hora local de la rtc
rtc = RTC()
(year, month, mday, _, hour, minute, second, _) = rtc.datetime()
# Corregir la zona horaria
hour -= 0
def fechahora():
    rtc = RTC()
    (year, month, mday, _, hour, minute, second, _) = rtc.datetime()
    # Corregir la zona horaria
    hour -= 0
    # Imprimir la fecha y hora
    print("Fecha: {:02d}/{:02d}/{}".format(mday, month, year))
    print("Hora: {:02d}:{:02d}:{:02d}".format(hour, minute, second))


#----------------------------------------------------------------------------------------------------
# Configuración de la interfaz SPI para la SD
spisd = SoftSPI(-1, miso=Pin(19), mosi=Pin(23), sck=Pin(18)) #pines de la RTC
# Inicialización de la tarjeta SD
sd = SDCard(spisd, Pin(5))
# Montar la tarjeta SD
os.mount(sd, "/sd")
def tarjetasd(temp_i, hum_i, temp_e, hum_e, uv_stre, uv_stri, porcentajes, total_litros):
    try:
        date_time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, mday, hour, minute, second)
        
        # Guardar datos de los sensores DHT22 en un archivo
        dht_file_path = "/sd/dht_data.txt"
        with open(dht_file_path, "a") as dht_file:
            dht_file.write(f"{date_time_str},{temp_i},{hum_i},{temp_e},{hum_e}\n")
        
        # Guardar datos de los sensores de suelo en un archivo
        soil_file_path = "/sd/soil_data.txt"
        with open(soil_file_path, "a") as soil_file:
            soil_file.write(f"{date_time_str},{','.join(map(str, porcentajes))}\n")
        
        # Guardar datos de los sensores UV en un archivo
        uv_file_path = "/sd/uv_data.txt"
        with open(uv_file_path, "a") as uv_file:
            uv_file.write(f"{date_time_str},{uv_stri},{uv_stre}\n")
        
        # Guardar datos del caudalímetro en un archivo
        flow_file_path = "/sd/caudalimetro_data.txt"
        with open(flow_file_path, "a") as flow_file:
            flow_file.write(f"{date_time_str},{total_litros}\n")
        
        print("Datos guardados correctamente.")
    
    except Exception as e:
        print("Error al escribir en la tarjeta SD:", e)
#----------------------------------------------------------------------
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

#         print("Sensor {}".format(i + 1))
#         print("Lectura: {}".format(valor))
#         print("Porcentaje de humedad: {:.2f} %".format(porcentaje_humedad))
#         print("Estado del suelo:", determinar_estado_suelo(porcentaje_humedad))
#         print("")

    estado_general, porcentaje_general = calcular_estado_general(porcentajes)
#     print("Estado general de la humedad del suelo:", estado_general)
#     print("Porcentaje general de humedad del suelo: {:.2f} %".format(porcentaje_general))
#     print("")
    sleep(1)  # dado en segundos
#     print("Datos de Sensores de humedad en el suelo:")
    
#-------------------------------------------------------------------------------------------
    fechahora()
    #temhum()
    uv_stre = uv_e
    uv_stri = uv_i
    temp_i, hum_i, temp_e, hum_e = dht22()
    tarjetasd(temp_i, hum_i, temp_e, hum_e, uv_stre, uv_stri)
    time.sleep(tiempo_esp)
#----------------------------------------------------------------------