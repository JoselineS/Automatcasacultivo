import network
import time
from machine import RTC, Pin, SoftSPI, ADC, Timer
from sdcard import SDCard
import os
import machine
from time import sleep
import dht

# Pines ADC para cada sensor
AOUT_PINS = [34, 35, 36, 39, 32]  # Ajusta según tus conexiones
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

# Definición del pin de entrada para el sensor de flujo
sf = Pin(25, Pin.IN)
np = 0  # Número de pulsos
total_litros = 0  # Variable para almacenar la cantidad total de litros
reloj = Timer(0)

def conteo(pin):
    global np
    np += 1

def freq(timer):
    global np, total_litros
    frec = np
    Q = frec / 7.5
    total_litros += Q / 60
    #print(f"Total Litros Consumidos = {total_litros} Litros")
    np = 0

sf.irq(trigger=Pin.IRQ_RISING, handler=conteo)
reloj.init(mode=Timer.PERIODIC, period=1000, callback=freq)

def uv_i():
    uv_interior = machine.ADC(12)
    lectura_i = uv_interior.read()
    if lectura_i < 50:
        indice = "0"
        riesgo = "Ninguno"
    elif 50 <= lectura_i < 318:
        indice = "de 1 a 2"
        riesgo = "Bajo"
    elif 318 <= lectura_i < 606:
        indice = "de 3 a 5"
        riesgo = "Moderado"
    elif 606 <= lectura_i < 795:
        indice = "de 6 a 7"
        riesgo = "Alto"
    elif 795 <= lectura_i < 1079:
        indice = "de 8 a 10"
        riesgo = "Muy alto"
    else:
        indice = "11 o mas "
        riesgo = "Extremadamente alto"
    print("UV interior:", lectura_i, "Indice:", indice, "Riesgo:", riesgo)
    uv_stri = f"UV interior: {lectura_i}, Indice: {indice}, Riesgo: {riesgo}"

def uv_e():
    uv_exterior = machine.ADC(14)
    lectura_e = uv_exterior.read()
    if lectura_e < 50:
        indice = "0"
        riesgo = "Ninguno"
    elif 50 <= lectura_e < 318:
        indice = "de 1 a 2"
        riesgo = "Bajo"
    elif 318 <= lectura_e < 606:
        indice = "de 3 a 5"
        riesgo = "Moderado"
    elif 606 <= lectura_e < 795:
        indice = "de 6 a 7"
        riesgo = "Alto"
    elif 795 <= lectura_e < 1079:
        indice = "de 8 a 10"
        riesgo = "Muy alto"
    else:
        indice = "11 o mas "
        riesgo = "Extremadamente alto"
    print("UV interior:", lectura_e, "Indice:", indice, "Riesgo:", riesgo)
    uv_stre = f"UV interior: {lectura_e}, Indice: {indice}, Riesgo: {riesgo}"

def dht22():
    sensor_i = dht.DHT22(Pin(23))
    sensor_e = dht.DHT22(Pin(22))
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
        return temp_i, hum_i, temp_e, hum_e
    except OSError as e:
        print('Error al leer los sensores')
        return None, None, None, None

rtc = RTC()
(year, month, mday, _, hour, minute, second, _) = rtc.datetime()
hour -= 0

def fechahora():
    rtc = RTC()
    (year, month, mday, _, hour, minute, second, _) = rtc.datetime()
    hour -= 0
    print("Fecha: {:02d}/{:02d}/{}".format(mday, month, year))
    print("Hora: {:02d}:{:02d}:{:02d}".format(hour, minute, second))

spisd = SoftSPI(-1, miso=Pin(19), mosi=Pin(23), sck=Pin(18))
sd = SDCard(spisd, Pin(5))
os.mount(sd, "/sd")

def tarjetasd(temp_i, hum_i, temp_e, hum_e, uv_stre, uv_stri):
    try:
        date_time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, mday, hour, minute, second)

        dht_file_path = "/sd/dht_data.txt"
        with open(dht_file_path, "a") as dht_file:
            dht_file.write(f"{date_time_str},{temp_i},{hum_i},{temp_e},{hum_e}\n")

        soil_file_path = "/sd/soil_data.txt"
        with open(soil_file_path, "a") as soil_file:
            soil_file.write(f"{date_time_str},{porcentajes[0]},{porcentajes[1]},{porcentajes[2]},{porcentajes[3]},{porcentajes[4]}\n")

        uv_file_path = "/sd/uv_data.txt"
        with open(uv_file_path, "a") as uv_file:
            uv_file.write(f"{date_time_str},{uv_stre},{uv_stri}\n")
    except Exception as e:
        print("Error al escribir en la tarjeta SD:", str(e))

# funcion para 
# Configuración de pines para el relé
PIN_RELE = 26  # Ajusta según tu conexión
rele = Pin(PIN_RELE, Pin.OUT)

umbral_suelo_seco = 3  # Ajusta según tus necesidades
umbral_humedad_general = 60  # Ajusta según tus necesidades
sensores_seco_count = 0

while True:
    porcentajes = []

    for i, adc in enumerate(adcs):
        valor = adc.read()

        # Ajusta estos valores según la calibración de tu sensor
        valor_min = 1000  # Valor mínimo de lectura del sensor
        valor_max = 4095  # Valor máximo de lectura del sensor

        porcentaje_humedad = calcular_porcentaje_humedad(valor, valor_min, valor_max)
        porcentajes.append(porcentaje_humedad)

        if porcentaje_humedad < 30:  # Ajusta este umbral según tus necesidades
            sensores_seco_count += 1

    estado_general, porcentaje_general = calcular_estado_general(porcentajes)

    # Comprobar si 3 o más sensores están en estado seco para activar el relé
    if sensores_seco_count >= umbral_suelo_seco:
        # Activar el relé
        rele.value(1)
        print("Activar relé")

    # Comprobar si el estado general del suelo es húmedo para desactivar el relé
    if porcentaje_general >= umbral_humedad_general:
        # Desactivar el relé
        rele.value(0)
        print("Desactivar relé")

    sensores_seco_count = 0  # Reiniciar el contador
    sleep(1)  # dado en segundos
