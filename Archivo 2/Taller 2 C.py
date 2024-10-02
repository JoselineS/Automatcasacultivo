from machine import Pin, ADC
from time import sleep

pot = ADC(Pin(15))
pot.width(ADC.WIDTH_11BIT)
while True:
    pot_value = pot.read()
    print(pot_value)
    sleep(0.5)