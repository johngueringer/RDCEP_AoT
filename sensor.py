#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Sensor class for encapsulating data in AoT sensors:
INSTANCE VARIABLES
    code        :  String  : Model of the AoT sensor
    data        :  Array   : list of data points (datetime, float) tuples
    sensor_name :  String  : Full name of sensor
    dtype       :  Array   : list of types of data (type of data, units) tuples
    context     :  String  : Additional sensor info
"""
class Sensor(object):
    def __init__(self, code):
        self._code = code
        self._data = []
        self._sensor_name = None
        self._dtype = []
        self._context = None

    @property
    def code(self):
        return self._code
        
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

    """
    Adds one data point to the Sensor from a formatted string
    
    :param line : Formatted line containing data to be added
    :type  line : String
    :return     : None
    :rtype      : void
    """
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
    
    """
    Creates a timeseries plot from the data in the Sensor
    
    :param None  : None
    :type  None  : void
    :return      : Subplot of timeseries
    :rtype       : matplotlib subplot
    """
    def plot_timeseries(self, subplot = None):
        if subplot is None:
            data = self._data
            dtype = self._dtype
            name = self._sensor_name

            x, y = zip(*data)
            type0, units = zip(*dtype)
            type0 = type0[0]
            units = units[0]

            n = len(x)
            strt = x[1].strftime("%m/%d/%y")
            stp = x[n - 1].strftime("%m/%d/%y")

            xlab = 'Time of Day'
            ylab_tmpl = '{} ({})'
            ylab = ylab_tmpl.format(type0, units)
            title_tmpl = '{}: {}\n{} - {}'
            title = title_tmpl.format(name, type0, strt, stp)

            fig = plt.figure() 
            ax1 = plt.subplot()
            ax1.plot(x, y, 'r-', label=type)
            handles, labels = ax1.get_legend_handles_labels()
            ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
            #ax1.gcf().autofmt_xdate()
            ax1.set_xlabel(xlab)
            ax1.set_ylabel(ylab)
            ax1.set_title(title)

            return ax1
        else:
            data = self._data
            dtype = self._dtype
            name = self._sensor_name

            x, y = zip(*data)
            type0, units = zip(*dtype)
            type0 = type0[0]
            units = units[0]

            n = len(x)
            strt = x[1].strftime("%m/%d/%y")
            stp = x[n - 1].strftime("%m/%d/%y")

            xlab = 'Time of Day'
            ylab_tmpl = '{} ({})'
            ylab = ylab_tmpl.format(type0, units)
            title_tmpl = '{}: {}\n{} - {}'
            title = title_tmpl.format(name, type0, strt, stp)

            subplot.plot(x, y, 'r-', label=type0)
            handles, labels = subplot.get_legend_handles_labels()
            subplot.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
            subplot.set_xlabel(xlab)
            subplot.set_ylabel(ylab)
            subplot.set_title(title)
            
    """
    Creates a timeseries plot from the data in the Sensor
    
    :param subplot  : Empty subplot
    :type  subplot  : matplotlib subplot
    :return         : None
    :rtype          : void
    """ 
        
"""
Dual Sensor subclass for AoT sensors that collect two types of data:
ADDITIONAL VARIABLES
    data2       :  Array   : Second list of data points (datetime, float) tuples
