from pigpio_dht import DHT11
import pigpio
import threading
import time
gpio = 21
btn = 26
sensor = DHT11(gpio)
pi = pigpio.pi()

def envoieInfo():
   result = sensor.read()
   if result['valid'] == True:
       print("Température :", result['temp_c'], "°C", result['valid'])
   else:
       print("rien envoyé")


def click():
   pi.set_mode(btn, pigpio.INPUT)
   pi.set_pull_up_down(btn, pigpio.PUD_DOWN)
   bouton = pi.read(btn)
   if bouton == 0:
        envoieInfo()
        print("envoyé par bouton")
        time.sleep(0.5)

try:
   thread_click = threading.Thread(target=click, daemon=True)
   thread_click.start()
   while True:
       time.sleep(2)
except KeyboardInterrupt:
   print("éteint manuellement")
