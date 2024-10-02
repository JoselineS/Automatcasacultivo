from machine import Pin, ADC, PWM
from time import sleep

# Configura el LDR (Light Dependent Resistor) en el pin 15
ldr = ADC(Pin(15))
ldr.width(ADC.WIDTH_10BIT)

led = PWM(Pin(22)) # Configura el LED PWM en el pin 22
while True:
    ldr_value = ldr.read()# Lee el valor del LDR
    led.duty(ldr_value)# ajusta la intensidad del LED basándose en el valor del LDR
    print("LDR Value:", ldr_value)
    sleep(0.1)  # Puedes ajustar el intervalo de muestreo según sea necesario
