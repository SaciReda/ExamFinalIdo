from pigpio_dht import DHT11
import pigpio
import threading
import time
import paho.mqtt.client as pmc

gpio = 21
btn = 26
led_blanche = 27
led_bleu = 22
led_rouge = 17
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

temp_recue = []
hum_recue = []

def on_message(client, userdata, msg):
    try:
        if msg.topic == TOPIC_T:
            temp = float(msg.payload.decode())
            temp_recue.append(temp)
        elif msg.topic == TOPIC_H:
            hum = float(msg.payload.decode())
            hum_recue.append(hum)
    except Exception as e:
        print("Erreur réception donnée:", e)

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = on_message
client.connect(BROKER, PORT)
client.loop_start()
client.subscribe(TOPIC_T)
client.subscribe(TOPIC_H)

def envoieInfo():
    result = sensor.read()
    if result['valid']:
        print("Température :", result['temp_c'], "°C", " Humidité : ", result['humidity'], "%")
        return result['temp_c'], result['humidity']
    else:
        print("rien envoyé")
        return None, None

def sec30():
    global temp_recue, hum_recue
    while True:
        temp, hum = envoieInfo()
        if temp is not None:
            client.publish(TOPIC_T, temp)
        if hum is not None:
            client.publish(TOPIC_H, hum)
        temp_recue = []
        hum_recue = []
        time.sleep(10)
        if temp is not None:
            temp_recue.append(temp)
        if hum is not None:
            hum_recue.append(hum)
        if temp is not None and temp == max(temp_recue):
            print("Temperature la plus haute ! allume led rouge")
            pi.write(led_rouge, 1)
        else:
            pi.write(led_rouge, 0)
        if hum is not None and hum == max(hum_recue):
            print("Humidite la plus haute ! allume led bleue")
            pi.write(led_bleu, 1)
        else:
            pi.write(led_bleu, 0)
        time.sleep(1)

def click():
    while True:
        pi.set_mode(btn, pigpio.INPUT)
        pi.set_pull_up_down(btn, pigpio.PUD_DOWN)
        bouton = pi.read(btn)
        if bouton == 0:
            print(bouton)
            temp, hum = envoieInfo()
            if temp != None and hum != None:
                client.publish(TOPIC_T, int(temp))
                client.publish(TOPIC_H, int(hum))
                print("envoyé par bouton")
            time.sleep(2)

try:
    pi.set_mode(led_rouge, pigpio.OUTPUT)
    pi.set_mode(led_bleu, pigpio.OUTPUT)
    thread_sec = threading.Thread(target=sec30, daemon=True)
    thread_click = threading.Thread(target=click, daemon=True)
    thread_sec.start()
    thread_click.start()
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    pi.write(led_rouge, 0)
    pi.write(led_bleu, 0)
    pi.write(led_blanche, 0)
    pi.stop()
    print("stop")
    client.loop_stop()
    client.disconnect()
