#!/usr/bin/python3

import threading
import time

class AgentThread(threading.Thread):
    """
    thread checking if there are tokens for Actions requests in the pipe,
    and triggering the Action task in that case.
    There could be more than one Agents.
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
            if not self.queue.empty():
                request = self.queue.get()
                rc = request.execute()

    def join(self,timeout=None):
        """
        Stop the thread. Overriding this method required to handle Ctrl-C from console.
        :param timeout: The timeout for stopping the thread.
        """
        self.stopevent.set()
        threading.Thread.join(self, timeout)


