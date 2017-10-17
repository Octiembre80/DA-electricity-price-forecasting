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

variables = ['T_2M']
#['SWDIFDS_RAD', 'SWDIRS_RAD', 'V_10M', 'U_10M', 'TOT_PRECIP', 'T_2M']

ll_lat = 365
ur_lat = 510
ll_lon = 375
ur_lon = 485

raw_out = './raw_data/grib/'

max_values = dict([(var, 0) for var in variables])

base_path = 'ftp://ftp-cdc.dwd.de/pub/REA/COSMO_REA6/hourly/2D/'
for var in variables:
    if var == 'TOT_PRECIP':
        mrange = range(9, 13, 1)
    else:
        mrange = range(7, 13, 1)

    for month in mrange:
        
        arr = []
        
        if month >= 10:
            month_string = str(month)
        else:
            month_string = '0' + str(month)
            
        time_index = open('./processed_data/weather/{}.2D.2015{}.txt'.format(var, month_string), 'w')
        path = base_path + var + '/' + '{}.2D.2015{}.grb.bz2'.format(var, month_string)
        
        print(path)
        
        _ = wget.download(path, out=raw_out)
        
        filename = raw_out + '{}.2D.2015{}.grb.bz2'.format(var, month_string)
        
        print('download finished')
        
        zipfile = bz2.BZ2File(filename) # open the file
        data = zipfile.read() # get the decompressed data
        newfilepath = filename[:-4] # new file name
        
        with open(newfilepath, 'wb') as f:
            f.write(data)
        
        print('unzip finished')
        
        cubes = iris.load_cube(newfilepath)
        
        for i in range(cubes.shape[0]):
            print('cube {}'.format(i))
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(cubes[i].coords('time')[0].cell(0).point.round()*3600))
            data = cubes[i].data[ll_lat:ur_lat, ll_lon:ur_lon]
#             print(data)
            arr.append(data)
            time_index.write(timestamp + '\n')
            max_value = np.amax(data)
            if max_value > max_values[var]:
                max_values[var] = max_value
        
        print('data extracted')
        
        del(cubes)
    
        time_index.close()
        arr = np.array(arr)
        np.save('./processed_data/weather/{}.2D.2015{}.npy'.format(var, month_string), arr)
        
        os.remove(filename)
        os.remove(newfilepath)
        urllib.urlcleanup()
        
        
with open('./processed_data/weather/max_values.json', 'r') as f:
	json.dump(max_values, f)
#json.dump(max_values, './processed_data/weather/max_values.json')
        
# 'SWDIRS_RAD/SWDIRS_RAD.2D.201506.grb.bz2''

# ftp://ftp-cdc.dwd.de/pub/REA/COSMO_REA6/hourly/2D/SWDIRS_RAD/SWDIRS_RAD.2D.201508.grb.bz2
