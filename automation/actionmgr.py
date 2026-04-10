#!/usr/bin/python3

import time
import queue
from automation.agent import AgentThread
from automation.harvest import HarvestThread 


class ActionManager:
    

    def __init__(self):
        self.queue = queue.Queue()
        self.harvest_thread = HarvestThread(self.queue)
        self.create_agent_threads()


    def create_agent_threads(self):
        """
        Create N threads Agent
        """
        self.agent_l = []
        n_agents = 3 
        # FIXME n_agents should be set in a config file
        for i in range(n_agents):
            self.agent_l.append(AgentThread(self.queue))


    def run(self):
        """
        perform actions for this daemon:
        start all harvest and agent threads,
        and wait for the daemon to be killed
        """
        self._start_threads()
        self._wait()

    def _start_threads(self):
        for agent in self.agent_l:
            agent.start()
        self.harvest_thread.start()

    def _wait(self):
        """
        keep the program running until a KeyboardInterrupt (Ctrl-C) is received
        """
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt):
            self.shutdown()
            raise

    def shutdown(self):
        """
        stopts all threads
        """
        self.harvest_thread.join()
        for agent in self.agent_l:
            agent.join()



