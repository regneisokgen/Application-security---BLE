#!/usr/bin/python3
import dbus

from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
#from gpiozero import CPUTemperature
from mqttPublisher import Publisher
import paho.mqtt.client as mqtt
import time
import json

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

class WindmilAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("WindmilBLE")
        self.include_tx_power = True

# one service in the GATT profile
class WindmilService(Service):
    WINDMIL_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):
        self.farenheit = True

        Service.__init__(self, index, self.WINDMIL_SVC_UUID, True)
        self.add_characteristic(UseCharacteristic(self))
        self.add_characteristic(OnCharacteristic(self))

'''
    def is_farenheit(self):
        return self.farenheit

    def set_farenheit(self, farenheit):
        self.farenheit = farenheit
'''

#Characteristics under a profile
class UseCharacteristic(Characteristic):
    USE_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
            self, self.USE_CHARACTERISTIC_UUID,
            ["read"], service)
        self.add_descriptor(UseDescriptor(self))

    def get_char_read_value(self):
        value = []
        #unit = "C"

        #cpu = CPUTemperature()
        #temp = cpu.temperature
        '''
        if self.service.is_farenheit():
            temp = (temp * 1.8) + 32
            unit = "F"
        '''
# OK
        strtemp = 'JSON - sensor/change/direction || sensor/status/run || sensor/change/speed || sensor/complete/control {"status": status, "frequency": 1150, "speed": 50, "direction": 0}'
        for c in strtemp:
            value.append(dbus.Byte(c.encode()))
        return value

    def set_temperature_callback(self):
        if self.notifying:
            value = self.get_char_read_value()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True

        value = self.get_char_read_value()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_temperature_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_char_read_value()

        return value

# enum the (starting) attr handle to end grp handle
class UseDescriptor(Descriptor):
    USE_DESCRIPTOR_UUID = "2901"
    USE_DESCRIPTOR_VALUE = "sensor/change/direction, sensor/status/run, sensor/change/speed, sensor/complete/control"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.USE_DESCRIPTOR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.USE_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class OnCharacteristic(Characteristic):
    ON_CHARACTERISTIC_UUID = "00000003-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.status = ''
        Characteristic.__init__(
            self, self.ON_CHARACTERISTIC_UUID,
            ["read", "write"], service)
        self.add_descriptor(OnDescriptor(self))

    def WriteValue(self, value, options):
        #need to transform dbus bytes to TEXT
        val = value
        transformed = dbus.Array(val, signature=dbus.Signature('y'))
        text = "%s" % ''.join([str(v) for v in transformed])
        if text == "On":
            self.status = 'On'
            message = {"status": "On", "frequency": 1150, "speed": 70, "direction": 100}
            data_out = json.dumps(message)
            result = client.publish_mqtt("sensor/status/run", data_out)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print("Status update published")
            else:
                print("Failed to publish update to topic")
            print("value written {}. to c".format(val))
        elif text == "Off":
            self.status = 'Off'
            message = {"status": "Off", "frequency": 1150, "speed": 70, "direction": 100}
            data_out = json.dumps(message)
            result = client.publish_mqtt("sensor/status/run", data_out)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print("Status update published")
            else:
                print("Failed to publish update to topic")
            print("value written {}. to c".format(val))
        else:
            print("Else value written {}".format(val))

    def ReadValue(self, options):
        value = []

        msg = '{}'.format(self.status)
        for m in msg:
            value.append(dbus.Byte(m.encode()))
        return value


class OnDescriptor(Descriptor):
    ON_DESCRIPTOR_UUID = "2901"
    On_DESCRIPTOR_VALUE = "Control the device by publishing to sensor/status/run for on/off operation"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.ON_DESCRIPTOR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.On_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


mqttinit = Publisher()
client = mqttinit.connect_on("192.168.2.86", 1883)
app = Application()
app.add_service(WindmilService(0))
app.register()

adv = WindmilAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
    adv.quit()
