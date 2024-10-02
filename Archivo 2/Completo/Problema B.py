from machine import Pin
from time import sleep
import dht

sensor = dht.DHT22(Pin(15))

# Definir pines
pinLED = Pin(2, Pin.OUT)  # Pin del LED integrado

# Función para leer la temperatura
def leer_temperatura():
    try:
        sleep(2)
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print('Temperatura: %3.1f C' % temp)
        print('Humedad: %3.1f %%' % hum)
        return temp
    except OSError as e:
        print('Error al leer el sensor.')
        #encender_led(pinLED)
        return None


# Función para encender el LED
def encender_led(pin):
    # Lógica para encender el LED en el pin especificado
    pin.value(1)  # Establecer el pin en HIGH para encender el LED

# Función para apagar el LED
def apagar_led(pin):
    # Lógica para apagar el LED en el pin especificado
    pin.value(0)  # Establecer el pin en LOW para apagar el LED

# Función para parpadear lentamente el LED
def parpadear_led_lento(pin):
    # Lógica para parpadear lentamente el LED en el pin especificado
    for _ in range(10):  # Parpadear 10 veces rápidamente
        encender_led(pin)
        sleep(0.8)  # Esperar 0.1 segundos
        apagar_led(pin)
        sleep(0.8)  # Esperar 0.1 segundos
    

# Función para parpadear rápidamente el LED
def parpadear_led_rapido(pin):
    # Lógica para parpadear rápidamente el LED en el pin especificado
    for _ in range(5):  # Parpadear 5 veces lentamente
        encender_led(pin)
        sleep(0.5)  # Esperar 0.5 segundos
        apagar_led(pin)
        sleep(0.5)  # Esperar 0.5 segundos

# Función para controlar el LED según la temperatura
def controlar_led(temperatura):
    if temperatura is not None:
        if 28 <= temperatura <= 32:
            # Temperatura en rango
            encender_led(pinLED)
            print('Temperatura en rango: Led Permanente')
        elif temperatura < 28:
            # Temperatura demasiado baja
            parpadear_led_lento(pinLED)
            print('Temperatura demasiado baja: Led paradenado lento')
        else:
            # Temperatura demasiado alta
            parpadear_led_rapido(pinLED)
            print('Temperatura demasiado alta: Led paradenado de advertencia')
            
# Bucle principal
while True:
    temperatura_actual = leer_temperatura()
    controlar_led(temperatura_actual)
    # Pausa o delay para evitar lecturas frecuentes y procesamiento innecesario
    sleep(0.5)