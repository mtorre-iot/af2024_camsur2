#
# Mario Torre - 01/25/2024
#
# HCC2 Flow estimator application
#
# -----------------------------------------------------------------------------
#
# Main entry 
#
# ------------------------------------------------------------------------------
from datetime import datetime
from filelock import FileLock
import json
import os
import time
import pandas as pd
from UI.orevent import OrEvent
from UI.ui_design_lib import update_screen
import hcc2sdk
from hcc2sdk.classes.datatype import data_type
from hcc2sdk.classes.variablemodel import quality_enum, realtime_data
from applib.miscfuncs import check_max_min
import cv2
import imutils
from imutils.video import VideoStream
import uuid



def app(logger, pitems, ui_config, vars, db, new_scan_event):
    appcfg_dir = 'appconfig/'
    appcfg_file = 'config.json'
    try:
        with open(os.path.join(appcfg_dir, appcfg_file)) as json_file:
            appcfg = json.load(json_file)
    except Exception as e:
        logger.error('Cannot read Application configuration file. Program ABORTED. Error: %s', str(e))
        return

    logger.name = "PYAPP"                   # give your logging context a name to appear in Unity
    logger.info("App: " + appcfg['app']['name'] + ", Version: " + appcfg['app']['version']) 
    
    image_dir = "/tmp"
    rtsp_url = "rtsp://admin:Sensia1!@192.168.1.81" 
    vs = VideoStream(rtsp_url).start()    # Open the RTSP stream
    jpeg_quality = 90  # Adjust this value to control the image quality (0-100)

    ############################################################ OUTER INFINITE LOOP ################################################################
    while True:
        #
        # wait for events
        #
        ######new_scan_event.wait()
        #
        # Get Timestamp
        #
        current_time = time.time()
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
        #
        # Before generating a new image, get rid of all previous images
        #
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        else:
            try:
                for f in os.listdir(image_dir):
                    os.remove(os.path.join(image_dir, f))
            except:
                pass
            
        # Grab a frame at a time
        frame = vs.read()
        
        if frame is None:
            continue

        # Resize and display the frame on the screen
        frame = imutils.resize(frame, width = 1200)

        image_path = os.path.join(image_dir, f'image_{timestamp}.jpg')  # Use .jpg extension
        cv2.imwrite(image_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
       
        pitems.capture_show.object = image_path

        time.sleep(1)
        #


