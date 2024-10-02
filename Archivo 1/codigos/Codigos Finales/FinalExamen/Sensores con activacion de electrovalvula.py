from machine import Pin, ADC, Timer
from time import sleep
import machine
import time
import dht

# -------------------------------------------------
# Define el pin para controlar la electroválvula
PIN_ELECTROVALVULA = 5
electrovalvula = Pin(PIN_ELECTROVALVULA, Pin.OUT)
electrovalvula.value(0)  # Inicialmente cerrada
# -------------------------------------------------

def uv_i():
    try:
        # Configuración de los pines de los sensores UV
        uv_interior = machine.ADC(12)  
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
    except Exception as e:
        print("Error en la función uv_i:", e)

def uv_e():
    try:
        # Configuración de los pines de los sensores UV
        uv_exterior = machine.ADC(14)  
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
    except Exception as e:
        print("Error en la función uv_e:", e)    

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
#-------------------------------------------------------------------------------------------------------

def medir_sensores_humedad_suelo():
    # Pines ADC para cada sensor
    AOUT_PINS = [34, 35, 36, 39, 32]  # definicion de los pines del sensor
    #            1   2  3   4    5 
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

    while True:
        porcentajes = []
        suelo_seco_count = 0  # Contador de sensores que marcan "Suelo seco"

        for i, adc in enumerate(adcs):
            valor = adc.read()

            valor_min = 1000  # Valor mínimo de lectura del sensor
            valor_max = 4095  # Valor máximo de lectura del sensor

            porcentaje_humedad = calcular_porcentaje_humedad(valor, valor_min, valor_max)
            porcentajes.append(porcentaje_humedad)

            print("Sensor {}".format(i + 1))
            print("Lectura: {}".format(valor))
            print("Porcentaje de humedad: {:.2f} %".format(porcentaje_humedad))
            estado_suelo = determinar_estado_suelo(porcentaje_humedad)
            print("Estado del suelo:", estado_suelo)
            print("")

            # Verifica si el sensor marca "Suelo seco"
            if estado_suelo == "Suelo seco":
                suelo_seco_count += 1

        estado_general, porcentaje_general = calcular_estado_general(porcentajes)
        print("Estado general de la humedad del suelo:", estado_general)
        print("Porcentaje general de humedad del suelo: {:.2f} %".format(porcentaje_general))
        print("")

        
        # Condicional para activar la electrovalvula
        # Control de la electroválvula
        if suelo_seco_count > 4:
            # Si más de 4 sensores marcan "Suelo seco", abrir la electroválvula
            electrovalvula.value(1)
            print("Las plantas necesitan agua, Electroválvula abierta")
        else:
            # Si todos los sensores marcan "Suelo húmedo", cerrar la electroválvula
            electrovalvula.value(0)
            print("Suficiente agua, Electroválvula cerrada")

        sleep(10)  # dado en segundos
        print("Datos de Sensores de humedad en el suelo:")


# ------------------------------------------------------------------------------------------------------

def medir_flujo_agua():
    # Definición del pin de entrada para el sensor de flujo
    sf = Pin(25, Pin.IN)

    # Inicialización de variables
    np = 0  # Número de pulsos
    total_litros = 0  # Variable para almacenar la cantidad total de litros

    # Creación de un objeto Timer para manejar el reloj
    reloj = Timer(0)

    # Función de interrupción que cuenta los pulsos
    def conteo(pin):
        nonlocal np
        np += 1

    # Función que se ejecuta periódicamente para calcular la frecuencia y la cantidad total de litros
    def freq(timer):
        nonlocal np, total_litros

        # Frecuencia en pulsos por segundo
        frec = np

        # Cálculo del flujo (Q) en Litros por minuto
        Q = frec / 7.5

        # Acumular la cantidad total de litros
        total_litros += Q / 60  # Convertir de litros por minuto a litros por segundo

        # Imprimir resultados
        #print(f"Frecuencia = {frec} Hz, Flujo (Q) = {Q} Litros/minuto, Total Litros = {total_litros} Litros")

        # Reiniciar el contador de pulsos
        np = 0

    # Configuración de la interrupción para el flanco de subida (rising edge)
    sf.irq(trigger=Pin.IRQ_RISING, handler=conteo)

    # Inicialización del temporizador para llamar a la función freq cada 1000 milisegundos (1 segundo)
    reloj.init(mode=Timer.PERIODIC, period=1000, callback=freq)

#funcion principal
while True:
    #llama a cada funcion de los sensores
    dht22()
    uv_i()
    uv_e()
    medir_flujo_agua()
    medir_sensores_humedad_suelo()
    
    
