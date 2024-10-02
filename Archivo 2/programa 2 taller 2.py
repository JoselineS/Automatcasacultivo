from machine import Pin, ADC
from time import sleep

ldr = ADC(Pin(4))
ldr.width(ADC.WIDTH_10BIT)

while True:
    ldr_value = ldr.read()
    print(ldr_value)
    sleep(0.5)
    