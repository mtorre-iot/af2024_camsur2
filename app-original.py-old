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
import json
import os
from threading import Thread
import time
import pandas as pd
from UI.orevent import OrEvent
from UI.ui_design_lib import update_screen
import hcc2sdk
from hcc2sdk.classes.datatype import data_type
from hcc2sdk.classes.variablemodel import quality_enum, realtime_data
from applib.miscfuncs import check_max_min
import cv2
import numpy as np
import imutils
from imutils.video import VideoStream
import uuid

def app(logger, pitems, ui_config, vars, db, camera_mutex):
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
    #
    # 
    image_dir = ui_config['general']['image_dir']
    motion_capture_dir =ui_config['general']['motion_capture_dir']
    rtsp_url = ui_config['general']['rtsp_url'] 

    # col_idx = 1
    # colors = ["dark", "success"]
    last_mean = 0
    first = True
    
    ############################################################ OUTER INFINITE LOOP ################################################################

    while True:
       
        vs = VideoStream(rtsp_url+ "/h264Preview_01_sub").start()    # Open the RTSP stream
        width = 640
        height = 480
            
        jpeg_quality = 90  # Adjust this value to control the image quality (0-100)

        ############################################################ INNER INFINITE LOOP ################################################################
        while True:
            #
            # Is camera_mutex available?
            #
            with camera_mutex:
                ######
            
                ######
                # pitems.app_running_ok.color = colors[col_idx]
                # if col_idx == 0: 
                #     col_idx = 1 
                # else: 
                #     col_idx = 0
                #
                #  Get current sensitivity level
                #
                #####level = pitems.motion_sensitivity.value
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
                    except Exception as e:
                        logger.error("Error trying to delete files in image directory. Error: "  + str(e))
                    
                # Grab a frame at a time
                frame = vs.read()
                
                #hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 

                if frame is None:
                    logger.warning("A frame from camera could not be detected. Keep trying...")
                    time.sleep(1)
                    break
                #
                # Let's convert to HSV
                #
                ##hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                #
                # Set range for red color and  
                # define mask 
                red_lower = np.array([128, 0, 0], np.uint8) 
                red_upper = np.array([255, 128, 128], np.uint8) 
                #red_mask = cv2.inRange(hsvFrame, red_lower, red_upper) 
            
                # Set range for green color and  
                # define mask 
                green_lower = np.array([0, 128, 0], np.uint8) 
                green_upper = np.array([128, 255, 128], np.uint8) 
                #green_mask = cv2.inRange(hsvFrame, green_lower, green_upper) 
            
                # Set range for blue color and 
                # define mask 
                blue_lower = np.array([0, 0, 128], np.uint8) 
                blue_upper = np.array([128, 128, 255], np.uint8) 
                #blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper) 

                perc_small_box = 0.20
                sfx1 = int((frame.shape[0] - frame.shape[0]*perc_small_box)/2)
                sfx2 = int((frame.shape[0] + frame.shape[0]*perc_small_box)/2)
                sfy1 = int((frame.shape[1] - frame.shape[1]*perc_small_box)/2)
                sfy2 = int((frame.shape[1] + frame.shape[1]*perc_small_box)/2)



                small_frame = frame[sfx1: sfx2, sfy1:sfy2]
                #small_frame = frame
                focus = cv2.rectangle(frame, (sfy1, sfx1), (sfy2, sfx2),  (0, 255,0), 2)
                avg_color_per_row = small_frame.mean(axis=0)
                avg_color = avg_color_per_row.mean(axis=0)
                avg_color =tuple(avg_color.astype(int))

                #avg_color_str = f"R: {avg_color[2]}, G: {avg_color[1]}, B: {avg_color[0]}"

                #
                #  Re arrange arrays
                #
                corrected_color = []
                corrected_color.append(avg_color[2])
                corrected_color.append(avg_color[1])
                corrected_color.append(avg_color[0])

                corrected_color_str = f"R: {corrected_color[0]}, G: {corrected_color[1]}, B: {corrected_color[2]}"
                #logger.info("Color detected: " + corrected_color_str)

                #red_mask = cv2.inRange(hsvFrame, red_lower, red_upper) 
                #green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)
                #blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper) 
                
                #
                # Now compare against ranges
                #
                # Red
                red = True
                green = True
                blue = True

                for i in range(len(red_lower)):
                    if corrected_color[i] < red_lower[i] or corrected_color[i] > red_upper[i]: 
                        red = False
                        break
                    
                for i in range(len(green_lower)):
                    if corrected_color[i] < green_lower[i] or corrected_color[i] > green_upper[i]: 
                        green = False
                        break

                for i in range(len(blue_lower)):
                    if corrected_color[i] < blue_lower[i] or corrected_color[i] > blue_upper[i]: 
                        blue = False
                        break
                
                logger.info("R is " + str(red) + ", R value: " + str(corrected_color[0]) + 
                            ",G is " + str(green) + ", G value: " + str(corrected_color[1]) +
                            ', B is ' + str(blue) + ", B value: " + str(corrected_color[2]))

                        
                ##############################################

                # Resize and display the frame on the screen
                frame = imutils.resize(frame, width = 1200)

                image_path = os.path.join(image_dir, f'image_{timestamp}.jpg')  # Use .jpg extension
                cv2.imwrite(image_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
            
                pitems.capture_show.object = image_path
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                result = np.abs(np.mean(gray) - last_mean)
                # if first == False:
                #     if result > level:
                #         pitems.motion_sensitivity_label.value = "Motion Detected!"
                #         #db.set_value("motion_det_flag", 1, quality_enum.OK)
                #         logger.info("Motion detected!")
                #         #
                #         # Capture on disk
                #         #
                #         capture_path = os.path.join(motion_capture_dir, f'image_{timestamp}.jpg')  # Use .jpg extension
                #         cv2.imwrite(capture_path, frame, [,int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
                #         #
                #     else:
                #         pitems.motion_sensitivity_label.value = ""
                #         #db.set_value("motion_det_flag", 0, quality_enum.OK)
                # first = False
                # last_mean = np.mean(gray)
            
            #time.sleep(pitems.screenshot_period.value)
            time.sleep(0.5)
            #


