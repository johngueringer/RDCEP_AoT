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


class Sensor(object):
    """Sensor class for encapsulating data in AoT sensors.

    INSTANCE VARIABLES
        code        :  str   : Model of the AoT sensor
        data        :  list  : list of data points (datetime, float) tuples
        sensor_name :  str   : Full name of sensor
        dtype       :  list  : list of types of data (type of data, units) tuples
        context     :  str   : Additional sensor info
    """
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

    def add_point(self, line):
        """Add one data point to the Sensor from a formatted string.

        :param line : Formatted line containing data to be added
        :type  line : str
        :return     : None
        :rtype      : None
        """
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
    
    def plot_timeseries(self, subplot=None):
        """Create a timeseries plot from the data in the Sensor.

        :param subplot : None
        :type  subplot : plt.subplot
        :return        : Subplot of timeseries
        :rtype         : plt.subplot
        """
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

            xlab = 'Time'
            ylab_tmpl = '{} ({})'
            ylab = ylab_tmpl.format(type0, units)
            title_tmpl = '{}: {}\n{} - {}'
            title = title_tmpl.format(name, type0, strt, stp)

            fig = plt.figure() 
            ax1 = plt.subplot()
            ax1.plot(x, y, 'r-', label=type)
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

            xlab = 'Time'
            ylab_tmpl = '{} ({})'
            ylab = ylab_tmpl.format(type0, units)
            title_tmpl = '{}: {}\n{} - {}'
            title = title_tmpl.format(name, type0, strt, stp)
            subplot.plot(x, y, 'r-', label=type0)
            handles, labels = subplot.get_legend_handles_labels()
            subplot.set_xlabel(xlab)
            subplot.set_ylabel(ylab)
            subplot.set_title(title)
       

class DualSensor(Sensor):
    """Dual Sensor subclass for AoT sensors that collect two types of data:

    ADDITIONAL VARIABLES
        data2       :  list   : Second list of data points (datetime, float) tuples
    """

    def __init__(self, code):
        super(DualSensor, self).__init__(code)
        self._data2 = []
    
    @property
    def data2(self):
        return self._data2
    
    def add_point(self, line):
        """Add one data point to the DualSensor from a formatted string.

        :param line : Formatted line containing data to be added
        :type  line : str
        :return     : None
        :rtype      : None
        """
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
    
    def plot_timeseries(self, subplot=None):
        """Create a timeseries plot from the data in the DualSensor.

        :param subplot : None
        :type  subplot : plt.subplot
        :return        : Subplot of timeseries
        :rtype         : plt.subplot
        """
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

            xlab = 'Time'

            ylab_tmpl = '{} ({})'
            y1lab = ylab_tmpl.format(type1, unit1)
            y2lab = ylab_tmpl.format(type2, unit2)

            title_tmpl = '{}: {} and {}\n{} - {}'
            title = title_tmpl.format(name, type1, type2, strt, stp)

            fig = plt.figure() 
            ax1 = plt.subplot()
            ln1 = ax1.plot(x, y1, 'r-', label=y1lab)
            ax2 = ax1.twinx()
            ln2 = ax2.plot(x, y2, 'b-', label=y2lab)
            
            lns = ln1 + ln2
            labs = [l.get_label() for l in lns]
            ax1.legend(lns, labs, loc='upper left', bbox_to_anchor=(0.95, 1), labelspacing=0.5)
            
            ax1.set_xlabel(xlab)
            ax1.set_ylabel(y1lab)
            ax1.set_title(title)

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

            xlab = 'Time'

            ylab_tmpl = '{} ({})'
            y1lab = ylab_tmpl.format(type1, unit1)
            y2lab = ylab_tmpl.format(type2, unit2)

            title_tmpl = '{}: {} and {}\n{} - {}'
            title = title_tmpl.format(name, type1, type2, strt, stp)

            ln1 = subplot.plot(x, y1, 'r-', label=y1lab)
            ax2 = subplot.twinx()
            ln2 = ax2.plot(x, y2, 'b-', label=y2lab)
            
            lns = ln1 + ln2
            labs = [l.get_label() for l in lns]
            subplot.legend(lns, labs, loc='upper left', bbox_to_anchor=(0.95, 1), labelspacing=0.5)
            
            subplot.set_xlabel(xlab)
            subplot.set_ylabel(y1lab)
            subplot.set_title(title)

            ax2.set_ylabel(y2lab)
    
    def plot_correlation(self):
        """Correlate the two sets of data in the DualSensor and plot
        the correlation.

        :return        : Subplot of timeseries
        :rtype         : plt.subplot
        """
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


