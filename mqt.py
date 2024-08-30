
from paho.mqtt import client as cl
import random

broker = '10.180.0.9'
port = 1883
topic = [("zigbee2mqtt/Dvere Petr", 0), ("zigbee2mqtt/tlacitko", 0)]
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = ''
password = ''


def mqtt():
    client = connect()
    subscribe(client)
    client.loop_forever()


def connect():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code {code}".format(rc))
    client = cl.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client):
    def on_message(client, userdata, msg):
        print(msg.payload.decode())
        if "double" in msg.payload.decode():
            print("yes")
    client.subscribe(topic)
    client.on_message = on_message


mqtt()
