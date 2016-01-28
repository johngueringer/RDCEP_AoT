#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import datetime as dt
from ConfigParser import ConfigParser
from constants import SENSOR_CODES, GRID_SENSOR, DATA_URI
from sensor import Sensor, GridSensor, DualSensor


# config = ConfigParser('config.ini')


class Node(object):
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
        grid_sensor.parse()

    def makeURLs(self, strt_dte, stp_dte):
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
        return dt.datetime.strptime(s, '%m/%d/%y %H:%M:%S')