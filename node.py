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

    def __init__(self, node, dtypes=None, strt=None, stp=None):
        self._node = node
        
        if strt == None and stp == None:
            today = dt.datetime.now()
            delta = dt.timedelta(days=1)
            yesterday = today - delta
            ydate = yesterday.strftime("%m-%d-%y")
            self._strt_dte = ydate
            self._stp_dte = ydate
            if not dtypes:
                self._sensors = {k: [] for k in SENSOR_CODES}
                self.pull_all(ydate, ydate)
            else:
                self._sensors = {}
                self.pull_select(dtypes, ydate, ydate)
        
        elif stp == None:
            self._strt_dte = strt
            self._stp_dte = strt
            if not dtypes:
                self._sensors = {k: [] for k in SENSOR_CODES}
                self.pull_all(strt, strt)
            else:
                self._sensors = {}
                self.pull_select(dtypes, strt, strt)
        else:
            self._strt_dte = strt
            self._stp_dte = stp
            if not dtypes:
                self._sensors = {k: [] for k in SENSOR_CODES}
                self.pull_all(strt, stp)
            else:
                self._sensors = {}
                self.pull_select(dtypes, strt, stp)

    @property
    def latlon(self):
        return None

    @property
    def node(self):
        return self._node

    @property
    def sensors(self):
        return self._sensors
    
    @property
    def strt_dte(self):
        return self._strt_dte
    
    @property
    def stp_dte(self):
        return self._stp_dte

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
        
    def pull_select(self, dtypes, strt, stp):
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
        
        for url in urls:
          #  try:
            request = urllib2.Request(url)
            handle = urllib2.urlopen(request)
            lines = handle.readlines()

            for line in lines[:15]:
                arr = self.get_type_from_line(line)
                if set(arr).intersection(dtypes):
                    code = line.split(',')[0].split('.')[0]
                    self._sensors[code] = sensors[code](code)
                    self.sensor(code).add_point(line)
          
            for line in lines[15:]:
                arr = self.get_type_from_line(line)
                if set(arr).intersection(dtypes):
                    code = line.split(',')[0].split('.')[0]
                    try:
                        self.sensor(code).add_point(line)
                    except:
                        self._sensors[code] = sensors[code](code)
                        self.sensor(code).add_point(line)
                    
          #  except:
          #      print "Missing data from: " + url
        
    def get_type_from_line(self, line):
        arr = line.split(",")
        data = arr[2:]
        dtypes = []
        
        for datum in data:
            parts = datum.split(";")
            dtypes.append(parts[0])
        
        return dtypes
    
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
    
    def plot_timeseries(self):
        """Plot data contained in all the sensors of the AoT node."""
        fig = plt.figure(figsize=(25, 15))
        figtitle = "AoT Node: {}\n{} - {}"
        figtitle = figtitle.format(self._node, self._strt_dte, self._stp_dte)
        fig.suptitle(figtitle, fontsize='x-large')
        
        sub_plots = []
        l = 3
        w = 5
        grid = (l, w)
        for i in range(l):
            for j in range(w):
                sub_plot = plt.subplot2grid(grid, (i, j), rowspan=1, colspan=1)
                sub_plots.append(sub_plot)
                
        i = 0
        sensors = self._sensors.iteritems()
        for sensor in sensors:
            sensor = sensor[1]
            sensor.plot_timeseries(sub_plots[i])
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            i+=1
        fig.autofmt_xdate()
        fig.savefig(self._node + ".png")
        plt.show()
