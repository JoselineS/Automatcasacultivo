# ------------------------------------
# conexion a la red wifi
try:
      import usocket as socket
except:
      import socket

import network
import dht
from machine import Pin
import esp
esp.osdebug(None)

import gc
gc.collect()
# credenciales 
ssid = 'test'
password = 'server00001'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid,password)
while station.isconnected() == False:
    pass
print('Connection successful')
print(station.ifconfig())
    #-------------------------------------

    #Funcion de como se vera la pagina web 
def web_page():
      html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
      <body><h1>Hello, World!</h1></body></html>"""
      return html

    # fin de la funcion--------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


    #Cuerpo principal------------------
while True:
      conn, addr = s.accept()
      print('Got a connection from %s' % str(addr))
      request = conn.recv(1024)
      print('Content = %s' % str(request))
      
      response = web_page()#llamado a la función de la web 
      
      
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      conn.close()

