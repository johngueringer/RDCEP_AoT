from sensor import Sensor, DualSensor, GridSensor
from node import Node
import urllib2
import datetime as dt
from ConfigParser import ConfigParser
from constants import SENSOR_CODES, GRID_SENSOR, DATA_URI
import numpy as np
import matplotlib as mtplt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cmaps
import scipy.stats as stats


class AoT(object):
    """AoT class for encapsulating a list of Node objects:

    INSTANCE VARIABLES
        nodes   :   Array   : List of Nodes
    """
    def __init__(self, nodes, dtypes=None, strt=None, stp=None):
        self._nodes = {}
        
        if strt == None and stp == None:
            today = dt.datetime.now()
            delta = dt.timedelta(days=1)
            yesterday = today - delta
            ydate = yesterday.strftime("%m-%d-%y")
            self._strt_dte = ydate
            self._stp_dte = ydate
            
            if not dtypes:
                self.pull_from(nodes, ydate, ydate)
            else:
                self.pull_from(nodes, ydate, ydate, dtypes)
        
        elif stp == None:
            self._strt_dte = strt
            self._stp_dte = strt
                                          
            if not dtypes:
                self.pull_from(nodes, strt, strt)
            else:
                self.pull_from(nodes, strt, strt, dtypes)
        else:
            self._strt_dte = strt
            self._stp_dte = stp
                                          
            if not dtypes:
                self.pull_from(nodes, strt, stp)
            else:
                self._sensors = {}
                self.pull_from(nodes, strt, stp, dtypes)
    
    def pull_from(self, nodes, strt, stp, dtypes=None):
       for node in nodes:
            if dtypes == None:
               anode = Node(node, strt, stp)
            else:
                anode = Node(node, dtypes, strt, stp)
                
            self._nodes[node] = anode
    
    @property
    def nodes(self):
        return self._nodes
    
    @property
    def strt_dte(self):
        return self._strt_dte
    
    @property
    def stp_dte(self):
        return self._stp_dte                                      
    
    def add(self, node):
        """Add a Node object to the AoT object.

        :param node : Node object to be added
        :type  node : Node
        :return     : None
        :rtype      : void
        """
        self._nodes[node._node] = node
