import machine
import time

def uv_i():
    # Configuración de los pines de los sensores UV
    uv_interior = machine.ADC(12)  
    lectura_i = uv_interior.read() # Asignación a variable y lectura
    if (lectura_i < 50):
        indice = "0"
        riesgo = "Ninguno"
    elif(lectura_i < 318):
        indice = "de 1 a 2"
        riesgo = "Bajo"
    elif(lectura_i < 606):
        indice = "de 3 a 5"
        riesgo = "Moderadp"
    elif(lectura_i < 795):
        indice = "de 6 a 7"
        riesgo = "Alto"
    elif(lectura_i < 1079):
        indice = "de 8 a 10"
        riesgo = "Muy alto"
    else:
        indice = "11 o mas "
        riesgo = "Extremadamente alto"
    print("UV interior:", lectura_i, "Indice:", indice, "Riesgo:", riesgo) # impresion en consola

def uv_e():
    # Configuración de los pines de los sensores UV
    uv_exterior = machine.ADC(14)  
    lectura_e = uv_exterior.read() # Asignación a variable y lectura
    if (lectura_e < 50):
        indice = "0"
        riesgo = "Ninguno"
    elif(lectura_e < 318):
        indice = "de 1 a 2"
        riesgo = "Bajo"
    elif(lectura_e < 606):
        indice = "de 3 a 5"
        riesgo = "Moderadp"
    elif(lectura_e < 795):
        indice = "de 6 a 7"
        riesgo = "Alto"
    elif(lectura_e < 1079):
        indice = "de 8 a 10"
        riesgo = "Muy alto"
    else:
        indice = "11 o mas "
        riesgo = "Extremadamente alto"
    print("UV interior:", lectura_e, "Indice:", indice, "Riesgo:", riesgo) # impresion en consola
    
while True:
    uv_i()
    #uv_e()    
    time.sleep(9)  # tiempo de entre cada lectura