"""
class DualSensor(Sensor):
    def __init__(self, code):
        super(DualSensor, self).__init__(code)
        self._data2 = []
    
    @property
    def data2(self):
        return self._data2
    
    """
    Adds one data point to the DualSensor from a formatted string
    
    :param line : Formatted line containing data to be added
    :type  line : String
    :return     : None
    :rtype      : void
    """
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
    
    """
    Creates a timeseries plot from the data in the DualSensor
    
    :param None  : None
    :type  None  : void
    :return      : Subplot of timeseries
    :rtype       : matplotlib subplot
    """
    def plot_timeseries(self, subplot = None):
        if subplot is None:
            data = self._data
            data2 = self._data2
            dtype = self._dtype
            name = self._sensor_name

            x, y1 = zip(*data)
            y2 = zip(*data2)[1]

            types, units = zip(*dtype)
            type1 = types[0]
            type2 = types[1]
            unit1 = units[0]
            unit2 = units[1]

            n = len(x)
            strt = x[1].strftime("%m/%d/%y")
            stp = x[n - 1].strftime("%m/%d/%y")

            xlab = 'Time of Day'

            ylab_tmpl = '{} ({})'
            y1lab = ylab_tmpl.format(type1, unit1)
            y2lab = ylab_tmpl.format(type2, unit2)

            title_tmpl = '{}: {} and {}\n{} - {}'
            title = title_tmpl.format(name, type1, type2, strt, stp)

            fig = plt.figure() 
            ax1 = plt.subplot()
            ax1.plot(x, y1, 'r-', label=y1lab)
            handles, labels = ax1.get_legend_handles_labels()
            ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
            ax1.set_xlabel(xlab)
            ax1.set_ylabel(y1lab)
            ax1.set_title(title)

            ax2 = ax1.twinx()
            ax2.plot(x, y2, 'b-', label=y2lab)
            handles, labels = ax2.get_legend_handles_labels()
            ax2.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 0.95))
            ax2.set_ylabel(y2lab)

            return ax1, ax2
        else:
            data = self._data
            data2 = self._data2
            dtype = self._dtype
            name = self._sensor_name

            x, y1 = zip(*data)
            y2 = zip(*data2)[1]

            types, units = zip(*dtype)
            type1 = types[0]
            type2 = types[1]
            unit1 = units[0]
            unit2 = units[1]

            n = len(x)
            strt = x[1].strftime("%m/%d/%y")
            stp = x[n - 1].strftime("%m/%d/%y")

            xlab = 'Time of Day'

            ylab_tmpl = '{} ({})'
            y1lab = ylab_tmpl.format(type1, unit1)
            y2lab = ylab_tmpl.format(type2, unit2)

            title_tmpl = '{}: {} and {}\n{} - {}'
            title = title_tmpl.format(name, type1, type2, strt, stp)

            fig = plt.figure()
            subplot.plot(x, y1, 'r-', label=y1lab)
            handles, labels = subplot.get_legend_handles_labels()
            subplot.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
            subplot.set_xlabel(xlab)
            subplot.set_ylabel(y1lab)
            subplot.set_title(title)

            ax2 = subplot.twinx()
            ax2.plot(x, y2, 'b-', label=y2lab)
            handles, labels = ax2.get_legend_handles_labels()
            ax2.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 0.95))
            ax2.set_ylabel(y2lab)
    
    """
    Creates a timeseries plot from the data in the DualSensor
    
    :param subplot  : Empty subplot
    :type  None     : matplotlib subplot
    :return         : None
    :rtype          : void
    """
    
    """
    Correlates the two sets of data in the DualSensor and plots the correlation.
    
    :param None  : None
    :type  None  : void
    :return      : Subplot of correlation
    :rtype       : matplotlib subplot
    """
    def plot_correlation(self):
        data = self._data
        data2 = self._data2
        dtype = self._dtype
        name = self._sensor_name

        x, y1 = zip(*data)
        y2 = zip(*data2)[1]
        
        types, units = zip(*dtype)
        type1 = types[0]
        type2 = types[1]
        unit1 = units[0]
        unit2 = units[1]

        n = len(x)
        strt = x[1].strftime("%m/%d/%y")
        stp = x[n - 1].strftime("%m/%d/%y")
        
        corr = stats.pearsonr(y1, y2)[0]
        
        ylab_tmpl = '{} ({})'
        y1lab = ylab_tmpl.format(type1, unit1)
        y2lab = ylab_tmpl.format(type2, unit2)
        
        title_tmpl = '{}: {} v.s. {}\nCorrelation = {}\n{} - {}'
        title = title_tmpl.format(name, type1, type2, corr, strt, stp)
               
        fig = plt.figure() 
        ax1 = plt.subplot()
        ax1.plot(y1, y2, 'o', label=y2lab)
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
        #ax1.gcf().autofmt_xdate()
        ax1.set_xlabel(y1lab)
        ax1.set_ylabel(y2lab)
        ax1.set_title(title)
        
        return ax1

"""
Grid Sensor subclass for the AoT IR grid sensor. This class overrides methods from the Sensor class
to properly work with grid data
"""
class GridSensor(Sensor):
    def __init__(self, code):
        super(GridSensor, self).__init__(code)
    
    """
    Adds one data point to the GridSensor from a formatted string
    
    :param line : Formatted line containing data to be added
    :type  line : String
    :return     : None
    :rtype      : void
    """
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
            type0 = info[0]
            unit = info[2]
            val = float(info[1])
            context = info[3]
            
            dtype = (type0, unit)
            dtypes.append(dtype)
            vals.append(val)
        
            self._dtype = dtypes
            self._context = context
            
        self._data.append((timestamp, vals))
          
    """
    Sorts the data in the GridSensor by pixel.
    
    :param None : None
    :type  None : void
    :return     : None
    :rtype      : void
    """
    def sort_by_pixel(self):
        pixels = []
        for i in range(17):
            pix = []
            pixels.append(pix)

        j = 0
        for instance in self._data:
            time = instance[0]

            for pix in pixels:
                if j > 16:
                    j = 0
                
                val = instance[1][j]
                point = (time, val)
                pix.append(point)
                j+=1

        self._data = pixels 
    
    """
    Creates a timeseries plot for each pixel in the grid
    
    :param None  : None
    :type  None  : void
    :return      : List of subplots for the pixels in the grid
    :rtype       : Array
    
    """
    def plot_timeseries(self):
        pixs = self._data
        sub_plots = []
        l = 4
        w = 4
        grid = (l, w)
        for i in range(4):
            for j in range(4):
                sub_plot = plt.subplot2grid(grid, (i, j), rowspan=1, colspan=1)
                sub_plots.append(sub_plot)

        i = 0
        for sub_plot in sub_plots:
            pix = pixs[i]
            x, y = zip(*pix)
            sub_plot.plot_date(x, y, fmt='r-')
            plt.gcf().autofmt_xdate()
            plt.xlabel('Time')
            plt.ylabel('Temperature (C)')
            plt.grid(True)
            i+=1

        return sub_plots
