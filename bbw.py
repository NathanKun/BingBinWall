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
RED   = 17
GREEN = 27
BLUE  = 22

# ultrasound distance sensor
#TRIG = 19
#ECHO = 26

# ToF distance sensor
VL53L0X_REG_IDENTIFICATION_MODEL_ID		= 0x00c0
VL53L0X_REG_IDENTIFICATION_REVISION_ID		= 0x00c2
VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD	= 0x0050
VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD	= 0x0070
VL53L0X_REG_SYSRANGE_START			= 0x000
VL53L0X_REG_RESULT_INTERRUPT_STATUS 		= 0x0013
VL53L0X_REG_RESULT_RANGE_STATUS 		= 0x0014
address = 0x29

# beeper
BEEP = 21

# pi-camera
IMAGES_DIR_PATH = '/home/pi/BingBinWall/images/'

# log dir
LOG_DIR_PATH = '/home/pi/BingBinWall/logs/'

# tensorflow
FROZEN_MODEL_PATH = '/home/pi/BingBinWall/graph.pb'
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

def blinkWhite():
    blink(RED, GREEN, BLUE, 2)

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
'''def mesureDistance():
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
'''


### ToF ###
def bswap(val):
    return struct.unpack('<H', struct.pack('>H', val))[0]

def mread_word_data(adr, reg):
    return bswap(bus.read_word_data(adr, reg))

def mwrite_word_data(adr, reg, data):
    return bus.write_word_data(adr, reg, bswap(data))

def makeuint16(lsb, msb):
    return ((msb & 0xFF) << 8)  | (lsb & 0xFF)

def VL53L0X_decode_vcsel_period(vcsel_period_reg):
# Converts the encoded VCSEL period register value into the real
# period in PLL clocks
    vcsel_period_pclks = (vcsel_period_reg + 1) << 1;
    return vcsel_period_pclks;

def mesureDistance():
    mesureOK = False

    while not mesureOK:
        val1 = bus.write_byte_data(address, VL53L0X_REG_SYSRANGE_START, 0x01)

        cnt = 0
        while (cnt < 100): # 1 second waiting time max
                time.sleep(0.010)
                val = bus.read_byte_data(address, VL53L0X_REG_RESULT_RANGE_STATUS)
                if (val & 0x01):
                        break
                cnt += 1

        if (val & 0x01):
            data = bus.read_i2c_block_data(address, 0x14, 12)
            distance = makeuint16(data[11], data[10])
            if (distance > 50 and distance < 1000):
                mesureOK = True

    return distance / 10 # mm to cm


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
    file = IMAGES_DIR_PATH + timeStr + '.jpg';
    
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
    logPredict(image_path, label, str(results[top_index]))
    return label


### Bing Bin Wall ###
def doResult(label):
    log("Responsing...")
    if label in LABEL_TO_DORGB:
        LABEL_TO_DORGB[label]()
    else:
        LABEL_TO_DORGB['other']()
    

def log(logStr, withTime = True):
    timeStr = ''
    if withTime:
        timeStr = '{0:%Y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3] + ": "
    logStr = timeStr + logStr
    
    print(logStr)
    with open(LOG_DIR_PATH + 'bbw.log', 'a') as f:
        f.write(logStr + '\n')

def logPredict(file, label, percentage):
    timeStr = '{0:%Y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]
    with open(LOG_DIR_PATH + 'predict.log', 'a') as f:
        f.write(timeStr + '\t' + file + '\t' + label + '\t' + percentage + '\n')

def quitGracefully(*args):
    # clean up gpio
    print("")
    log("Exiting...")
    run = False
    GPIO.cleanup()
    log("Bye")
    exit(0)

def my_except_hook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        quitGracefully()
    else:
        GPIO.cleanup()
        log("Exception", withTime = False)
        log("exctype:", withTime = False)
        log(str(exctype), withTime = False)
        log("value:", withTime = False)
        log(str(value), withTime = False)
        log("traceback:", withTime = False)
        tbList = tb.format_tb(traceback, 100)
        for i in tbList:
            log(i, withTime = False) # limit = 100
            
        sys.__excepthook__(exctype, value, traceback)
        
if __name__ == '__main__':
    import os
    import sys
    import traceback as tb
    import datetime
    import signal

    sys.excepthook = my_except_hook
    signal.signal(signal.SIGINT, quitGracefully)

    # check if log folder exists
    if not os.path.exists(LOG_DIR_PATH):
        os.mkdir(LOG_DIR_PATH)
        
    log("Bing Bin Wall Starting...")
    
    # import modules
    import time
    import numpy as np
    import _thread
    import RPi.GPIO as GPIO
    import picamera
    import tensorflow as tf
    import smbus2 as smbus
    import struct

    # init gpio
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(BEEP,GPIO.OUT)
    GPIO.output(BEEP, False)

    #GPIO.setup(TRIG,GPIO.OUT)
    #GPIO.setup(ECHO,GPIO.IN)
    #GPIO.output(TRIG, False)

    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(BLUE, GPIO.OUT)
    GPIO.output(RED, True)
    GPIO.output(GREEN, True)
    GPIO.output(BLUE, True)

    # init i2c
    bus = smbus.SMBus(1)

    # check if image dir exists
    if not os.path.exists(IMAGES_DIR_PATH):
        os.mkdir(IMAGES_DIR_PATH)

    # init camera
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)

    # indicate initialized successfully
    blinkGreen()

    # main loop
    log("Main loop start")
    run = True
    while run:
        # mesure distance
        distance = mesureDistance()
        if(distance < 30):
            beepTooClose()
        elif (distance <= 70 and distance >=30):
            log("Object found, working...")
	    # beep
            _thread.start_new_thread(beepDistanceOk, ())
	    # white light
            _thread.start_new_thread(blinkWhite, ())
            time.sleep(0.5)
            doResult(predict(takePhoto(camera)))
            log("Finished")
        # else distance > 70 : do nothing
        time.sleep(0.5)
    # main loop end
