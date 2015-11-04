import urllib2 as ulib2
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib as mtplt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cmaps

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
            print "Getting data from: " + url
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

def pullTempSensor(node, strt, stp):
    urls = makeURLs(node, strt, stp)
    sensorname = 'MLX90614ESF-DAA.Melexis.008-2013'
    sensor = []
    temp = 0.0
    units = 'F'
    
    for url in urls:
        try:
            request = ulib2.Request(url)
            handle = ulib2.urlopen(request)
            lines = handle.readlines()

            for line in lines:
                contents = line.split(",")
                if sensorname == contents[0]:

                    dtdata = contents[1].split()
                    date = dtdata[0].split('/')
                    mm = int(date[0])
                    dd = int(date[1])
                    yyyy = int(date[2]) + 2000
                    time = dtdata[1].split(':')
                    h = int(time[0])
                    m = int(time[1])
                    s = int(time[2])

                    datetime = dt.datetime(yyyy, mm, dd, h, m, s)

                    for content in contents[2:]:
                        data = content.split(";")
                        temp = (float)(data[1])

                    instance = {"timestamp": datetime,
                             "sensorname": contents[0],
                             "temperature": temp,
                             "units": units,
                             }
                    sensor.append(instance)
        except:
            print "Missing data from: " + url
            
    return sensor


"""
Fetches AoT data from specified url, and extracts IR Temperature Grid
Stores each sensor measurement in Python Dictionary
Returns a list of sensor measurements
"""
def pullTempGridSensor(node, strt, stp):
    urls = makeURLs(node, strt, stp)
    sensorname = 'D6T-44L-06.Omron.2012'
    sensor = []
    
    for url in urls:
        try:
            request = ulib2.Request(url)
            handle = ulib2.urlopen(request)
            lines = handle.readlines()

            for line in lines:
                contents = line.split(",")
                if sensorname == contents[0]:
                    temps = []
                    units = []
                    pixels = []

                    dtdata = contents[1].split()
                    date = dtdata[0].split('/')
                    mm = int(date[0])
                    dd = int(date[1])
                    yyyy = int(date[2]) + 2000
                    time = dtdata[1].split(':')
                    h = int(time[0])
                    m = int(time[1])
                    s = int(time[2])

                    datetime = dt.datetime(yyyy, mm, dd, h, m, s)

                    for content in contents[2:]:
                        data = content.split(";")
                        temps.append((float)(data[1]))
                        units.append(data[2])
                        pixels.append(data[3])

                    instance = {"timestamp": datetime,
                             "sensorname": contents[0],
                             "temperature": temps,
                             "unit": units,
                             "pixels": pixels,
                             }
                    sensor.append(instance)
        except:
            print "Missing data from: " + url 
            
    return sensor

def pullHumSensor(node, strt, stp):
    urls = makeURLs(node, strt, stp)
    sensorname = 'HIH6130.Honeywell.2011'
    sensor = []
    temp = 0.0
    hum = 0.0
    tunits = 'C'
    hunits = '%RH'
    
    for url in urls:
        try:
            request = ulib2.Request(url)
            handle = ulib2.urlopen(request)
            lines = handle.readlines()

            for line in lines:
                contents = line.split(",")
                if sensorname == contents[0]:

                    dtdata = contents[1].split()
                    date = dtdata[0].split('/')
                    mm = int(date[0])
                    dd = int(date[1]) + 2000
                    yyyy = int(date[2])
                    time = dtdata[1].split(':')
                    h = int(time[0])
                    m = int(time[1])
                    s = int(time[2])

                    datetime = dt.datetime(yyyy, mm, dd, h, m, s)

                    tdata = contents[2].split(";")
                    temp = (float)(tdata[1])
                    
                    hdata = contents[3].split(";")
                    hum = (float) (hdata[1])

                    instance = {"timestamp": datetime,
                             "sensorname": contents[0],
                             "temperature": temp,
                             "humidity": hum,
                             "tempunits": tunits,
                             "humunits": hunits
                             }
                    sensor.append(instance)
        except:
            print "Missing data from: " + url
            
    return sensor

"""
---------------EXTRACTING DATA---------------
"""

def tempData(sensor):
    times = []
    temps = []
    
    for instance in sensor:
        time = mdates.date2num(instance['timestamp'])
        temp = instance['Temperature']
        
        times.append(time)
        temps.append(temp)
    
    return times, temps

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

def humidityData(sensor):
    times = []
    hums = []
    for instance in sensor:
        time = mdates.date2num(instance['timestamp'])
        hum = instance['Humidity']
        
        times.append(time)
        hums.append(hum)
        
    return times, hums

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
    for instance in sensor:
        unit = instance['units'][0]
        grid = instance['Temperature']
        avg = mean(grid)
        
        instance['Temperature'] = avg
        instance['units'] = unit
        instance['context'] = 'merged'
        

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

def temp_timeseries(times, temps):
    plt.plot_date(times, temps, fmt='r-')
    plt.gcf().autofmt_xdate()
    plt.xlabel('Time')
    plt.ylabel('Temperature (F)')
    plt.grid(True)
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

def humidity_timeseries(times, hums):
    plt.plot_date(times, hums, fmt='r-')
    plt.gcf().autofmt_xdate()
    plt.xlabel('Time')
    plt.ylabel('Humidity (%RH)')
    plt.grid(True)
    plt.show()