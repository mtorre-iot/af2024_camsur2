#
# Ajay Varma / Mario Torre - 09/18/2024
#
# Automation Fair 2024 Hands on sessions - color-commanded controller (camsur)
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
import cv2
import numpy as np
import imutils
from imutils.video import VideoStream
#
# Internal methods
#
def initialize_image_dir(image_dir):
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    else:
        for f in os.listdir(image_dir):
            os.remove(os.path.join(image_dir, f))


def app(logger, pitems, ui_config, db, new_scan_event):
    appcfg_dir = 'appconfig/'
    appcfg_file = 'config.json'
    try:
        with open(os.path.join(appcfg_dir, appcfg_file)) as json_file:
            appcfg = json.load(json_file)
    except Exception as e:
        logger.error('Cannot read Application configuration file. Program ABORTED. Error: %s', str(e))
        return

    logger.name = "CAMSUR"  # give your logging context a name to appear in Unity
    logger.info("App: " + appcfg['app']['name'] + ", Version: " + appcfg['app']['version']) 
    #
    # 
    rtsp_url = ui_config['general']['rtsp_url'] 
    image_dir = ui_config['image']['dir']
    #
    # Before generating a new images, get rid of all previous images
    #
    ############################################################ OUTER INFINITE LOOP ################################################################

    while True:
        vs = VideoStream(rtsp_url).start()    # Open the RTSP stream
        jpeg_quality = appcfg['app']['jpeg_quality']  # Adjust this value to control the image quality (0-100)

        ############################################################ INNER INFINITE LOOP ################################################################
        while True:
            #
            # initialize any image capture
            #
            try:
                initialize_image_dir(image_dir)
            except Exception as e:
                logger.error("Error trying to delete files in image directory. Error: "  + str(e))
                exit()
            #
            # Get Timestamp
            #
            current_time = time.time()
            timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
            #                    
            # Grab a frame at a time
            #
            frame = vs.read()

            if frame is None:
                logger.warning("A frame from camera could not be detected. Keep trying...")
                time.sleep(app['app']['time_between_images'])
                break
            #
            # Set range for red color and define mask 
            red_lower = np.array([128, 0, 0], np.uint8) 
            red_upper = np.array([255, 128, 128], np.uint8) 
            
            # Set range for green color and define mask 
            green_lower = np.array([0, 128, 0], np.uint8) 
            green_upper = np.array([128, 255, 128], np.uint8) 
            
            # Set range for blue color and define mask 
            blue_lower = np.array([0, 0, 128], np.uint8) 
            blue_upper = np.array([128, 128, 255], np.uint8) 

            # Configure capture window

            perc_small_box = appcfg['app']['capture_window_perc']
            sfx1 = int((frame.shape[0] - frame.shape[0]*perc_small_box)/2)
            sfx2 = int((frame.shape[0] + frame.shape[0]*perc_small_box)/2)
            sfy1 = int((frame.shape[1] - frame.shape[1]*perc_small_box)/2)
            sfy2 = int((frame.shape[1] + frame.shape[1]*perc_small_box)/2)

            small_frame = frame[sfx1: sfx2, sfy1:sfy2]
            focus = cv2.rectangle(frame, (sfy1, sfx1), (sfy2, sfx2),  (0, 255,0), 2)
            avg_color_per_row = small_frame.mean(axis=0)
            avg_color = avg_color_per_row.mean(axis=0)
            avg_color =tuple(avg_color.astype(int))
            #
            # Resize and display the frame on the screen
            #
            if (ui_config['image']['show'] == True):
                frame = imutils.resize(frame, width = 1200)

                image_path = os.path.join(image_dir, f'image_{timestamp}.jpg')  # Use .jpg extension
                cv2.imwrite(image_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
            
                pitems.capture_show.object = image_path
            #
            #  Re arrange arrays
            #
            corrected_color = []
            corrected_color.append(avg_color[2])
            corrected_color.append(avg_color[1])
            corrected_color.append(avg_color[0])
            #
            # Now compare against ranges
            #
            red = True
            green = True
            blue = True

            for i in range(len(red_lower)):
                red = red and ((corrected_color[i] >= red_lower[i]) and (corrected_color[i] <= red_upper[i])) 
                if red == False:
                    break

            if red == False:
                for i in range(len(green_lower)):
                    green = green and ((corrected_color[i] >= green_lower[i]) and (corrected_color[i] <= green_upper[i])) 
                    if green == False:
                        break

                if green == False:
                    for i in range(len(blue_lower)):
                        blue = blue and ((corrected_color[i] >= blue_lower[i]) and (corrected_color[i] <= blue_upper[i])) 
                        if blue == False:
                            break
                else:
                    blue = False
            else:
                green = False
                blue = False

            #logger.info("R is " + str(red) + ", R value: " + str(corrected_color[0]) + 
            #           ", G is " + str(green) + ", G value: " + str(corrected_color[1]) +
            #           ", B is ' + str(blue) + ", B value: " + str(corrected_color[2]))
            #
            # Write results to HCC2
            #
            try:
                db.set_value("red", red, quality_enum.OK)
                db.set_value("green", green, quality_enum.OK)
                db.set_value("blue", blue, quality_enum.OK)
            except Exception as e:
                logger.error('Cannot write data into realtime DB. Error: %s', str(e))
            #
            # Update screen
            #
            red_idx = 1 if red else 0
            green_idx = 1 if green else 0
            blue_idx = 1 if blue else 0
            

            pitems.red_label.color = ui_config["boolean_status"]['red']['color'][red_idx]
            pitems.green_label.color = ui_config["boolean_status"]['green']['color'][green_idx]
            pitems.blue_label.color = ui_config["boolean_status"]['blue']['color'][blue_idx]

            time.sleep(appcfg['app']['time_between_images'])
            


