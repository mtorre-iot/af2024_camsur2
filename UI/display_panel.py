#
# Mario Torre - 01/29/2024
#
import asyncio
import os
import json
import panel as pn
import pandas as pd
from datetime import datetime
from filelock import FileLock
from UI.ui_design_lib import copyFile, send_notification
from UI.ui_styles import header_widgets_style, body_wb_style, subbody_wb_style, log_widgets_style, body_widgets_style, header_wb_style
from UI.classes.model import Model


def display_panel(logger, stream, config, ui_config, pitems, webport, new_model_event):
  #
  # Callbacks
  #
  def capture_button_callback(event):
    logger.info("Capture Button pressed!!")


  def model_load_file_callback(event):
    
    pitems.model_valid_ok.value = False # assume model will be invalid
    full_file_name = pitems.model_file_input.filename
    file_contents = pitems.model_file_input.value
    if file_contents is None:
      send_notification(ui_config['notifications']['FILEMP']['message'], None, ui_config['notifications']['FILEMP']['severity'], ui_config['notifications']['FILEMP']['duration'])
      logger.warning(ui_config['notifications']['FILEMP']['message'])
      return
    #
    # try to save model file
    #
    try:
      #pitems.model_file_input.save(os.path.join(ui_config['general']['temp_model_dir'], full_file_name))
      pitems.model_file_input.save(os.path.join(ui_config['general']['model_dir'], full_file_name))
    except Exception as e:
      send_notification(ui_config['notifications']['FILNSAV']['message'], str(e), ui_config['notifications']['FILNSAV']['severity'], ui_config['notifications']['FILNSAV']['duration'])
      logger.warning(ui_config['notifications']['FILNSAV']['message'].format(str(e)))
      return
    #
    # Check if model file contents are valid 
    #
    try:
        #lookup_df = pd.read_csv(os.path.join(ui_config['general']['temp_model_dir'], full_file_name))
        lookup_df = pd.read_csv(os.path.join(ui_config['general']['model_dir'], full_file_name))
    except Exception as e:
      send_notification(ui_config['notifications']['FILINVD']['message'], str(e), ui_config['notifications']['FILINVD']['severity'], ui_config['notifications']['FILINVD']['duration'])
      logger.warning(ui_config['notifications']['FILINVD']['message'].format(str(e)))
      return
      #
      # file read. We assume that:
      # column 1: Delta Pressure (DP)
      # column 2: Gas lift injection rate
      # column 3: Estimated Oil Rate
      #
      # check if file got (at least) 3 columns
      #
    if len(lookup_df.columns) < 3:
      send_notification(ui_config['notifications']['FILINVD']['message'], "invalid number of columns", ui_config['notifications']['FILINVD']['severity'], ui_config['notifications']['FILINVD']['duration'])
      logger.warning(ui_config['notifications']['FILINVD']['message'].format("invalid number of columns"))
      return
    #
    # copy temporary file into the model/ subdirectory
    #
    # try:
    #   copyFile(os.path.join(ui_config['general']['temp_model_dir'], full_file_name), os.path.join(ui_config['general']['model_dir'], full_file_name))
    # except Exception as e:
    #   send_notification(ui_config['notifications']['TFLNSAV']['message'], str(e), ui_config['notifications']['TFLNSAV']['severity'], ui_config['notifications']['TFLNSAV']['duration'])
    #   logger.warning(ui_config['notifications']['TFLNSAV']['message'].format(str(e)))
    #   return
    #
    # update the model state file
    #
    app_model = Model()
    app_model.model_file_name = full_file_name
    app_model.update_timestamp = datetime.now().strftime(ui_config['misc']['datetime_format'])

    model_desc_file_name = os.path.join(ui_config['general']['model_dir'], ui_config['general']['model_state_file_name'])
    model_file_lock_name = os.path.join(ui_config['general']['model_dir'], ui_config['general']['model_file_lock_name'])
    json_object = json.dumps(app_model.__dict__)
    with FileLock(model_file_lock_name):
      with open(model_desc_file_name, "w") as file:
        file.write(json_object)
    #
    # All seems fine.
    #
    send_notification(ui_config['notifications']['FILSUC']['message'], full_file_name, ui_config['notifications']['FILSUC']['severity'], ui_config['notifications']['FILSUC']['duration'])
    logger.info(ui_config['notifications']['FILSUC']['message'].format(full_file_name))
    pitems.model_file_name.value = full_file_name
    pitems.model_file_update_ts.value = app_model.update_timestamp
    pitems.model_valid_ok.value = True
    #
    # let the app new that a new model was deployed!
    #
    new_model_event.set()

    return
  #
  # Panel Initialization and general configuration
  #
  pn.extension(design=ui_config['template']['design'])
  pn.extension(notifications=True)
  pn.config.theme = ui_config['template']['theme']

  pn.config.raw_css.append(header_widgets_style)
  pn.config.raw_css.append(body_widgets_style)
  #
  # variables definitions 
  #
  # WHP (well head pressure):
  # pitems.whp_value = pn.widgets.StaticText(name=ui_config['texts']['whp_value']['name'], value = ui_config['texts']['whp_value']['init_value'], sizing_mode = ui_config['texts']['whp_value']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.whp_ts = pn.widgets.StaticText(name=ui_config['texts']['whp_ts']['name'], value = ui_config['texts']['whp_ts']['init_value'], sizing_mode = ui_config['texts']['whp_ts']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.whp_quality = pn.widgets.StaticText(name=ui_config['texts']['whp_quality']['name'], value = ui_config['texts']['whp_quality']['init_value'], sizing_mode = ui_config['texts']['whp_quality']['sizing_mode'], stylesheets=[body_widgets_style])
  # #
  # # FLP (flow line pressure):
  # pitems.flp_value = pn.widgets.StaticText(name=ui_config['texts']['flp_value']['name'], value = ui_config['texts']['flp_value']['init_value'], sizing_mode = ui_config['texts']['flp_value']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.flp_ts = pn.widgets.StaticText(name=ui_config['texts']['flp_ts']['name'], value = ui_config['texts']['flp_ts']['init_value'], sizing_mode = ui_config['texts']['flp_ts']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.flp_quality = pn.widgets.StaticText(name=ui_config['texts']['flp_quality']['name'], value = ui_config['texts']['flp_quality']['init_value'], sizing_mode = ui_config['texts']['flp_quality']['sizing_mode'], stylesheets=[body_widgets_style])
  
  # #
  # # GL Injection Rate:
  # pitems.gl_injection_rate_value = pn.widgets.StaticText(name=ui_config['texts']['gl_injection_rate_value']['name'], value = ui_config['texts']['gl_injection_rate_value']['init_value'], sizing_mode = ui_config['texts']['gl_injection_rate_value']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.gl_injection_rate_ts = pn.widgets.StaticText(name=ui_config['texts']['gl_injection_rate_ts']['name'], value = ui_config['texts']['gl_injection_rate_ts']['init_value'], sizing_mode = ui_config['texts']['gl_injection_rate_ts']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.gl_injection_rate_quality = pn.widgets.StaticText(name=ui_config['texts']['gl_injection_rate_quality']['name'], value = ui_config['texts']['gl_injection_rate_quality']['init_value'], sizing_mode = ui_config['texts']['gl_injection_rate_quality']['sizing_mode'], stylesheets=[body_widgets_style])
  # #
  # # Oil Rate estimation:
  # pitems.oil_rate_est_value = pn.widgets.StaticText(name=ui_config['texts']['oil_rate_est_value']['name'], value = ui_config['texts']['oil_rate_est_value']['init_value'], sizing_mode = ui_config['texts']['oil_rate_est_value']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.oil_rate_est_ts = pn.widgets.StaticText(name=ui_config['texts']['oil_rate_est_ts']['name'], value = ui_config['texts']['oil_rate_est_ts']['init_value'], sizing_mode = ui_config['texts']['oil_rate_est_ts']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.oil_rate_est_quality = pn.widgets.StaticText(name=ui_config['texts']['oil_rate_est_quality']['name'], value = ui_config['texts']['oil_rate_est_quality']['init_value'], sizing_mode = ui_config['texts']['oil_rate_est_quality']['sizing_mode'], stylesheets=[body_widgets_style])
  # #
  # # Model:
  # pitems.model_file_name = pn.widgets.StaticText(name=ui_config['texts']['model_file_name']['name'], value = ui_config['texts']['model_file_name']['init_value'], sizing_mode = ui_config['texts']['model_file_name']['sizing_mode'], stylesheets=[body_widgets_style])
  # pitems.model_file_update_ts = pn.widgets.StaticText(name=ui_config['texts']['model_file_update_ts']['name'], value = ui_config['texts']['model_file_update_ts']['init_value'], sizing_mode = ui_config['texts']['model_file_update_ts']['sizing_mode'], stylesheets=[body_widgets_style])

  pitems.capture_btn = pn.widgets.Button(name=ui_config['buttons']['capture_btn']['name'], width=ui_config['buttons']['capture_btn']['width'], button_type=ui_config['buttons']['capture_btn']['type'], stylesheets=[body_widgets_style])
  pitems.capture_btn.on_click(capture_button_callback)
  #
  # Log:
  log_text_area_input = pn.widgets.TextAreaInput(name="", sizing_mode="stretch_both", stylesheets=[body_widgets_style, log_widgets_style])
  #
  # General
  model_valid_ok_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['1']['name'], value="", stylesheets=[body_widgets_style])
  pitems.model_valid_ok = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['1']['color'], value = False)
  app_running_ok_label = pn.widgets.StaticText(name=ui_config["boolean_status"]['2']['name'], value="", stylesheets=[body_widgets_style])
  pitems.app_running_ok = pn.widgets.BooleanStatus(color=ui_config["boolean_status"]['2']['color'], value = False)
  
  pitems.model_file_input = pn.widgets.FileInput(width=ui_config['file_inputs']['model_file_input']['width'], stylesheets=[body_widgets_style])
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
  #
  # # Titles:
  # whp_title = pn.pane.Markdown(ui_config['texts']['whp']['name'])
  # flp_title = pn.pane.Markdown(ui_config['texts']['flp']['name'])
  # gl_injection_rate_title = pn.pane.Markdown(ui_config['texts']['gl_injection_rate']['name'])
  # oil_rate_est_title = pn.pane.Markdown(ui_config['texts']['oil_rate_est']['name'])

  # #button1 = pn.widgets.Button(name="button1",  width=220, button_type="success", stylesheets=[body_widgets_style])

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
  
  # inputs_widgetbox.append(flp_title)
  # #
  # ## COLUMN 1
  # #
  # inputs_widgetbox.append(pn.Row(
  #   pn.Column(pitems.flp_value),
  #   pn.Column(pitems.flp_ts),
  #   pn.Column(pitems.flp_quality)
  #   )
  # )
  # inputs_widgetbox.append(gl_injection_rate_title)

  # inputs_widgetbox.append(pn.Row(
  #   pn.Column(pitems.gl_injection_rate_value),
  #   pn.Column(pitems.gl_injection_rate_ts),
  #   pn.Column(pitems.gl_injection_rate_quality)
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

  # model_widgetbox.append(model_title)

  # model_widgetbox.append(pn.Row(
  #   pn.Column(pitems.model_file_name),
  #   pn.Column(pitems.model_file_update_ts)
  #   )
  # )
  # model_widgetbox.append(pn.Row(
  #   pn.Column(pitems.model_file_input),
  #   pn.Column(pitems.model_load_btn),
  #   pn.Column(pn.Row(
  #       pn.Column(model_valid_ok_label, pitems.model_valid_ok),
  #       pn.Column(app_running_ok_label, pitems.app_running_ok)
  #       )
  #     )
  #   )
  # )
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