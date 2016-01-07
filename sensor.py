#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime as dt


class Sensor(object):
    def __init__(self, code, node):
        self.code = code
        self.node = node
        self._data = list()
        self._sensor_name = None
        self._timestamp = None
        self._units = None
        self._context = None

    @property
    def data(self):
        return self._data

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def sensor_name(self):
        return self._sensor_name

    @property
    def units(self):
        return self._units

    @property
    def context(self):
        return self._context

    def add_point(self, line):
        arr = line.split(',')
        name = arr[0]
        timestamp = dt.datetime.strptime(arr[1], '%m/%d/%y %H:%M:%S')
        units = []
        self._timestamp = timestamp

        data = arr[2:]
        for datum in data:
            info = datum.split(';')
            val = float(info[1])
            units.append(info[2])
            context = info[3]
            self._data = val
            self._units = units
            self._context = context




class GridSensor(Sensor):
    def parse(self, line):

        arr = line.split(',')
        name = arr[0]
        timestamp = dt.datetime.strptime(arr[1], '%m/%d/%y %H:%M:%S')
        sensor = {'sensorname': name,
                  'timestamp': timestamp}
        temps = []
        units = []
        pixels = []
        for content in arr[2:]:
            data = content.split(";")
            key = data[0]
            val = float(data[1])
            temps.append(val)
            units.append(data[2])
            pixels.append(data[3])

            sensor[key] = temps
            sensor['units'] = units
            sensor['context'] = pixels

        return sensor