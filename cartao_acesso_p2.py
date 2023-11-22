import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import paho.mqtt.client as mqtt
import time 
import requests

ligado = 0
Broker = "test.mosquitto.org"
PortaBroker = 1883
KeepAliveBroker = 60
TopicoSubscribe = "pudim123"
TopicoAuth = "pudim1234"

def on_connect(client, userdata, flags, rc):
    client.subscribe(TopicoSubscribe)

def on_message(client, userdata, msg):
    global ligado
    MensagemRecebida = str(msg.payload)
    print(MensagemRecebida+" "+str(msg.payload))
    
    if str(msg.payload) == "b'1'":
        print("PERMITIDO")        
        ligado = 1
    else:
        print("NÃO AUTORIZADO")
        ligado = 0
    
client = mqtt.Client()
client.on_connect = on_connect
client.connect("test.mosquitto.org", 1883, 60)

while True:
    leitorRfid = SimpleMFRC522()
    GPIO.setmode(GPIO.BOARD)
    
    # Define os pinos de saída
    GPIO.setup(11, GPIO.OUT)  # led verde
    GPIO.setup(13, GPIO.OUT)  # led vermelho
    
    # Controle de acesso
    if ligado == 1:  # acesso permitido
        GPIO.output(11, 0)
        GPIO.output(13, 1)
    else:  # acesso negado
        GPIO.output(11, 1)
        GPIO.output(13, 0)
        
    print("Aproxime o cartão da leitora...")
    
    try:
        id, text = leitorRfid.read()
        print("ID do cartão: ", id)
        if id == 758599558077:
            print("Acesso permitido!")
            ligado = 1
            time.sleep(1)
        else:
            print("Acesso negado!")
            ligado = 0
            print("Permita o acesso:")
            client.on_message = on_message
            client.publish(TopicoAuth, "Acesso  negado clique para  permitir")    
            client.loop_start()
            time.sleep(10)  # Espere por 5 segundos antes de continuar
            client.loop_stop()
            

        url =  f"https://api.thingspeak.com/update?api_key=KT46PHXKM4AL0Y8H&field1={ligado}"
        
        response = requests.get(url)
            
    finally:
        GPIO.cleanup()
