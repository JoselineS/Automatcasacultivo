from machine import Pin
from time import sleep
import dht

sensor = dht.DHT22(Pin(15))

# Definir pines
pinLED_verde = Pin(4, Pin.OUT)   # LED verde para temperatura en rango
pinLED_amarillo = Pin(13, Pin.OUT)  # LED amarillo para temperatura demasiado baja
pinLED_rojo = Pin(12, Pin.OUT)   # LED rojo para temperatura demasiado alta

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
        return None

# Función para encender el LED en el pin especificado
def encender_led(pin):
    pin.value(1)  # Establecer el pin en HIGH para encender el LED

# Función para apagar el LED en el pin especificado
def apagar_led(pin):
    pin.value(0)  # Establecer el pin en LOW para apagar el LED

# Función para controlar el LED según la temperatura
def controlar_led(temperatura):
    if temperatura is not None:
        if temperatura == 30:
            # Temperatura igual a 30 °C, activar LED amarillo
            encender_led(pinLED_amarillo) #encendido
            apagar_led(pinLED_verde)
            apagar_led(pinLED_rojo)
            print('Temperatura es de 30 °C, activar LED amarillo')
            print ("")
        elif temperatura >= 32:
            # Temperatura igual o superior a 32 °C, activar LED rojo
            encender_led(pinLED_rojo) #encendido
            apagar_led(pinLED_amarillo)
            apagar_led(pinLED_verde)
            print('Temperatura mayor a 32 °C, activar LED rojo')
            print ("")
        elif temperatura <30 :
            # Temperatura menor a 30 °C, LED verde encendido
            apagar_led(pinLED_rojo)
            encender_led(pinLED_verde)
            apagar_led(pinLED_amarillo)
            print('Temperatura menor a 30 °C, LED verde encendido')
            print ("")
# Bucle principal
while True:
    temperatura_actual = leer_temperatura()
    controlar_led(temperatura_actual)
    sleep(0.5)