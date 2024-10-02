# codigo para leerlos datos del sensor de suelo
#version: V1.3
#Logs: se agrego el porcentaje de humedad con 2 decimales
#	   Se agrego el estado del suelo(seco,moderado,humedo)
from machine import ADC, Pin
from time import sleep

AOUT_PIN = 34  # PIN ESP32 GPIO36 (ADC0) que se conecta al pin AOUT del sensor de humedad

adc = ADC(Pin(AOUT_PIN))
adc.atten(ADC.ATTN_11DB)  # Configurar la atenuación a 11dB para un rango de voltaje de 0-3.6V

def calcular_porcentaje_humedad(valor, valor_min, valor_max):
    porcentaje = (valor - valor_max) / (valor_min - valor_max) * 100.0
    return max(0, min(100, porcentaje))  # Asegura que el porcentaje esté en el rango 0-100

def determinar_estado_suelo(porcentaje):
    if porcentaje > 70:
        return "Suelo húmedo"
    elif porcentaje >= 30 and porcentaje <= 70:
        return "Suelo moderado"
    else:
        return "Suelo seco"


while True:
    valor = adc.read()  # Lee el valor analógico del sensor

    # Ajusta estos valores según la calibración de tu sensor
    valor_min = 240  # Valor mínimo de lectura del sensor
    valor_max = 600  # Valor máximo de lectura del sensor

    porcentaje_humedad = calcular_porcentaje_humedad(valor, valor_min, valor_max)

    print("Lectura del sensor de humedad en el suelo:", valor)
    #print("Porcentaje de humedad:", porcentaje_humedad) #porcentaje con 6 decimals (por defecto)
    print("Porcentaje de humedad: {:.2f} %".format(porcentaje_humedad)) #porcentaje con 2 decimales
    print("Estado del suelo:", determinar_estado_suelo(porcentaje_humedad))
    print("")

    sleep(5) #dado en segundos
    #sleep(x * 60) #dado en minutos. reemplazar "x" por los minutos que deseamos colocar
