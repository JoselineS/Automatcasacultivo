from machine import ADC, Pin
from time import sleep

# Pines ADC para cada sensor
AOUT_PINS = [34, 35, 36, 39, 32]  # Ejemplo, ajusta según tus conexiones

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

while True:
    sensor_data = ""
    
    for i, adc in enumerate(adcs):
        valor = adc.read()

        # Ajusta estos valores según la calibración de tu sensor
        valor_min = 240  # Valor mínimo de lectura del sensor
        valor_max = 600  # Valor máximo de lectura del sensor

        porcentaje_humedad = calcular_porcentaje_humedad(valor, valor_min, valor_max)

        sensor_data += "Sensor {}: Lectura: {} | Porcentaje: {:.2f}% | Estado: {}\n".format(i+1, valor, porcentaje_humedad, determinar_estado_suelo(porcentaje_humedad))

    print("Datos de sensores de humedad en el suelo")
    print(sensor_data)
    sleep(5)  # dado en segundos
    