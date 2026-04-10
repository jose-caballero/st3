#!/usr/bin/python3

import threading
import time

class HarvestThread(threading.Thread):
    """
    thread checking if there are request for Actions and put them in the pipe,
    """

    def __init__(self, queue):
        """
        :param Queue queue: A queue that is used to fetch new requests.
        """
        threading.Thread.__init__(self) # init the thread
        self.stopevent = threading.Event()
        self.queue = queue

    def run(self):
        """
        Method called by thread.start()
        Main functional loop.
        """
        while not self.stopevent.isSet():
            time.sleep(1)
            requests = self._find_new_requests()
            for request in requests:
                self.queue.put(request)
    
    def join(self,timeout=None):
        """
        Stop the thread. Overriding this method required to handle Ctrl-C from console.
        :param timeout: The timeout for stopping the thread.
        """
        self.stopevent.set()
        threading.Thread.join(self, timeout)


