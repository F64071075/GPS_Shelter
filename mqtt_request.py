# python3.6

import ssl, base64, json

from paho.mqtt import client as mqtt_client


LORA_SERVER = 'mqtt.hscc.csie.ncu.edu.tw'
LORA_ACCOUNT = ''
LORA_PASSWORD = ''
port = 1883
topic = 'application/6/device/0000000000000001/rx'
data = []

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            
    def on_log(client, userdata, level, buf):
        print('level', level)
        print("log: ",buf)
        
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.username_pw_set(LORA_ACCOUNT, LORA_PASSWORD)
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    client.on_connect = on_connect
    client.connect(LORA_SERVER, port)
    client.on_log = on_log
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, message):
        msg = json.loads(message.payload.decode())
        print("message received " ,msg)
        data_decoded = str(base64.b64decode(msg['data']), 'utf-8')
        data_decoded = data_decoded.replace('b\'', "")
        data_decoded = data_decoded.replace('\\r', '')
        data_list = data_decoded.split('\\n\'')
        for d in data_list:
            if d != '':
                data.append(d)
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    print('Please enter your file name : ')
    name = input()
    print('Please enter your server account : ')
    LORA_ACCOUNT = input()
    print('Please enter your server password : ')
    LORA_PASSWORD = input()
    try:
        run()
    except KeyboardInterrupt:
        with open(name+'.txt', 'w') as output:
            for row in data:
                output.write(str(row)+'\n')