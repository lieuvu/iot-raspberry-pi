from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import dht11
import RPi.GPIO as GPIO
import datetime
from picamera import PiCamera
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import TransferConfig


#Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    
def initAWSIot():
    rootCAPath = '/home/pi/certs/AmazonRootCA1.pem'
    privateKeyPath = '/home/pi/certs/d88f3ef11b-private.pem.key'
    certificatePath = '/home/pi/certs/d88f3ef11b-certificate.pem.crt'
    host = 'a4wun5h9508b8-ats.iot.eu-west-1.amazonaws.com'
    port = 8883
    clientId = 'BLE-Pi-123'
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
    return myAWSIoTMQTTClient

def capturePicture(camera, imagePath):
    print('Capturing picture....')
    camera.resolution = (300, 300)
    camera.framerate = 90
    camera.start_preview()
    camera.capture(imagePath, 'png', True, (300, 300))
    time.sleep(1)
    camera.stop_preview()
    print('Picture captured!')

def uploadToS3(s3Client, bucket, localImagePath, uploadedImage):
    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                            multipart_chunksize=1024*25, use_threads=True)
    

    try:
        print('Uploading image to S3..')
        s3Client.upload_file('/home/pi/Desktop/image.png', bucket, uploadedImage, None, None, config)
        print("Upload Successful")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
 
def deleteImageInS3(s3Client, bucket, uploaded_image):
    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                            multipart_chunksize=1024*25, use_threads=True)
    
    try:
        s3Client.delete_object(Bucket=bucket, Key=uploaded_image)
    except ClientError as e:
        print(e)
        
def detectImageIfHuman(bucket, uploadedImage):
    rekognitionClient = boto3.client('rekognition')
    response = rekognitionClient.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':uploadedImage}})

    # Process the image recognition results
    humanArr = ['Face', 'Human', 'Person', 'Man']
    isHuman = False
    
    for label in response['Labels']:
        print(label['Name'] + ' : ' + str(label['Confidence']))
    
    for label in response['Labels']:
        if label['Name'] in humanArr and label['Confidence'] > 95:
            isHuman = True
            break
    return isHuman

def main():
    # Some constants
    pirPin = 17
    topic = 'my_pi/1'
    
    # GPIO Setup
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pirPin,GPIO.IN)
    
    print('Starting Alarm Program...')
    
    # AWS Iot Client Setup
    myAWSIoTMQTTClient = initAWSIot()
    
    # Camera Setup
    camera = PiCamera()
    
    while True:
        # If there is movement
        if GPIO.input(pirPin) != 0:
            print('*** Movement dected ***')
            
            imagePath = '/home/pi/Desktop/image.png'
            
            # Capture picture
            capturePicture(camera, imagePath)
            
            bucket = 'iot-photos'
            uploadedImage = f'uploaded_image.png'
            s3Client = boto3.client('s3')
            
            # Upload to S3
            uploadToS3(s3Client, bucket, imagePath, uploadedImage)
            
            # Detect image
            isHuman = detectImageIfHuman(bucket, uploadedImage)
                 
            if isHuman:
                print('Human detected')
                # Send message to AWS SNS
                message = {}
                message['alarm'] = 'true'
                message['acation'] = 'Dangerous. Run away!'
                messageJson = json.dumps(message)
                myAWSIoTMQTTClient.publish(topic, messageJson, 1)
                print('Published topic %s: %s\n' % (topic, messageJson))
                
                # Delete picture
                deleteImageInS3(s3Client, bucket, uploadedImage)
            else:
                print('Not Human!')
                
            time.sleep(3)
        else:
            print ('*** Not movement ***')
            time.sleep(3)
        
def cleanup():
    #turn off buzzer
    GPIO.cleanup()
    
# Running
if __name__ == '__main__':
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        cleanup()
        pass



