    #Grupo B
    #Se intenta importar el módulo usocket, si falla, se importa socket
try:
    import usocket as socket
except:
    import socket

    # Se importa el módulo network
    import network
    # se importa el modulo esp
    import dht
    # se importa el modulod e tiempo 
    from time import sleep
    # se importa el modulo de pin para la conexión a la Esp32
    from machine import Pin
    # Se importa el módulo esp y se desactiva el modo de depuración
    import esp
    esp.osdebug(None)
    # Se realiza la recolección de basura para liberar memoria
    import gc
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
    # Se espera hasta que la conexión sea exitosa
    # while station.isconnected():
    #   sleep(2)
    # si la linea anerior no muestra el ip comentarla y usar esta
    while station.isconnected() == False:
        pass
    # Se imprime un mensaje indicando que la conexión fue exitosa
    print('Conexion exitosa')
    # Se imprime la configuración de la interfaz de red
    print(station.ifconfig())#estos datos nos dan la ip que sirve para visualizar servidor web

    #Dependiendo del sensor que se esta usando se descomenta una y se comenta la otra 
    sensor = dht.DHT22(Pin(23))
    #sensor = dht.DHT11(Pin(23))
    #Leds y pines a los que estan conectados 
    led = Pin(5,Pin.OUT)
    led2 = Pin(18,Pin.OUT)
    led3 = Pin(19,Pin.OUT)

    #funcion de medicion de la temperatura y humedad, y cambio en la iluminacion del led
    #en base a ciertas condiciones 
    def sensores():
        try:
            sleep(2)
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            temp_f = temp * (9/5) + 32.0
            print('Temperature: %3.1f C' %temp)
            print('Temperature: %3.1f F' %temp_f)
            print('Humidity: %3.1f %%' %hum)
    # if el cual maneja la iluminacion de los leds 
            if temp>=28.0 and temp<=32.0:
                led.on()
                led2.off()
                led3.off()
            if temp<28:
                led.off()
                led2.on()
                led3.off()
            if temp>32:
                led.off()
                led2.off()
                led3.on()   
        except OSError as e:
            print('Error al leer el sensor')#en caso de que falle la lectura del sensor 
    #funcion que contiene el html del servidor web, es lo que se mostrara en la web
    def web_page():
    #solicita los datos al sensor 
      valortemp = sensor.temperature()
      valorhum = sensor.humidity()
      html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
      <meta http-equiv="refresh" content="5">
      <style>
               html {{
                    font-family: Helvetica;
                    display: inline-block;
                    margin: 0px auto;
                    text-align: center;
                }}
                h1 {{
                    color: #0F3376;
                    padding: 2vh;
                }}
                p {{
                    font-size: 1.5rem;
                }}
                table {{
                    margin: auto;            
                }}
                td{{
                    padding: 10px ;
                }}
      </style>
      </head>
      <body>
      <h1>Temperatura y Humedad</h1>
      <h1>ESP32-Micropython</h1>
      <div class="data-container">
                  <table>
                    <tr>
                        <td>Temperatura:</td>
                        <td id="temperature">{}</td>
                    </tr>
                    <tr>
                        <td>Humedad:</td>
                        <td id="humidity">{}</td>
                    </tr>
                </table>
      <script>
            setTimeout(function() {{
                location.reload();
            }}, 5000); // Recargar la página cada 5 segundos
      </script>
      </div>

      </body></html>"""
      return html
    # Creación de un socket para la comunicación
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    # Bucle principal para gestionar las conexiones
    while True:
        conn, addr = s.accept()
        print('Tengo una conexión de %s' % str(addr))
        request = conn.recv(1024)
        print('Content = %s' % str(request))
        sensores()#llamado a la funcion de encender sensores
        response = web_page()#función de como se vera la web
        
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

