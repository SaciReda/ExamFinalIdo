


from pigpio_dht import DHT11

import time
 
gpio = 21
 
sensor = DHT11(gpio)

while True:

    result = sensor.read()
    if result['valid']==True:
        print("Température :", result['temp_c'], "°C ",result['valid'])
    else:
        continue

    time.sleep(3)



 




from pigpio_dht import DHT11, DHT22
import time
import paho.mqtt.client as pmc

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/pira/T"
gpio = 21 
sensor = DHT11(gpio)        
result = sensor.read()
print(result)
def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", result)

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion

client.connect(BROKER,PORT)
client.publish(TOPIC,result)
client.disconnect()

from pigpio_dht import DHT11

import time
 
gpio = 21
 
sensor = DHT11(gpio)

while True:

    result = sensor.read()
   
    print("Température :", result['temp_c'], "°C")
    

    time.sleep(3)

