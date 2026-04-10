#!/usr/bin/python3

import sys
from automation.actionmgr import ActionManager

class TriggerCLI:
    """
    class to start the daemon that handle Requests
    for Actions
    """
    def __init__(self, conf_path):
        self.actionmanager = ActionManager()

    def run(self):
        try:
            # Call the run method of the actionmanager to start the daemon
            self.actionmanager.run()
        except KeyboardInterrupt:
            # If a KeyboardInterrupt (Ctrl+C) is caught
            # initiate a graceful shutdown.
            self.actionmanager.shutdown()
            sys.exit(0)
        except ImportError as errorMsg:
            # If an ImportError occurs
            # exit with status code 1.
            sys.exit(1)
        except:
            # For any other exceptions exit
            # with status code 1.
            sys.exit(1)


