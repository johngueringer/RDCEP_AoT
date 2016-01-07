#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))


SENSOR_CODES = [
    'MLX90614ESF-DAA', 'D6T-44L-06', 'TMP421', 'BMP180', 'PDV_P8104',
    'Thermistor_NTC_PR103J2', 'HIH6130', 'SHT15', 'DS18B20', 'RHT03',
    'SHT75', 'HIH4030', 'GA1A1S201WP', 'MAX4466', 'HTU21D']

GRID_SENSOR = 'D6T-44L-06.Omron.2012'

DATA_URI = "http://outworld.mcs.anl.gov/waggle-data/{}/data/data_{}-{}-{}-{}.txt"