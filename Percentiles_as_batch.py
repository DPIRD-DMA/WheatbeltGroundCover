# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:55:13 2021

@author: jlaycock
"""
import os
import numpy as np
import gdal
from osgeo import gdal_array
import csv
#import rioxarray as rxr

directory = r'C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\TVC_satellite\SW_TVC\Masked_Clipped'
# mask = r'C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\out\Percentile\arable'
# dirsave = r'C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\out\Percentile'

print(os.listdir(directory))

with open('mean5_95.csv', 'w', newline='') as csvfile:
    for filename in os.listdir(directory):
        if filename.endswith(".tif"):
            rasterfile = os.path.join(directory, filename)
            print('\nFull File Name & Path =  ' + rasterfile)
            
            rasterArray = gdal_array.LoadFile(rasterfile) #Read raster as numpy array
    
            ras = gdal.Open(rasterfile) # opening the raster file with its metadata
            NoData = ras.GetRasterBand(1).GetNoDataValue() # reading the nodata value of the raster
            print('nodata value is: '+str(NoData)) # printing the nodata value
            
            rasterArray[rasterArray==NoData] = np.nan # changing all nodata pixels values to nan
            
            # print('mean = {}'.format(np.nanmean(rasterArray)))
            # print('median = {}'.format(np.nanmedian(rasterArray)))
            # print('max = {}'.format(np.nanmax(rasterArray)))
            # print('min = {}'.format(np.nanmin(rasterArray)))
            # print('count = {}'.format(np.count_nonzero(np.isnan(rasterArray))))
            # print('SDDev = {}'.format(np.nanstd(rasterArray)))
        

            fieldnames = ['FileN','Stats', 'value' ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
            writer.writeheader()
            # writer.writerow({'FileN': rasterfile, 'Stats': 'mean', 'value': np.nanmean(rasterArray)})
            # writer.writerow({'FileN': rasterfile, 'Stats': 'max', 'value': np.nanmax(rasterArray)})
            # writer.writerow({'FileN': rasterfile, 'Stats': 'min', 'value': np.nanmin(rasterArray)})
            # writer.writerow({'FileN': rasterfile, 'Stats': 'STdev', 'value': np.nanstd(rasterArray)})
            
            # writer.writerow({'FileN': rasterfile, 'Stats': '10pc', 'value': np.nanpercentile(rasterArray,10)})
            # writer.writerow({'FileN': rasterfile, 'Stats': '25pc', 'value': np.nanpercentile(rasterArray,25)})
            # writer.writerow({'FileN': rasterfile, 'Stats': '50pc', 'value': np.nanpercentile(rasterArray,50)})
            # writer.writerow({'FileN': rasterfile, 'Stats': '75pc', 'value': np.nanpercentile(rasterArray,75)})
            # writer.writerow({'FileN': rasterfile, 'Stats': '90pc', 'value': np.nanpercentile(rasterArray,90)})
            ##### calculating the 5th and 95th percentiles
            writer.writerow({'FileN': rasterfile, 'Stats': '5pc', 'value': np.nanpercentile(rasterArray,5)})
            writer.writerow({'FileN': rasterfile, 'Stats': '95pc', 'value': np.nanpercentile(rasterArray,95)})
            
            print('.._..')
    print('__Complete__')    