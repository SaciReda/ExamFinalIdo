##Majorité du travail fait par Réda et Amadou mis a part la partie pour les leds et les Api
# Importation des bibliotheques
from pigpio_dht import DHT11
import pigpio
import threading
import time
import paho.mqtt.client as pmc
from flask import Flask, jsonify, request

# Initialisation des variables
gpio = 21
btn = 26
led_blanche = 27
led_bleu = 22
led_rouge = 17
temperature = 0
sensor = DHT11(gpio)
pi = pigpio.pi()

# Initialisation du Broker MQTT
BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC_T = "/final/ra/t"
TOPIC_H = "/final/ra/h"

# Fonction de connexion au broker Mqtt
def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté au broker MQTT")
    else:
        print("Erreur de connexion MQTT :", code)

temp_recue = []
hum_recue = []

# Variable globale pour activer/désactiver l'envoi
envoi_actif = True

# Fonction de reception des message
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

# Fonctionde publication de messages
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = on_message
client.connect(BROKER, PORT)
client.loop_start()
client.subscribe(TOPIC_T)
client.subscribe(TOPIC_H)

# Envoi de la température et de l'humidité
def envoieInfo():
    result = sensor.read()
    if result['valid']:
        print("Température :", result['temp_c'], "°C", " Humidité : ", result['humidity'], "%")
        return result['temp_c'], result['humidity']
    else:
        print("rien envoyé")
        return None, None

# gestion des LEDs 
def sec30():
    global temp_recue, hum_recue
    while True:
        if envoi_actif:
            pi.write(led_blanche, 1)  # LED blanche allumée si envoi actif
            # Envoi de la temperature et de lhumidite
            temp, hum = envoieInfo()
            # verifie si temp et hum ne sont pas None si il ne le sont pas il les envoies (client.publish)
            if temp != None:
                client.publish(TOPIC_T, temp)
            if hum  != None:
                client.publish(TOPIC_H, hum)
            # initialisation des listes quand on envoie les donnees de temp et hum
            temp_recue = []
            hum_recue = []
            time.sleep(10)
            # verifie si temp et hum ne sont pas None si il ne le sont pas il les ajoute a la liste 
            if temp != None:
                temp_recue.append(temp)
            if hum != None:
                hum_recue.append(hum)
            # verifie si temp et hum ne sont pas None et que NOTRE valeur soit  ==  au max(la valeur la plus haute de (*_recue)
            # si toutes les conditions sont vrai on les allumes en rouge et/ou bleu
            if temp != None and temp == max(temp_recue):
                print("Temperature la plus haute ! allume led rouge")
                pi.write(led_rouge, 1)
            else:
                pi.write(led_rouge, 0)
            if hum != None and hum == max(hum_recue):
                print("Humidite la plus haute ! allume led bleue")
                pi.write(led_bleu, 1)
            else:
                pi.write(led_bleu, 0)
            time.sleep(1)
        else:
            pi.write(led_blanche, 0)  # LED blanche éteinte si envoi désactivé
            pi.write(led_rouge, 0)
            pi.write(led_bleu, 0)
            time.sleep(0.5)

def click():
    # fonction pour le bouton 
    global envoi_actif
    while True:
        pi.set_mode(btn, pigpio.INPUT)
        pi.set_pull_up_down(btn, pigpio.PUD_DOWN)
        bouton = pi.read(btn)
        if bouton == 0:
            start = time.time()
            # Attend que le bouton soit relâché ou 2 secondes dépassées
            #
            while pi.read(btn) == 0:
                if time.time() - start > 2:
                    envoi_actif = not envoi_actif
                    print("Envoi active" if envoi_actif else "Envoi désactive")
                    pi.write(led_blanche, 1 if envoi_actif else 0)
                    while pi.read(btn) == 0:
                        time.sleep(0.05)
                    break
                time.sleep(0.05)
            else:
                # Appui court : nenvoie que si envoi_actif est True
                # Fait pas Amadou au complet()
                if envoi_actif:
                    print(bouton)
                    temp, hum = envoieInfo()
                    if temp != None and hum != None:
                        client.publish(TOPIC_T, int(temp))
                        client.publish(TOPIC_H, int(hum))
                        print("envoyé par bouton")
                # Quand cest desactive et on essaye denvoyer avec le boutton mais cest eteint il nenvoie rien
                else:
                    print("Envoi desactive, rien envoye")
            time.sleep(0.2)


app = Flask(__name__)
##créer le lien vers la page avec les données

@app.route('/donnees', methods=['GET'])
def getTemp():
    
    result = sensor.read()
    if result['valid']:
        temp = result['temp_c']
        hum = result['humidity']
        t = {}
        t['tempe'] = temp
        h = {}
        h['humid'] = hum
        ##return sous format json pour l'envoyer
        return jsonify(t, h)
    else:
        ##trouver sur internet error met le message en rouge 
        return jsonify({'error': 'capteur non valide'})
##créer le lien vers la page avec les données
@app.route('/etat', methods=['GET'])
def getEtat():
        messageEtat=0
        t = {}
        if envoi_actif==True:
            messageEtat=1

        t['etat de connexion'] = messageEtat
        
        ##return sous format json pour l'envoyer
        return jsonify(t)
    

try:
    pi.set_mode(led_rouge, pigpio.OUTPUT)
    pi.set_mode(led_bleu, pigpio.OUTPUT)
    pi.set_mode(led_blanche, pigpio.OUTPUT)
    pi.write(led_blanche, 1)
    thread_sec = threading.Thread(target=sec30, daemon=True)
    thread_click = threading.Thread(target=click, daemon=True)
    thread_sec.start()
    thread_click.start()
    # Lancer  sur le port 3000
    app.run(host='0.0.0.0', port=3000)
    ##empeche que le programme crash pour lui laisser le temps de load
    while True:
        time.sleep(2)
# eteindre les LEDs et stop le programme
except KeyboardInterrupt:
    pi.write(led_rouge, 0)
    pi.write(led_bleu, 0)
    pi.write(led_blanche, 0)
    pi.stop()
    print("stop")
    client.loop_stop()
    client.disconnect()
