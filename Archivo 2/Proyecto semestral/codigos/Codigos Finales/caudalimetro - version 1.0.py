from machine import Pin, Timer

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
    print(f"Total Litros Consumidos = {total_litros} Litros")

    # Reiniciar el contador de pulsos
    np = 0

# Configuración de la interrupción para el flanco de subida (rising edge)
sf.irq(trigger=Pin.IRQ_RISING, handler=conteo)

# Inicialización del temporizador para llamar a la función freq cada 1000 milisegundos (1 segundo)
reloj.init(mode=Timer.PERIODIC, period=1000, callback=freq)


"""
Frecuencia de pulsos (Hz) = 7.5Q, donde Q es el caudal en Litros/minuto
Caudal (Litros/hora) = (Frecuencia de pulsos x 60 minutos) / 7.5Q

En otras palabras:

Frecuencia del Sensor (Hz) = 7.5 * Q (Litros/minuto)
Litros = Q * tiempo transcurrido (segundos) / 60 (segundos/minuto)
Litros = (Frecuencia (Pulsos/segundo) / 7.5) * tiempo transcurrido (segundos) / 60
Litros = Pulsos / (7.5 * 60)
Detrás del Telón
"""
