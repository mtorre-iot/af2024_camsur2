#
# Mario Torre  - 01/30/2024
#
from queue import Empty

def display_datastore(logger, config, ui_config, pitems, display_queue):
    
    while True:
        try:
            message = display_queue.get(block=True)
        except Empty as e:
            message = ""
        if message != "":
            display_queue.task_done()
            #
            # Go through 