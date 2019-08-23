from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import dht11
import RPi.GPIO as GPIO
import datetime

rootCAPath = '/home/pi/certs/AmazonRootCA1.pem'
privateKeyPath = '/home/pi/certs/d88f3ef11b-private.pem.key'
certificatePath = '/home/pi/certs/d88f3ef11b-certificate.pem.crt'
host = 'a4wun5h9508b8-ats.iot.eu-west-1.amazonaws.com'
port = 8883
clientId = 'BLE-Pi-123'
topic = 'my_pi/1'

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    
#initialize
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId) #clientId can be anything
myAWSIoTMQTTClient.configureEndpoint(host, port) #host is your Pi’s AWS IoT Endpoint, port is 8883
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

#AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

#Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
# myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

# read data using pin 17
instance = dht11.DHT11(pin=17)

while True:
    result = instance.read()
    if result.is_valid():
        print("Last valid input: " +  str(datetime.datetime.now()))
        print("Temperature: %d C" % result.temperature)
        print("Humidity: %d %%" % result.humidity)
        if result.temperature > 28 and result.humidity > 50:
            message = {}
            message['humidity'] = result.humidity
            message['temperature'] = result.temperature
            messageJson = json.dumps(message)
            myAWSIoTMQTTClient.publish(topic, messageJson, 1)
            print('Published topic %s: %s\n' % (topic, messageJson))
            time.sleep(2)    
    time.sleep(2)

