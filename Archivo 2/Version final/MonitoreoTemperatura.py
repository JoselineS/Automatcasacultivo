try:
    import usocket as socket
except:
    import socket

import network
import dht
from time import sleep
from machine import Pin
import esp

esp.osdebug(None)
import gc
gc.collect()

ssid = 'test'
password = 'server00001'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
while not station.isconnected():
    pass
print('Conexión exitosa')
print(station.ifconfig())

sensor = dht.DHT22(Pin(15))
pinLED_verde = Pin(4, Pin.OUT)
pinLED_amarillo = Pin(13, Pin.OUT)
pinLED_rojo = Pin(12, Pin.OUT)


def leer_temperatura():
    try:
        sleep(2)
        sensor.measure()
        temperatura = sensor.temperature()
        humedad = sensor.humidity()
        print('Temperatura: %3.1f C' % temperatura)
        print('Humedad: %3.1f %%' % humedad)

        if temperatura == 30:
            pinLED_amarillo.on()
            pinLED_rojo.off()
            pinLED_verde.off()
            print('Temperatura es de 30 °C, activar LED amarillo')
            print("")
        elif temperatura >= 32:
            pinLED_rojo.on()
            pinLED_amarillo.off()
            pinLED_verde.off()
            print('Temperatura mayor a 32 °C, activar LED rojo')
            print("")
        elif temperatura < 30:
            pinLED_rojo.off()
            pinLED_verde.on()
            pinLED_amarillo.off()
            print('Temperatura menor a 30 °C, LED verde encendido')
            print("")
    except OSError as e:
        print('Error al leer el sensor.')


def web_page():
    valortemperatura = sensor.temperature()
    valorhumedad = sensor.humidity()

    autores = ["Carlos Ureña", "Cesar Quijada", "Caroline Bethancourth", "Osvaldo Torrero", "Jorge Mendoza", "Javier Rodríguez"]

    autores_html = "<ul class='autores-list'>"
    for autor in autores:
        autores_html += "<li>{}</li>".format(autor)
    autores_html += "</ul>"

    color_rectangulo = ""
    if valortemperatura < 30:
        color_rectangulo = "green"
    elif valortemperatura == 30:
        color_rectangulo = "yellow"
    elif valortemperatura >= 32:
        color_rectangulo = "red"

    html = """<html lang="es"> <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            font-size: 2.2em;
            background-color: #64adf5;
            color: #fafcfc;
            padding: 10px;
        }}

        h1 {{
            font-size: 2em;
            color: #f7f9fa;
            margin: 5px 0;
            
        }}
        
        h2 {{
            font-size: 1em;
            color: #0d3b69;
            margin: 5px 0;
            
        }}
        
        h3 {{
            font-size: 1.5em;
            color: #1574d4;
            margin: 5px 0;
            
        }}

        .data-container {{
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px auto;
            max-width: 600px;
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

        .indicador-rectangulo {{
            width: 50px;
            height: 20px;
            border-radius: 5px;
            margin: 10px;
            display: inline-block;
            visibility: hidden;
        }}

        #verde {{
            background-color: green;
        }}

        #amarillo {{
            background-color: yellow;
        }}

        #rojo {{
            background-color: red;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Proyecto IoT</h1>
        <h2>Servidor web  con la tarjeta ESP32 y Micro Python</h2>
    </header>

    <div class="data-container">
        <h3>Temperatura y Humedad</h3>
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

    <div class="data-container">
    <h3>Estado de los LEDs</h3>
    <div id="verde" class="indicador-rectangulo" style="visibility: {}"></div>
    <div id="amarillo" class="indicador-rectangulo" style="visibility: {}"></div>
    <div id="rojo" class="indicador-rectangulo" style="visibility: {}"></div>
    
</div>


    <div class="data-container">
        <h3>Autores del Proyecto</h3>
        {}
    </div>

    <script>
        setTimeout(function() {{
            location.reload();
        }}, 2000);

        var verde = document.getElementById('verde');
        var amarillo = document.getElementById('amarillo');
        var rojo = document.getElementById('rojo');

        if ("{}" === 'green') {{
            verde.style.visibility = 'visible';
        }} else if ("{}" === 'yellow') {{
            amarillo.style.visibility = 'visible';
        }} else if ("{}" === 'red') {{
            rojo.style.visibility = 'visible';
        }}
    </script>
</body>
</html>""".format(valortemperatura, valorhumedad, color_rectangulo, color_rectangulo, color_rectangulo, autores_html, color_rectangulo, color_rectangulo, color_rectangulo, autores_html)
    return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    try:
        conn, addr = s.accept()
        print('Tengo una conexión de %s' % str(addr))
        request = conn.recv(1024)
        leer_temperatura()
        response = web_page()

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')

        conn.sendall(response)
        conn.close()

    except OSError as e:
        print('Error en la conexión: %s' % str(e))
