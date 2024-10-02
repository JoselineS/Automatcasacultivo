# codigo para leerlos datos del sensor de suelo
#V1.0
from machine import ADC, Pin
from time import sleep_ms

AOUT_PIN = 36  # PIN ESP32 GPIO36 (ADC0) que se conecta al pin AOUT del sensor de humedad

adc = ADC(Pin(AOUT_PIN))
adc.atten(ADC.ATTN_11DB)  # Configurar la atenuación a 11dB para un rango de voltaje de 0-3.6V

while True:
    valor = adc.read()  # Lee el valor analógico del sensor

    print("Valor de humedad:", valor)

    sleep_ms(500)
