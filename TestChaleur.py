from pigpio_dht import DHT11
import pigpio
import threading
import time
import paho.mqtt.client as pmc
 
gpio = 21
btn = 26
led_blanche = 5
led_bleu = 6
led_rouge = 13
temperature = 0
sensor = DHT11(gpio)
pi = pigpio.pi()
 
BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC_T = "/final/ra/t"
TOPIC_H = "/final/ra/h"
 
 
def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté au broker MQTT")
    else:
        print("Erreur de connexion MQTT :", code)
 
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.connect(BROKER, PORT)
client.loop_start()
 
def envoieInfo():
    result = sensor.read()
    if result['valid']:
        print("Température :", result['temp_c'], "°C", " Humidité : ", result['humidity'], "%")
        
        return result['temp_c'], result['humidity']
    else:
        print("rien envoyé")
        return None, None
 
def sec30():
    while True:
        temp, hum = envoieInfo()
        time.sleep(1)
        message = "Message 30 seconde"
        print(message)
        client.publish(TOPIC_T, temp)
        client.publish(TOPIC_H, hum)
        envoieInfo()
        time.sleep(10)
 
def click():
    while True:
        pi.set_mode(btn, pigpio.INPUT)
        pi.set_pull_up_down(btn, pigpio.PUD_DOWN)
        bouton = pi.read(btn)
        if bouton == 0:
            print(bouton)
            temp, hum = envoieInfo()
            if temp !=None and hum !=None:
                client.publish(TOPIC_T, int(temp))
                client.publish(TOPIC_H, int(hum))
                print("envoyé par bouton")
            time.sleep(2)
 
try:
    thread_sec = threading.Thread(target=sec30, daemon=True)
    thread_click = threading.Thread(target=click, daemon=True)
    thread_sec.start()
    thread_click.start()
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    print("stop")
    client.loop_stop()
    client.disconnect()
