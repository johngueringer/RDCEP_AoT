import urllib2 as ulib2
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib as mtplt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cmaps
from matplotlib import animation as anim
import scipy.stats as stats
import time

"""
---------------FETCHING DATA---------------
"""

def makeURLs(node, strt_dte, stp_dte):
    base1 = "http://outworld.mcs.anl.gov/waggle-data/"
    base2 = "/data/data_"
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
        
        url = base1 + node + base2 + mm + '-' + dd + '-' + yy + '-' + hh + '.txt'
        urls.append(url)
        strt += delta
        
    return urls

def to_datetime(str):
    dtstr = str.split()
    datestr = dtstr[0]
    timestr = dtstr[1]
    
    date = datestr.split('/')
    mm = int(date[0])
    dd = int(date[1])
    yyyy = int(date[2]) + 2000
    
    time = timestr.split(':')
    h = int(time[0])
    m = int(time[1])
    s = int(time[2])
    
    dtobj = dt.datetime(yyyy, mm, dd, h, m, s)
    
    return dtobj

def to_sensor(line):
    contents = line.split(',')
    name = contents[0]
    timestamp = to_datetime(contents[1])
    units = []
    sensor = {'sensorname': name,
              'timestamp': timestamp}
    
    data = contents[2:]
    for datum in data:
        info = datum.split(';')
        key = info[0]
        val = float(info[1])
        units.append(info[2])
        context = info[3]
        
        sensor[key] = val
        sensor['units'] = units
        sensor['context'] = context
    
    return sensor

def to_sensorGrid(line):
    contents = line.split(',')
    name = contents[0]
    timestamp = to_datetime(contents[1])
    sensor = {'sensorname': name,
              'timestamp': timestamp}
    
    temps = []
    units = []
    pixels = []
    for content in contents[2:]:
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

def pull_all(node, strt, stp):
    urls = makeURLs(node, strt, stp)
    gridsensor = 'D6T-44L-06.Omron.2012'
    aot_node = {'MLX90614ESF-DAA': [],
                'D6T-44L-06': [],
                'TMP421': [],
                'BMP180': [],
                'PDV_P8104': [],
                'Thermistor_NTC_PR103J2': [],
                'HIH6130': [],
                'SHT15': [],
                'DS18B20': [],
                'RHT03': [],
                'SHT75': [],
                'HIH4030': [],
                'GA1A1S201WP': [],
                'MAX4466': [],
                'HTU21D': []}
    models = aot_node.keys()
    
    for url in urls:
        try:
            request = ulib2.Request(url)
            handle = ulib2.urlopen(request)
            lines = handle.readlines()

            for line in lines:
                if line.split(',')[0] == gridsensor:
                    sensor = to_sensorGrid(line)
                else:
                    sensor = to_sensor(line)

                model = sensor['sensorname'].split('.')[0]
                for mdl in models:
                    if model == mdl:
                        aot_node[mdl].append(sensor)
        except:
            print "Missing data from: " + url
        
    return aot_node



"""
---------------EXTRACTING DATA---------------
"""
def tempGridData(sensor):
    times = []
    pixels = []
    for i in range(17):
        pix = []
        pixels.append(pix)
    
    j = 1
    for instance in sensor:
        time = mdates.date2num(instance['timestamp'])
        times.append(time)

        for pix in pixels:
            if j > 16:
                j = 1
            pix.append(instance['Temperature'][j])
            j+=1
                
    return times, pixels

