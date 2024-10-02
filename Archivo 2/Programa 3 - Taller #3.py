from machine import Pin, ADC, PWM
from time import sleep

# Configura el pin del LDR
ldr_pin = Pin(4)
ldr = ADC(ldr_pin)
ldr.width(ADC.WIDTH_10BIT)
led_pin = Pin(22) # Configura el pin del LED PWM
led_pwm = PWM(led_pin, freq=5000, duty=0)  # Frecuencia y ciclo de trabajo inicial

while True:
    ldr_value = ldr.read() # Lee el valor del LDR
    led_duty = int(ldr_value / 4)  # Puedes ajustar la escala según sea necesario
    led_duty = max(0, min(led_duty, 1023))  # Limita el ciclo de trabajo a un rango válido (0-1023)
    led_pwm.duty(led_duty) # Establece el ciclo de trabajo del LED PWM

    print("Sensor de luz:", ldr_value)
    print("Intensidad del LED:",led_duty)
    print(" ")
    sleep(0.3)
