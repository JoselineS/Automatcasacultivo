try:
    import usocket as socket
except:
    import socket

import network  # Se importa el módulo network
import dht # se importa el modulo esp
from time import sleep # se importa el modulod e tiempo
from machine import Pin # se importa el modulo de pin para la conexión a la Esp32
import esp # Se importa el módulo esp y se desactiva el modo de depuración
esp.osdebug(None)
        
import gc # Se realiza la recolección de basura para liberar memoria
gc.collect()

# Se especifican las credenciales de la red WiFi
ssid = 'test'
password = 'server00001'

        # Se crea una instancia de la clase WLAN del módulo network
station = network.WLAN(network.STA_IF)
        # Se activa la interfaz de estación (modo cliente)
station.active(True)
        # Se intenta conectar a la red WiFi con las credenciales proporcionadas
station.connect(ssid, password)
while station.isconnected() == False:
    pass
print('Conexion exitosa') # Se imprime un mensaje indicando que la conexión fue exitosa
        # Se imprime la configuración de la interfaz de red
print(station.ifconfig())#estos datos nos dan la ip que sirve para visualizar servidor web
        
sensor = dht.DHT22(Pin(15))
        # Definir pines
pinLED_verde = Pin(4, Pin.OUT)   # LED verde para temperatura en rango
pinLED_amarillo = Pin(13, Pin.OUT)  # LED amarillo para temperatura demasiado baja
pinLED_rojo = Pin(12, Pin.OUT)   # LED rojo para temperatura demasiado alta

    # ----------------------------------------------------------------------------------------
        # Función para leer la temperatura
def leer_temperatura():
        try:
            sleep(2)
            sensor.measure()
            temperatura = sensor.temperature()
            humedad = sensor.humidity()
            print('Temperatura: %3.1f C' %temperatura)
            print('Humedad: %3.1f %%' %humedad)
        # condicional para controlar los leds
            if temperatura == 30:
                # Temperatura igual a 30 °C, activar LED amarillo
                pinLED_amarillo.on() #encendido
                pinLED_rojo.off()
                pinLED_verde.off()
                print('Temperatura es de 30 °C, activar LED amarillo')
                print ("")
            elif temperatura >= 32:
                # Temperatura igual o superior a 32 °C, activar LED rojo
                pinLED_rojo.on() #encendido
                pinLED_amarillo.off()
                pinLED_verde.off()
                print('Temperatura mayor a 32 °C, activar LED rojo')
                print ("")
            elif temperatura <30 :
                # Temperatura menor a 30 °C, LED verde encendido
                pinLED_rojo.off()
                pinLED_verde.on() #encendido
                pinLED_amarillo.off()
                print('Temperatura menor a 30 °C, LED verde encendido')
                print ("")
        except OSError as e:
                    print('Error al leer el sensor.')
    #----------------------------------------------------------------------------------------------
# funcion de pagina web
def web_page():
    valortemperatura = sensor.temperature()
    valorhumedad = sensor.humidity()

    # Lista de autores del proyecto
    autores = ["Autor1", "Autor2", "Autor3", "Autor4", "Autor5"]

    # Crear la cadena de autores para la lista horizontal
    autores_html = "<ul class='autores-list'>"
    for autor in autores:
        autores_html += "<li>{}</li>".format(autor)
    autores_html += "</ul>"

    # Establecer colores para los indicadores
    color_verde = "#2ecc71"
    color_amarillo = "#f1c40f"
    color_rojo = "#e74c3c"

    # Determinar color del rectángulo según la temperatura
    if valortemperatura < 30:
        temperatura_color = color_verde
    elif valortemperatura == 30:
        temperatura_color = color_amarillo
    else:
        temperatura_color = color_rojo

    html = """<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="5">
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            color: #333;
            text-align: center;
            margin: 0;
            padding: 0;
        }}

        header {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 10px;
        }}

        h1 {{
            color: #3498db;
            margin: 5px 0;
        }}

        .data-container {{
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px auto;
            max-width: 400px;
        }}

        table {{
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
        }}

        td, th {{
            padding: 15px;
            border-bottom: 1px solid #ddd;
        }}

        .autores-list {{
            list-style-type: none;
            padding: 0;
            display: flex;
            justify-content: center;
        }}

        .autores-list li {{
            margin: 0 10px;
        }}

        .indicador-temperatura {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }}

        .indicador-rectangulo {{
            width: 50px;
            height: 20px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Proyecto IoT</h1>
    </header>

    <div class="data-container">
        <h2>Temperatura y Humedad</h2>
        <table>
            <tr>
                <td>Temperatura:</td>
                <td>{}</td>
            </tr>
            <tr>
                <td>Humedad:</td>
                <td>{}</td>
            </tr>
        </table>
    </div>

    <!-- Indicadores de temperatura -->
    <div class="indicador-temperatura">
        <div class="indicador-rectangulo" style="background-color: {}"></div>
        <div class="indicador-rectangulo" style="background-color: {}"></div>
        <div class="indicador-rectangulo" style="background-color: {}"></div>
    </div>

    <!-- Lista de autores -->
    <div class="data-container">
        <h2>Autores del Proyecto</h2>
        {}
    </div>

    <script>
        // código para actualizar la página web
        setTimeout(function() {{
            location.reload();
        }}, 2000); // Recargar la página cada 5 segundos
    </script>
</body>
</html>""".format(valortemperatura, valorhumedad, color_verde, color_amarillo, color_rojo, autores_html)

    return html
    
                # Creación de un socket para la comunicación
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
                        
                        
    # Bucle principal para gestionar las conexiones
while True:
    try:
        conn, addr = s.accept()
        print('Tengo una conexión de %s' % str(addr))
        request = conn.recv(1024)
        #print('Content = %s' % str(request))
        leer_temperatura()#llamado a la funcion de encender sensores
        response = web_page()#función de como se vera la web

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        
        conn.sendall(response)
        conn.close()
        
    except OSError as e:
        print('Error en la conexión: %s' % str(e))
    