def extractData(sensor):
    std_keys = ['timestamp', 'sensorname', 'units', 'context']
    gridsensor = 'D6T-44L-06.Omron.2012'
    merged = 'merged'
    
    sample = sensor[0]
    senstype = sample['sensorname']
    context = sample['context']
    units = sample['units']
    keys = sample.keys()
    
    data_keys = []
    times = []
    set1 = []
    
    for key in keys:
        if key not in std_keys:
            data_keys.append(key)

    if senstype == gridsensor and context != merged:
        times, set1 = tempGridData(sensor)
        
        return {'time': times,
               'data': [set1],
               'data_keys': data_keys,
               'units': units}
    
    if len(data_keys) == 2:
        set2 = []
        for instance in sensor:
            key1 = data_keys[0]
            key2 = data_keys[1]
            datum1 = instance[key1]
            datum2 = instance[key2]
            time = instance['timestamp']
            
            set1.append(datum1)
            set2.append(datum2)
            times.append(time)
        
        return {'time': times,
               'data': [set1, set2],
               'data_keys': data_keys,
               'units': units}
    else:
        for instance in sensor:
            key = data_keys[0]
            datum = instance[key]
            time = instance['timestamp']
            
            set1.append(datum)
            times.append(time)
        
        return {'time': times,
               'data': [set1],
               'data_keys': data_keys,
               'units': units}


"""
---------------MANIPULATING DATA---------------
"""

def mean(values):
    avg = 0
    total = 0
    i = 0
    for value in values:
        total += value
        i += 1
        
    avg = total / i
    return avg
        
def mean_hrly_temp(sensor):
    hr_avgs = []
    j = 0
    n = len(sensor)
    time = sensor[0]['timestamp']
    hr = time.hour
    temps = []
    hr_temps = []
    times = [time]
    
    while(j < n):
        instance = sensor[j]
        curr_time = instance['timestamp']
        curr_hr = curr_time.hour
            
        if(hr == curr_hr):
            hr_temps.append(instance['Temperature'])
            j += 1
        else:
            avg = mean(hr_temps)
            temps.append(avg)
            hr = curr_hr
            times.append(curr_time)
            hr_temps = []
            
        if((j + 1) == n):
            avg = mean(hr_temps)
            temps.append(avg)
            hr = curr_hr
    
    return times, temps

def mean_hrly_tempGrid(sensor):
    hr_avgs = []
    i = 0
    j = 0
    n = len(sensor)
    time = sensor[0]['timestamp']
    hr = time.hour
    pixs = []
    hr_pixs = []
    for i in range(17):
        pix = []
        hr_pix = 0
        pixs.append(pix)
        hr_pixs.append(hr_pix)
    
    times = [time]
    
    while(j < n):
        instance = sensor[j]
        curr_time = instance['timestamp']
        curr_hr = curr_time.hour
            
        if(hr == curr_hr):
            grid = instance['Temperature']
            k = 0
            for item in grid:
                hr_pixs[k] += item
                k += 1
            i += 1
            j += 1
        else:
            avgs = []
            for hr_pix in hr_pixs:
                avg = hr_pix / i
                avgs.append(avg)
            i = 0
            k = 0
            for avg in avgs:
                pixs[k].append(avg)
                k += 1
            hr = curr_hr
            times.append(curr_time)
            hr_pixs = [0, 0, 0, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0,
                       0, 0, 0, 0]
            
        if((j + 1) == n):
            avgs = []
            for hr_pix in hr_pixs:
                avg = hr_pix / i
                avgs.append(avg)
            i = 0
            k = 0
            for avg in avgs:
                pixs[k].append(avg)
                k += 1
    
    return times, pixs

def mergeGrid(sensor):
    new_sensor = []
    for i in range(len(sensor)):
        instance = sensor[i]
        unit = instance['units'][0]
        grid = instance['Temperature']
        avg = mean(grid)
        
        instance['Temperature'] = avg
        instance['units'] = [unit]
        instance['context'] = 'merged'
        
        new_sensor.append(instance)
        
    return new_sensor
        

"""
---------------GRAPHING DATA---------------
"""
def tempGrid_timeseries(times, pixs):
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
        sub_plot.plot_date(times, pixs[i], fmt='r-')
        plt.gcf().autofmt_xdate()
        plt.xlabel('Time')
        plt.ylabel('Temperature (C)')
        plt.grid(True)
        i+=1

    plt.show()

