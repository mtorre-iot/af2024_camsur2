#
# Mario Torre - 01/29/2024
#
import panel as pn
from dateutil import tz
from enum import Enum
import shutil
import hcc2sdk
from hcc2sdk.classes.variablemodel import quality_enum

class Severity (Enum):
    SUCCESS = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    @staticmethod
    def convert_string_to_severity(type):
        type = type.lower()
        if type == "success":
            return Severity.SUCCESS
        if type == "info":
            return Severity.INFO
        if type == "warning":
            return Severity.WARNING
        return Severity.ERROR



def send_notification(format, data, type, duration):

    pn.state.notifications.position = 'top-right'
    severity = Severity.convert_string_to_severity(type)
    message = format.format(data)
    duration = duration * 1000
    if severity == Severity.SUCCESS:
        pn.state.notifications.success(message, duration=duration)
    elif severity == Severity.INFO:
        pn.state.notifications.info(message, duration=duration)
    elif severity == Severity.WARNING:
        pn.state.notifications.warning(message, duration=duration)
    else:
        pn.state.notifications.error(message, duration=duration)
    
def convertUTCToLocalDateTime(dt):
    rtn = None
    if dt != None:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = dt.replace(tzinfo=from_zone)
        rtn = utc.astimezone(to_zone)
    return rtn

def update_screen(db_item, pitem_value, pitem_ts, pitem_quality, ui_config):

    if db_item is not None:
        pitem_value.value = ui_config['misc']['float_format'] % db_item.value
        local_ts = convertUTCToLocalDateTime(db_item.timestamp)
        pitem_ts.value =local_ts.strftime(ui_config['misc']['datetime_format'])
        pitem_quality.value = str(quality_enum.convert_quality_to_string(db_item.quality))    

def copyFile(src, dst):
    shutil.copyfile(src, dst)
