from machine import Pin
from time import sleep
import dht

def dht22():
    sensor_i = dht.DHT22(Pin(4))
    sensor_e = dht.DHT22(Pin(15))
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
        print('Failed to read sensor.')

while True:
    dht22()
    sleep(5)
    
