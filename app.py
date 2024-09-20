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
import json
import os
import time
import pandas as pd
from UI.classes.color_detector import ColorDetector
from UI.ui_design_lib import update_screen
import hcc2sdk
from hcc2sdk.classes.variablemodel import quality_enum
import cv2
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

def set_capture_window(frame, perc_small_box):
    sfx1 = int((frame.shape[0] - frame.shape[0]*perc_small_box)/2)
    sfx2 = int((frame.shape[0] + frame.shape[0]*perc_small_box)/2)
    sfy1 = int((frame.shape[1] - frame.shape[1]*perc_small_box)/2)
    sfy2 = int((frame.shape[1] + frame.shape[1]*perc_small_box)/2)
    small_frame = frame[sfx1: sfx2, sfy1:sfy2]
    #focus = cv2.rectangle(frame, (sfy1, sfx1), (sfy2, sfx2),  (0, 255,0), 2)
    return small_frame
#
# Main APP entry point
#
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
    cd = ColorDetector()
    #
    prev_combined_state = False
    debounce_counter = 0
    #
    ############################################OUTER INFINITE LOOP ########################################

    while True:
        vs = VideoStream(rtsp_url).start()    # Open the RTSP stream
        jpeg_quality = appcfg['app']['jpeg_quality']  # Adjust this value to control the image quality (0-100)
        logger.info("video streaming started.")
        ################################### INNER INFINITE LOOP ############################################
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
            # initialize detector
            #
            cd.initialize()
            #
            # Configure capture window
            #
            small_frame = set_capture_window(frame, appcfg['app']['capture_window_perc'])
            avg_color_per_row = small_frame.mean(axis=0)
            avg_color = avg_color_per_row.mean(axis=0)
            avg_color =tuple(avg_color.astype(int))
            #
            # Resize and display the frame on the screen
            #
            if (ui_config['image']['show'] == True):
                #frame = imutils.resize(frame, width = 1200)

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
            red, green, blue = cd.detect_colors(corrected_color)
            if (4* red + 2 * green + blue) != prev_combined_state:
                debounce_counter += 1
            else:
                debounce_counter = 0
            
            if debounce_counter >= appcfg['app']['debounce_max_counter']:
                #
                prev_combined_state = (4 * red + 2 * green + blue) 
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
            


