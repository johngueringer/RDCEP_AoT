#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime as dt


class Sensor(object):
    def __init__(self, code):
        self.code = code
        self._data = []
        self._sensor_name = None
        self._dtype = []
        self._context = None

    @property
    def data(self):
        return self._data


    @property
    def sensor_name(self):
        return self._sensor_name

    @property
    def dtype(self):
        return self._dtype

    @property
    def context(self):
        return self._context

    def add_point(self, line):
        arr = line.split(',')
        name = arr[0]
        timestamp = dt.datetime.strptime(arr[1], '%m/%d/%y %H:%M:%S')
        dtypes = []
        self._sensor_name = name

        data = arr[2:]
        for datum in data:
            info = datum.split(';')
            type = info[0]
            unit = info[2]
            val = (timestamp, float(info[1]))
            context = info[3]
            
            dtype = (type, unit)
            dtypes.append(dtype)
            
            self._data.append(val)
            self._dtype = dtypes
            self._context = context
    
class DualSensor(Sensor):
    def __init__(self, code):
        super(DualSensor, self).__init__(code)
        self._data2 = []
    
    @property
    def data2(self):
        return data2
    
    @property
    def add_point(self, line):
        arr = line.split(',')
        name = arr[0]
        timestamp = dt.datetime.strptime(arr[1], '%m/%d/%y %H:%M:%S')
        dtypes = []
        self._sensor_name = name

        data = arr[2:]
        i = 0
        for datum in data:
            info = datum.split(';')
            type = info[0]
            unit = info[2]
            val = (timestamp, float(info[1]))
            context = info[3]
            
            dtype = (type, unit)
            dtypes.append(dtype)
            
            self._dtype = dtypes
            self._context = context
            if i == 0:
                self._data.append(val)
            else:
                self._data2.append(val)
            i+=1
            
class GridSensor(Sensor):
    def __init__(self, code):
        super(GridSensor, self).__init__(code)
        
    def add_point(self, line):
        arr = line.split(',')
        name = arr[0]
        timestamp = dt.datetime.strptime(arr[1], '%m/%d/%y %H:%M:%S')
        vals = []
        dtypes = []
        self._sensor_name = name

        data = arr[2:]
        i = 0
        for datum in data:
            info = datum.split(';')
            type = info[0]
            unit = info[2]
            val = (timestamp, float(info[1]))
            context = info[3]
            
            dtype = (type, unit)
            dtypes.append(dtype)
            vals.append(val)
        
            self._dtype = dtypes
            self._context = context
            
        self._data.append(vals)
            