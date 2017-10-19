"""This script downloads and processes weather data from the ftp server of the German national weather service.
Total runtime will be approximately 36 hours. Final data will be saved in numpy binary files. Total size of the 
final data will be around 10 GB. Only data for 2015 is downloaded."""

import iris
import datetime as dt
import time
import numpy as np
import bz2
import json
import wget
import os
import bz2
import urllib

# define variables
variables = ['SWDIFDS_RAD', 'SWDIRS_RAD', 'V_10M', 'U_10M', 'TOT_PRECIP', 'T_2M']

# define lat-lon grid to keep (these particular coordinates are chosen to span Germany)
ll_lat = 365
ur_lat = 510
ll_lon = 375
ur_lon = 485

# download directory
raw_out = './raw_data/grib/'

# path to ftp server
base_path = 'ftp://ftp-cdc.dwd.de/pub/REA/COSMO_REA6/hourly/2D/'

# range of month to download
mrange = range(1, 13, 1)

# iterate over variables and months 
for var in variables:
    for month in mrange:
        
        arr = []
        
        # format string representation of month
        if month >= 10:
            month_string = str(month)
        else:
            month_string = '0' + str(month)
        
        # create a file to write timeseries index of downloaded data to
        time_index = open('./processed_data/weather/{}.2D.2015{}.txt'.format(var, month_string), 'w')
       
        path = base_path + var + '/' + '{}.2D.2015{}.grb.bz2'.format(var, month_string)
        
        print(path)
        
        # download data file
        _ = wget.download(path, out=raw_out)
        
        filename = raw_out + '{}.2D.2015{}.grb.bz2'.format(var, month_string)
        
        print('download finished')
        
        # open, decompress, save decompressed
        zipfile = bz2.BZ2File(filename) 
        data = zipfile.read()
        newfilepath = filename[:-4]
        
        with open(newfilepath, 'wb') as f:
            f.write(data)
        
        print('unzip finished')
        
        # load decompressed data into iris.cubes object for manipulation
        
        # erroneous data for this var-month combination, contains multiple cubes
        # keep last cube (assumption: last cube == best data)
        if var == 'TOT_PRECIP' and month == 8:
            cubes = iris.load(newfilepath)[1]
        else:
            cubes = iris.load_cube(newfilepath)
        
        # extract data from cubes by iterating over data-structure
        for i in range(cubes.shape[0]):
            
            # one entry represents one hour of the respective month
            print('cube {}'.format(i))
            
            # get timestamp in gmt format
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(cubes[i].coords('time')[0].cell(0).point.round()*3600))
            
            # extract weather data for the predefined grid as numpy array
            data = cubes[i].data[ll_lat:ur_lat, ll_lon:ur_lon]

            arr.append(data)
            time_index.write(timestamp + '\n')


        print('data extracted')
        del(cubes)
    
        # save data to npy file
        time_index.close()
        arr = np.array(arr)
        np.save('./processed_data/weather/{}.2D.2015{}.npy'.format(var, month_string), arr)
        
        # clean up
        os.remove(filename)
        os.remove(newfilepath)
        urllib.urlcleanup()
