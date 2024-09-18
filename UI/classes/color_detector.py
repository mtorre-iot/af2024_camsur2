#
# Ajay Varma / Mario Torre - 09/18/2024
#
# Automation Fair 2024 Hands on sessions - color-commanded controller (camsur)


import numpy as np


class ColorDetector (object):
    def __init__(self):
        self.red_lower = None 
        self.red_upper = None
        self.green_lower = None
        self.green_upper = None
        self.blue_lower = None
        self.blue_upper = None

    def initialize(self):
        # Set range for red color and define mask 
        self.red_lower = np.array([128, 0, 0], np.uint8) 
        self.red_upper = np.array([255, 128, 128], np.uint8) 
            
        # Set range for green color and define mask 
        self.green_lower = np.array([0, 128, 0], np.uint8) 
        self.green_upper = np.array([128, 255, 128], np.uint8) 
            
        # Set range for blue color and define mask 
        self.blue_lower = np.array([0, 0, 128], np.uint8) 
        self.blue_upper = np.array([128, 128, 255], np.uint8) 

    def detect_colors(self, corrected_color):
        red = True
        green = True
        blue = True

        for i in range(len(self.red_lower)):
            red = red and ((corrected_color[i] >= self.red_lower[i]) and (corrected_color[i] <= self.red_upper[i])) 
            if red == False:
                break

        if red == False:
            for i in range(len(self.green_lower)):
                green = green and ((corrected_color[i] >= self.green_lower[i]) and (corrected_color[i] <= self.green_upper[i])) 
                if green == False:
                    break

            if green == False:
                for i in range(len(self.blue_lower)):
                    blue = blue and ((corrected_color[i] >= self.blue_lower[i]) and (corrected_color[i] <= self.blue_upper[i])) 
                    if blue == False:
                        break
            else:
                blue = False
        else:
            green = False
            blue = False

        return red, green, blue