def tempGrid_heatmap(pixs):
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
        sub_plot.pcolor(np.array([pixs[i]]), cmap=cmaps.Reds)
        plt.gcf().autofmt_xdate()
        plt.xlabel('Time')
        plt.ylabel('Temperature (C)')
        plt.grid(True)
        i+=1

    plt.show()

def temp_heatmap(times, temps):
    subplot1 = plt.subplot2grid((2,1), (0, 0), rowspan=1, colspan=1)
    subplot1.pcolor(np.array([temps]), cmap=cmaps.Reds)

    subplot2 = plt.subplot2grid((2,1), (1, 0), rowspan=1, colspan=1)
    subplot2.plot_date(times, temps, fmt='r-')
    plt.gcf().autofmt_xdate()
    plt.xlabel('Time')
    plt.ylabel('Temperature')
    plt.grid(True)
    plt.show()

def plot_timeseries(sensor):
    gridsensor = 'D6T-44L-06.Omron.2012'
    merged = 'merged'
    
    sensor_data = extractData(sensor)
    times = sensor_data['time']
    data = sensor_data['data']
    dkeys = sensor_data['data_keys']
    units = sensor_data['units']
    set1 = data[0]
    
    if len(data) == 2:
        set2 = data[1]
        
        title = sensor[0]['sensorname'] + ': ' + sensor[0]['timestamp'].strftime('%m-%d-%Y')
        y1lab = dkeys[0] + ' (' + units[1] + ')'
        y2lab = dkeys[1] + ' (' + units[0] + ')'
               
        fig = plt.figure() 
        ax1 = plt.subplot()
        ax1.plot(times, set1, 'r-', label=y1lab)
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
        #ax1.gcf().autofmt_xdate()
        ax1.set_xlabel('Time (hr)')
        ax1.set_ylabel(y1lab)
        ax1.set_title(title)
        
        ax2 = ax1.twinx()
        ax2.plot(times, set2, 'b-', label=y2lab)
        handles, labels = ax2.get_legend_handles_labels()
        ax2.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 0.95))
        ax2.set_ylabel(y2lab)
        plt.show()
        
    elif sensor[0]['sensorname'] == gridsensor and sensor[0]['context'] != merged:
        tempGrid_timeseries(times, set1)
        
    else:
        title = sensor[0]['sensorname'] + ': ' + sensor[0]['timestamp'].strftime('%m-%d-%Y')
        ylab = dkeys[0] + ' (' + units[0] + ')'
        fig = plt.figure() 
        ax1 = plt.subplot()
        ax1.plot(times, set1, 'r-', label=ylab)
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
        #ax1.gcf().autofmt_xdate()
        ax1.set_xlabel('Time (hr)')
        ax1.set_ylabel(ylab)
        ax1.set_title(title)
        plt.show()
        
def plot_correlation(sensor):
    sensor_data = extractData(sensor)
    times = sensor_data['time']
    data = sensor_data['data']
    dkeys = sensor_data['data_keys']
    units = sensor_data['units']
    
    if len(data) == 2:
        set1 = data[0]
        set2 = data[1]
        
        corr = stats.pearsonr(set1, set2)[0]
        
        title = sensor[0]['sensorname'] + ': ' + sensor[0]['timestamp'].strftime('%m-%d-%Y') + '\n' + dkeys[0] + ' v.s ' + dkeys[1] + '\n Correlation: ' + '%.3f' % corr
        y1lab = dkeys[0] + ' (' + units[1] + ')'
        y2lab = dkeys[1] + ' (' + units[0] + ')'
               
        fig = plt.figure() 
        ax1 = plt.subplot()
        ax1.plot(set2, set1, 'o', label=y1lab)
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.95, 1))
        #ax1.gcf().autofmt_xdate()
        ax1.set_xlabel(y2lab)
        ax1.set_ylabel(y1lab)
        ax1.set_title(title)
        plt.show()
    else:
        print "Sensor must have 2 sets of data"
