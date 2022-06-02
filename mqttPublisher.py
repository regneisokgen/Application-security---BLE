import paho.mqtt.client as mqtt
import time
import json

# CHANGE THIS!!
HOST = "192.168.2.67"
PORT = 1883
# user = 'root'
# passwd = 'onioneer'

class Publisher:

    def connect_on(self, ip, port):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt.Client()
        # client.username_pw_set(user, passwd)
        client.on_connect = on_connect
        client.connect(ip, port)
        return client

    def publish_mqtt(self, client, topic, status, frequency, speed, direction):
        message = {"status": status, "frequency": frequency, "speed": speed, "direction": direction}
        data_out = json.dumps(message)
        result = client.publish(topic, data_out)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print("Status update published")
        else:
            print("Failed to publish update to topic")

#publisher = Publisher()
#clinet = publisher.connect_on(HOST, PORT)
#publisher.publish_mqtt(clinet, "sensor/change/direction", "On", "1150", "50", "0")
#publisher.publish_mqtt(clinet, "sensor/status/run", "Off", "1150", "70", "100")
#publisher.publish_mqtt(clinet, "sensor/change/speed", "Off", "", "20", "100")
#publisher.publish_mqtt(clinet, "sensor/complete/control", "On", "1150", "80", "0")