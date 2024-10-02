import network
import time
from machine import RTC
import os
from machine import Pin, SoftSPI
from sdcard import SDCard
import sys
from machine import Pin
from time import sleep
import dht

sensor = dht.DHT11(Pin(23))
WIFI_SSID = 'test'
WIFI_PASSWORD = 'server00001'

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    if not wifi.isconnected():
        print('Connecting to WiFi...')
        timeout = 0
        while not wifi.isconnected() and timeout < 10:
            print('Time remaining:', 10 - timeout)
            timeout += 1
            time.sleep(1)
        if wifi.isconnected():
            print('Connected to WiFi')
        else:
            print('Failed to connect to WiFi')
            sys.exit()

connect_wifi()



# Obtener la fecha y hora local
rtc = RTC()
(year, month, mday, _, hour, minute, second, _) = rtc.datetime()

# Corregir la zona horaria
hour -= 0

# Imprimir la fecha y hora
# print("Fecha: {:02d}/{:02d}/{}".format(mday, month, year))
# print("Hora: {:02d}:{:02d}:{:02d}".format(hour, minute, second))
def fechahora():
    rtc = RTC()
    (year, month, mday, _, hour, minute, second, _) = rtc.datetime()

    # Corregir la zona horaria
    hour -= 0

    # Imprimir la fecha y hora
    print("Fecha: {:02d}/{:02d}/{}".format(mday, month, year))
    print("Hora: {:02d}:{:02d}:{:02d}".format(hour, minute, second))

# Configuración de la interfaz SPI para la SD
spisd = SoftSPI(-1, miso=Pin(19), mosi=Pin(23), sck=Pin(18))

# Inicialización de la tarjeta SD
sd = SDCard(spisd, Pin(5))
os.mount(sd, "/sd")
def tarjetasd():
    # Intentar escribir la fecha y hora en el archivo
    try:
    # Montar la tarjeta SD

    # Crear una cadena de texto con la fecha y hora
        date_time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, mday, hour, minute, second)

    # Ruta del archivo en la tarjeta SD
        file_path = "/sd/fecha_hora.txt"

        # Escribir la fecha y hora en el archivo
        with open(file_path, "w") as file:
            file.write(date_time_str)
#             file.write(date_time_str + '\n')
#             file.write('Temperature: %3.1f C\n' % temp)
#             file.write('Temperature: %3.1f F\n' % temp_f)
#             file.write('Humidity: %3.1f %%\n' % hum)
        print("Fecha y hora escritas en la tarjeta SD con éxito.")
                # Desmontar la tarjeta SD
        #os.umount("/sd")
        #print("Tarjeta SD desmontada.")
    except Exception as e:
        print("Error al escribir en la tarjeta SD:", e)
   # finally:
def temhum():
    try:
        sleep(2)
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        temp_f = temp * (9/5) + 32.0
        print('Temperature: %3.1f C' %temp)
        print('Temperature: %3.1f F' %temp_f)
        print('Humidity: %3.1f %%' %hum)
    except OSError as e:
        print('Failed to read sensor.')
    
        
tiempo_esp = 10
while True:
    fechahora()
    temhum()
    tarjetasd()
    time.sleep(tiempo_esp)
    
    
