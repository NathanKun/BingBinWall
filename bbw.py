#!/usr/bin/python3.4

"""
Bing Bin Wall
Python script of Bing Bin Wall project
For raspberry pi 3b
"""

__author__ = "Junyang HE, Yuzhou SONG"
__version__ = "1.0"
__maintainer = "Junyang HE, Yuzhou SONG"
__email__ = "nathanhejunyang@gmail.com"


# rgb led
RED   = 2
GREEN = 3
BLUE  = 4

# ultrasound distance sensor
TRIG = 19
ECHO = 26

# beeper
BEEP = 21

# pi-camera
IMAGESPATH = "../images/"

# tensorflow
FROZEN_MODEL_PATH = './graph.pb'
INPUT_SIZE = 224
INDEX_2_LABEL = {
    0 : 'cardboard',
    1 : 'plastic',
    2 : 'paper',
    3 : 'glass',
    4 : 'metal'
}

### RGB ###
def blink(pin1, pin2=None, pin3=None, duration=3):
    GPIO.output(pin1, False)
    if pin2: GPIO.output(pin2, False)
    if pin3: GPIO.output(pin3, False)
    
    time.sleep(duration)
    
    GPIO.output(pin1, True)
    if pin2: GPIO.output(pin2, True)
    if pin3: GPIO.output(pin3, True)
        

def blinkRed():
    blink(RED)

def blinkGreen():
    blink(GREEN)

def blinkBlue():
    blink(BLUE)
    
def blinkYellow():
    blink(RED, GREEN)

# predict rgb indication
LABEL_TO_DORGB = {
    'cardboard' : blinkBlue,
    'plastic' : blinkYellow,
    'paper' : blinkBlue,
    'glass' : blinkGreen,
    'metal' : blinkYellow,
    'other' : blinkRed
}


### ultrasound ###
def mesureDistance():
    # mesure distance in cm
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
        pulse_start = time.time()

    while GPIO.input(ECHO)==1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance


### beeper ###
def beepOnce(beepDuration = 0.2, waitDuration = 0.2):
    GPIO.output(BEEP, True)
    time.sleep(beepDuration)
    GPIO.output(BEEP, False)
    time.sleep(waitDuration)

def beepTooClose():
    for i in range(0, 3):
        beepOnce()

def beepDistanceOk():
    beepOnce(1, 1)


### pi-camera ###
def takePhoto(camera):
    log("Taking photo...")
    timeStr = '{0:%Y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]
    file = IMAGESPATH + timeStr + '.jpg';
    
    camera.capture(file)

    return file

### Tensorflow ###
def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
                                input_mean=0, input_std=255):
    input_name = "file_reader"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels=3,
                                           name='png_reader')
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                      name='gif_reader'))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    else:
        image_reader = tf.image.decode_jpeg(file_reader, channels=3,
                                            name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result

def load_frozen_graph(frozen_model):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(frozen_model, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    return detection_graph

def predict(image_path, input_name="input:0", output_name="final_result:0"):
    """
    Predict image category.

    :param image_path: str
    :param input_name: str
    :param output_name: str

    :return: category and probability
    :rtype: (str, float)
    """
    
    log("Predicting...")
    
    graph = load_frozen_graph(FROZEN_MODEL_PATH)
    image_tensor = read_tensor_from_image_file(image_path,
                                               input_height=INPUT_SIZE,
                                               input_width=INPUT_SIZE)
    input_tensor = graph.get_tensor_by_name(input_name)
    output_tensor = graph.get_tensor_by_name(output_name)
    with tf.Session(graph=graph) as sess:
        results = sess.run(output_tensor,
                           {input_tensor: image_tensor})
    results = np.squeeze(results)
    top_index = results.argsort()[-1]
    label = INDEX_2_LABEL[top_index]
    
    log("Predict result: " + label + ": " + str(results[top_index]))
    return label

def doResult(label):
    log("Responsing...")
    if label in LABEL_TO_DORGB:
        LABEL_TO_DORGB[label]()
    else:
        LABEL_TO_DORGB['other']()
    

def log(logStr):
    timeStr = '{0:%Y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]
    print(timeStr + ": " + logStr)

if __name__ == '__main__':
    import datetime
    log("Bing Bin Wall Starting...")
    
    # import modules
    import os
    import time
    import numpy as np
    import _thread
    import RPi.GPIO as GPIO
    import picamera
    import tensorflow as tf

    # init gpio
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(BEEP,GPIO.OUT)
    GPIO.output(BEEP, False)

    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    GPIO.output(TRIG, False)

    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(BLUE, GPIO.OUT)
    GPIO.output(RED, True)
    GPIO.output(GREEN, True)
    GPIO.output(BLUE, True)

    # check if image dir exists
    if not os.path.exists(IMAGESPATH):
        os.mkdir(IMAGESPATH)

    # init camera
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)

    # main loop
    log("Main loop start")
    run = True
    while run:
        try:
            # mesure distance
            distance = mesureDistance()
            if(distance < 30):
                beepTooClose()
            elif (distance <= 70 and distance >=30):
                log("Object found, working...")
                _thread.start_new_thread(beepDistanceOk, ())
                doResult(predict(takePhoto(camera)))
                log("Finished")
            # else distance > 70 : do nothing
                
        except KeyboardInterrupt:
            # clean up gpio
            print("")
            log("Exiting...")
            run = False
            GPIO.cleanup()
            log("Bye")
    # main loop end
