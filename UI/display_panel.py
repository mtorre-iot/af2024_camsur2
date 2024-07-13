#
# Mario Torre - 01/29/2024
#
import asyncio
import os
import json
import panel as pn
import pandas as pd
from datetime import datetime
from UI.ui_design_lib import copyFile, send_notification
from UI.ui_styles import header_widgets_style, body_wb_style, subbody_wb_style, log_widgets_style, body_widgets_style, header_wb_style, motion_detection_widgets_style
from UI.classes.model import Model


def display_panel(logger, stream, config, ui_config, pitems, webport, new_model_event):
  #
  # Callbacks
  #
  def capture_button_callback(event):
    logger.info("Capture Button pressed!!")
  #
  # Panel Initialization and general configuration
  #
  pn.extension(design=ui_config['template']['design'])
  pn.extension(notifications=True)
  pn.config.theme = ui_config['template']['theme']

  pn.config.raw_css.append(header_widgets_style)
  pn.config.raw_css.append(body_widgets_style)

  pitems.capture_btn = pn.widgets.Button(name=ui_config['buttons']['capture_btn']['name'], width=ui_config['buttons']['capture_btn']['width'], button_type=ui_config['buttons']['capture_btn']['type'], stylesheets=[body_widgets_style])
  pitems.capture_btn.on_click(capture_button_callback)
  #
  # Log:
  #
  log_text_area_input = pn.widgets.TextAreaInput(name="", sizing_mode="stretch_both", stylesheets=[body_widgets_style, log_widgets_style])
  #
  # General
  #
  model_valid_ok_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['1']['name'], value="", stylesheets=[body_widgets_style])
  pitems.model_valid_ok = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['1']['color'], value = False)
  app_running_ok_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['2']['name'], value="", stylesheets=[body_widgets_style])
  pitems.app_running_ok = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['2']['color'], value = False)
  
  pitems.model_file_input = pn.widgets.FileInput(width=ui_config['file_inputs']['model_file_input']['width'], stylesheets=[body_widgets_style])
  pitems.motion_sensitivity = pn.widgets.FloatInput(name="Motion Sensitivity", value = 10.00,  stylesheets=[body_widgets_style])
  pitems.motion_sensitivity_label = pn.widgets.StaticText(name="", value="", styles=motion_detection_widgets_style)
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
  body1_widgetbox = pn.WidgetBox (name=ui_config['widgetboxes']['body1']['name'], styles=body_wb_style)
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
  pitems.capture_show = pn.pane.Image(os.path.join(ui_config['misc']['files_dir'], ui_config['misc']['empty_image']), width=ui_config['misc']['image_size'])
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
  inputs_widgetbox.append(pn.Row(
     pn.Column(pitems.capture_btn),
    )
  )
  inputs_widgetbox.append(pn.Row(
     pn.Column(pitems.motion_sensitivity),
    )
  )
  inputs_widgetbox.append(pn.Row(
     pn.Column(pitems.motion_sensitivity_label),
    )
  )

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