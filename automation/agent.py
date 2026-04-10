#!/usr/bin/python3

import threading
import time

class AgentThread(threading.Thread):
    """
    thread checking if there are tokens for Actions requests in the pipe,
    and triggering the Action task in that case.
    There could be more than one Agents.
    """

    def __init__(self, mgr):
        """
        :param ActionManager mgr: reference to the ActionManager object
                                  that created this thread
        """
        threading.Thread.__init__(self) # init the thread
        self.stopevent = threading.Event()
        self.mgr = mgr 

    def run(self):
        """
        Method called by thread.start()
        Main functional loop.
        """
        while not self.stopevent.isSet():
            time.sleep(1)
            request = self.mgr.get_request()
            if request:
                request.execute()

    def join(self,timeout=None):
        """
        Stop the thread. Overriding this method required to handle Ctrl-C from console.
        :param timeout: The timeout for stopping the thread.
        """
        self.stopevent.set()
        threading.Thread.join(self, timeout)


