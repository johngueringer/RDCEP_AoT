#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import datetime as dt
from ConfigParser import ConfigParser
from constants import SENSOR_CODES, GRID_SENSOR, DATA_URI
from sensor import Sensor, GridSensor, DualSensor
import numpy as np
import matplotlib as mtplt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cmaps
import scipy.stats as stats


# config = ConfigParser('config.ini')


class Node(object):
    """Node class for encapsulating AoT sensor data:

    INSTANCE VARIABLES
        node     : str     : name of the AoT node
        sensors  : dict    : Dictionary of Sensor objects
    """

    def __init__(self, node):
        self._node = node
        self._sensors = {k: [] for k in SENSOR_CODES}

    @property
    def latlon(self):
        return None

    @property
    def node(self):
        return self._node

    @property
    def sensors(self):
        return self._sensors

    def sensor(self, code):
        return next((v for k, v in self.sensors.iteritems() if k == code), None)

    def pull_all(self, strt, stp):
        """Pull the AoT sensor data from the specified start time to
        the specified stop time; store the data in the Sensor objects of
        the sensors dictionary.

        :param strt : First date from which to start pulling data
        :type  strt : str

        :param stp  : Last date from which data will be pulled
        :type  stp  : str

        :return     : This method stores the data from wa8.gl in appropriate
                      Sensor objects
        :rtype      : None

        """
        urls = self.makeURLs(strt, stp)
        sensors = {'MLX90614ESF-DAA': Sensor,
                       'D6T-44L-06': GridSensor,
                       'TMP421': Sensor,
                       'BMP180': DualSensor,
                       'PDV_P8104': Sensor,
                       'Thermistor_NTC_PR103J2': Sensor,
                       'HIH6130': DualSensor,
                       'SHT15': DualSensor,
                       'DS18B20': Sensor,
                       'RHT03': DualSensor,
                       'SHT75': DualSensor,
                       'HIH4030': Sensor,
                       'GA1A1S201WP': Sensor,
                       'MAX4466': Sensor,
                       'HTU21D': DualSensor}
        
        for k, v in sensors.iteritems():
            self._sensors[k] = v(k)

        for url in urls:
            try:
                request = urllib2.Request(url)
                handle = urllib2.urlopen(request)
                lines = handle.readlines()

                for line in lines:
                    code = line.split(',')[0].split('.')[0]
                    self.sensor(code).add_point(line)
            except:
                print "Missing data from: " + url
                
        grid_sensor = self.sensor('D6T-44L-06')
        grid_sensor.sort_by_pixel()

    def makeURLs(self, strt_dte, stp_dte):
        """Generate a list of URLs from which to pull AoT data.

        :param strt_dte : First date from which URLs will be generated
        :type  strt_dte : str

        :param stp_dte  : Last date from which URLs will be generated
        :type  stp_dte  : str

        :return         : List of URLs from which to pull data
        :rtype          : list
        """
        urls = []

        strt_dte_data = strt_dte.split('-')
        stp_dte_data = stp_dte.split('-')

        strt = dt.datetime(int(strt_dte_data[2]), int(strt_dte_data[0]), int(strt_dte_data[1]))
        stp = dt.datetime(int(stp_dte_data[2]), int(stp_dte_data[0]), int(stp_dte_data[1]))
        diff = stp - strt

        total_hrs = (diff.days + 1) * 24
        delta = dt.timedelta(hours=1)

        for i in range(total_hrs):
            if strt.month < 10:
                mm = '0' + str(strt.month)
            else:
                mm = str(strt.month)
            if strt.day < 10:
                dd = '0' + str(strt.day)
            else:
                dd = str(strt.day)
            if strt.hour < 10:
                hh = '0' + str(strt.hour)
            else:
                hh = str(strt.hour)
            yy = str(strt.year)

            url = DATA_URI.format(self.node, mm, dd, yy, hh)
            urls.append(url)
            strt += delta

        return urls
    

    def to_datetime(self, s):
        """Convert formatted string to datetime object

        :param s  : Formatted string
        :type  s  : str
        :return   : datetime object representing the date
        :rtype    : dt.datetime
        """
        return dt.datetime.strptime(s, '%m/%d/%y %H:%M:%S')
    
    def plot_all(self):
        """Plot data contained in all the sensors of the AoT node."""
        sub_plots = []
        l = 5
        w = 3
        grid = (l, w)
        for i in range(l):
            for j in range(w):
                sub_plot = plt.subplot2grid(grid, (i, j), rowspan=1, colspan=1)
                sub_plots.append(sub_plot)

        sensors = self._sensors.iteritems()
        for sub_plot in sub_plots:
            sensor = sensors.next()[1]
            if isinstance(sensor, GridSensor):
                pass
            else:
                sensor.plot_timeseries(sub_plot)
        
        plt.show()
