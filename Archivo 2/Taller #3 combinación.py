from machine import Pin, PWM
from time import sleep

frequency = 4000
led =PWM(Pin(22), frequency)

while True:
    for duty_cycle in range (1,1024):
        led.duty(duty_cycle)
        print(duty_cycle)
        sleep(0.1)