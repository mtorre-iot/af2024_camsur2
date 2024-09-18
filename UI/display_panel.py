#
# Mario Torre - 01/29/2024
#
import asyncio
import os
import json
import panel as pn
import time
import pandas as pd
from datetime import datetime
from UI.ui_design_lib import copyFile, send_notification
from UI.ui_styles import header_widgets_style, body_wb_style, subbody_wb_style, log_widgets_style, body_widgets_style, header_wb_style, motion_detection_widgets_style
from imutils.video import VideoStream
import cv2
import imutils


def display_panel(logger, stream, config, ui_config, pitems, webport, camera_mutex):
  #
  # Panel Initialization and general configuration
  #
  pn.extension(design=ui_config['template']['design'])
  pn.extension(notifications=True)
  pn.config.theme = ui_config['template']['theme']

  pn.config.raw_css.append(header_widgets_style)
  pn.config.raw_css.append(body_widgets_style)

  red_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['red']['name'], value="", stylesheets=[body_widgets_style])
  pitems.red_label = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['red']['color'][0], value = True)
  green_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['green']['name'], value="", stylesheets=[body_widgets_style])
  pitems.green_label = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['green']['color'][0], value = True)
  blue_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['blue']['name'], value="", stylesheets=[body_widgets_style])
  pitems.blue_label = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['blue']['color'][0], value = True)
  #
  # Log:
  #
  log_text_area_input = pn.widgets.TextAreaInput(name="", sizing_mode="stretch_both", stylesheets=[body_widgets_style, log_widgets_style])
  #
  # General
  #
  #pitems.motion_sensitivity = pn.widgets.FloatInput(name="Motion Sensitivity (%)", value = 10.00, width=150,  stylesheets=[body_widgets_style])
  #pitems.motion_sensitivity_label = pn.widgets.StaticText(name="", value="", styles=motion_detection_widgets_style)
  #pitems.screenshot_period = pn.widgets.IntInput(name="Scan period (s)", value = 3, start=1, end=60, step=1, width=150, stylesheets=[body_widgets_style])
  #
  # Widgetbox building 
  #
  # Master:
  master_widgetbox = pn.WidgetBox (name=ui_config['widgetboxes']['template']['name'], styles=header_wb_style)
  #
  # Header:
  header_widgetbox = pn.WidgetBox (name=ui_config['widgetboxes']['header']['name'], height=ui_config['widgetboxes']['header']['height'], styles=header_wb_style)
  header_title = pn.widgets.StaticText(name="", value = ui_config['header']['title'], sizing_mode = "stretch_width", stylesheets=[header_widgets_style])
  header_widgetbox.append(header_title)
  #
  # Bodies:
  body1_widgetbox = pn.WidgetBox (name=ui_config['widgetboxes']['body1']['name'], height = 460, styles=body_wb_style)
  body2_widgetbox = pn.WidgetBox (name=ui_config['widgetboxes']['body2']['name'], styles=body_wb_style)
  #
  # Inputs:
  inputs_widgetbox = pn.WidgetBox(name=ui_config['widgetboxes']['inputs']['name'], sizing_mode = ui_config['widgetboxes']['inputs']['sizing_mode'], styles=subbody_wb_style)
  inputs_title = pn.pane.Markdown(ui_config['widgetboxes']['inputs']['title'])
  #
  # Outputs:
  outputs_widgetbox = pn.WidgetBox(name=ui_config['widgetboxes']['outputs']['name'], sizing_mode = ui_config['widgetboxes']['outputs']['sizing_mode'], styles=subbody_wb_style)
  outputs_title = pn.pane.Markdown(ui_config['widgetboxes']['outputs']['title'])
  #
  # capture:
  pitems.capture_show = pn.pane.Image(os.path.join(ui_config['files']['dir'], ui_config['files']['empty']), width=ui_config['files']['size'])
  #
  # Log:
  log_widgetbox = pn.WidgetBox(name=ui_config['widgetboxes']['log']['name'], sizing_mode = ui_config['widgetboxes']['log']['sizing_mode'], styles=subbody_wb_style)
  log_title = pn.pane.Markdown(ui_config['widgetboxes']['log']['title'])
  #
  # Final page building and formatting
  #
  ### ROW 1
  # 
  inputs_widgetbox.append(inputs_title)
  # inputs_widgetbox.append(whp_title)
  # #
  # ## COLUMN 1
  # #
  #inputs_widgetbox.append(pn.Row(
  #   pn.Column(pitems.capture_btn),
  #  )
  #)
  #inputs_widgetbox.append(pn.Row(
  #   pn.Column(pitems.motion_sensitivity),
  #  )
  #)
  #inputs_widgetbox.append(
  #  pn.Row(
  #    pn.Column(pitems.screenshot_period)
  #  )
  #)
  inputs_widgetbox.append(
    pn.Row(
  #   pn.Column(pitems.motion_sensitivity_label),
  #  )
  #)
    pn.Column(pn.Row(
        pn.Column(red_label, pitems.red_label),
        pn.Column(green_label, pitems.green_label),
        pn.Column(blue_label, pitems.blue_label)
        )
      )
    )
  )

  # inputs_widgetbox.append(pn.Row(
  #    pn.Column(app_running_ok_label),
  #    pn.Column(pitems.app_running_ok)
  #   )
  # )
   


    #
  # COLUMN 2
  #
  outputs_widgetbox.append(outputs_title)
  #outputs_widgetbox.append(oil_rate_est_title)

  outputs_widgetbox.append(
    pn.Row(
      pn.Column(pitems.capture_show)
    )
  )
  #
  # ROW 2 
  #
  log_widgetbox.append(pn.Row(pn.Param(stream,  
    widgets={"value": {"widget_type": log_text_area_input}})))
  #
  # Body widget buildup
  #
  body1_widgetbox.append(pn.Row(
      pn.Column(inputs_widgetbox),
      pn.Spacer(width=ui_config['spacers']['1']['width']),
      pn.Column(outputs_widgetbox), # model_widgetbox)
    )
  ) 
  body2_widgetbox.append(log_widgetbox)
  #
  # final widgets combination
  #
  master_widgetbox.append(header_widgetbox)
  master_widgetbox.append(body1_widgetbox)
  master_widgetbox.append(body2_widgetbox)
  #
  # All set! Fire it up!
  #
  event_loop = asyncio.new_event_loop()
  asyncio.set_event_loop(event_loop)
  try:
    master_widgetbox.show(title=ui_config['header']['title'], port=webport, websocket_origin="*")
  except Exception as e:
    logger.error("Exception trying to start Panel thread. Error: " + str(e) + ". Program ABORTED.")
  exit()