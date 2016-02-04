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

"""
AoT class for encapsulating a list of Node objects:
INSTANCE VARIABLES
    nodes   :   Array   : List of Nodes
"""
class AoT(object):
    def __init__(self):
        self._nodes = []
    
    @property
    def nodes(self):
        return self._nodes
    
    """
    Adds a Node object to the AoT object
    
    :param node : Node object to be added
    :type  node : Node
    :return     : None
    :rtype      : void
    """
    def add(self, node):
        self._nodes.append(node)