class GridSensor(Sensor):
    """Grid Sensor subclass for the AoT IR grid sensor.

    This class overrides methods from the Sensor class to properly work
    with grid data.
    """
    def __init__(self, code):
        super(GridSensor, self).__init__(code)
    
    def add_point(self, line):
        """Add one data point to the GridSensor from a formatted string.

        :param line : Formatted line containing data to be added
        :type  line : str
        :return     : None
        :rtype      : None
        """
        arr = line.split(',')
        name = arr[0]
        timestamp = dt.datetime.strptime(arr[1], '%m/%d/%y %H:%M:%S')
        vals = []
        dtypes = []
        self._sensor_name = name

        data = arr[2:]
        context = []
        i = 0
        for datum in data:
            info = datum.split(';')
            type0 = info[0]
            unit = info[2]
            val = float(info[1])
            context.append(info[3])
            
            dtype = (type0, unit)
            dtypes.append(dtype)
            vals.append(val)
        
            self._dtype = dtypes
            
        self._context = context
        self._data.append((timestamp, vals))
          
    def sort_by_pixel(self):
        """Sort the data in the GridSensor by pixel.

        :return     : None
        :rtype      : None
        """
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
        
    def sort_by_time(self):
        """Sort the data in the GridSensor by time.

        :return     : None
        :rtype      : None
        """
        data = []
        pixs = self._data
        n = len(pixs[0])
        
        for i in range(n):
            time = pixs[0][i][0]
            dpoint = []
            for pix in pixs:
                point = pix[i][1]
                dpoint.append(point)
                
            val = (time, dpoint)
            data.append(val)
            
        self._data = data
    
    def plot_timeseries(self, subplots=None):
        """Create a timeseries plot for each pixel in the grid

        :param subplot : None
        :type  subplot : plt.subplot
        :return      : List of subplots for the pixels in the grid
        :rtype       : list
        """
        if subplots == None:
            pixs = self._data
            sub_plots = []
            l = 4
            w = 4
            grid = (l, w)
            for i in range(l):
                for j in range(w):
                    sub_plot = plt.subplot2grid(grid, (i, j), rowspan=1, colspan=1)
                    sub_plots.append(sub_plot)

            i = 1
            for sub_plot in sub_plots:
                pix = pixs[i]
                x, y = zip(*pix)
                sub_plot.plot_date(x, y, fmt='r-')
                sub_plot.set_xlabel('Time')
                sub_plot.set_ylabel('Temperature (C)')
                sub_plot.set_title(self._sensor_name + ": " + self._context[i])
                i+=1
            plt.subplots_adjust(wspace=0.2, hspace=1)

            return sub_plots
        else:
            i = 1
            for sub_plot in sub_plots:
                pix = pixs[i]
                x, y = zip(*pix)
                sub_plot.plot_date(x, y, fmt='r-')
                sub_plot.set_xlabel('Time')
                sub_plot.set_ylabel('Temperature (C)')
                sub_plot.set_title(self._sensor_name + ": " + self._context[i])
                i+=1
            plt.subplots_adjust(wspace=0.2, hspace=1)
    
    def plot_heatmap(self, subplots=None):
        """Create a heatmap for each pixel in the grid
        :param subplot : None
        :type  subplot : plt.subplot
        :return      : List of subplots for the pixels in the grid
        :rtype       : list
        """
        if subplots == None:
            pixs = self._data
            fig = plt.figure()
            sub_plots = []
            l = 4
            w = 4
            grid = (l, w)
            for i in range(l):
                for j in range(w):
                    sub_plot = plt.subplot2grid(grid, (i, j), rowspan=1, colspan=1)
                    sub_plots.append(sub_plot)
         
            i = 1
            for sub_plot in sub_plots:
                pix = pixs[i]
                y = zip(*pix)[1]
                sub_plot.pcolor(np.array([y]), cmap=cmaps.Reds)
                sub_plot.set_xlabel('Time')
                sub_plot.set_ylabel('Temperature (C)')
                sub_plot.set_title(self._sensor_name + ": " + self._context[i])
                i+=1
            plt.subplots_adjust(wspace=0.2, hspace=0.2)
            
            return sub_plots
        else:
            pixs = self._data
            i = 0
            for pix in pixs[0:]:
                sub_plot = subplots[i]
                y = zip(*pix)[1]
                sub_plot.pcolor(np.array([y]), cmap=cmaps.Reds)
                sub_plot.set_xlabel('Time')
                sub_plot.set_ylabel('Temperature (C)')
                sub_plot.set_title(self._sensor_name + ": " + self._context[i])
                i+=1
            plt.subplots_adjust(wspace=0.2, hspace=0.2)