from pigpio_dht import DHT11
import pigpio
import threading
import time
gpio = 21
btn = 26
led_blanche=5 
led_bleu=6 
led_rouge=13 
sensor = DHT11(gpio)
pi = pigpio.pi()
def envoieInfo():
   result = sensor.read()
   if result['valid'] == True:
       print("Température :", result['temp_c'], "°C", " Humidité : ", result['humidity'] , " % " )
   else:
       print("rien envoyé")
def sec30():
       while True:
        envoieInfo()
        print("envoyé par sec")
        time.sleep(15)
def click():
   while True:
    pi.set_mode(btn, pigpio.INPUT)
    pi.set_pull_up_down(btn, pigpio.PUD_DOWN)
    bouton = pi.read(btn)
    if bouton == 0:
            print(bouton)
            envoieInfo()
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
   print("éteint manuellement")
