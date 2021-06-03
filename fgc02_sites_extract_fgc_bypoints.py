"""
Created By: Nick Middleton
Created For: Department of Primary Industries and Regional Development, Wester Australia
Creation Date: 7th of May 2019
Purpose:
       To extract Fractional Ground Cover (FGC) triplets of Photosynthetic Vegetation (PV), 
       Non-Photosynthetic Vegetation (NPV) and Bare Soil (BS) and Pixel Quality information for user supplied points.
       Points should be supplied in a CSV text file with structure:
       id, x, y
       Where x and y are in crs=3577 (Australian Albers) eastings and northings.

       The out put of the script is CSV text file with the structure:
       time,id,sensor,BS,PV,NPV,UE,pixelquality
NOTE:
This script is in development and care should be taken when using.

No guarentees are given and users should do their own validation.

This script is for use under the NCI Virtual Desktop Environment (VDI)

Ensure that the terminal that this script is run from has the following entered prior to running:
$module use /g/data/v10/public/modules/modulefiles
$module load dea

The"$" simply indicates the command is to entered in the terminal.

"""
#
#
#Import necessary packages and modules
import datacube
import pandas

#Connect to the Data Cube
dc = datacube.Datacube(app='test_fgc')

##################################################################################################################
#USER DEFINED VARIABLES

#Start date for extraction
date_start = '2019-01-01'
#End date for extraction
date_end = '2019-05-31'
#Input CSV file with id,x,y data structure
path_in = "/home/570/nm3598/dea_njm/fgc_sites_one2nine.csv"
#Ouput csv file
path_out = "/home/570/nm3598/dea_njm/fgc_sites_one2nine_deaextract.csv"
##################################################################################################################

#Open files and set counters
fin = open(path_in, "r")
lines = fin.readlines()
fout = open(path_out, "w")
linecount = 0
outcount = 0

#Iterate through input csv file
for line in lines:
    #Don't read header row
    if linecount == 0:
        linecount = linecount + 1
    #Avoid rows of the iput csv with no data.
    elif line == '\n':
        print ("Reached end of file")
    #Process a real record from input csv
    else:
        #Split line of the input csv by ',' to access values
        lstVars = line.split(',')
        #Get value for id
        ident = lstVars[0]
        #Get value for x coordinate in crs=3577
        x3577 = float(lstVars[1])
        #Get value for y coordinate in crs=3577
        y3577 = float(lstVars[2])
        
        #Access Fractional Cover for Landsat 8
        ds_fgc8 = dc.load(product='ls8_fc_albers',
        					x=(x3577), 
        					y=(y3577),
        					crs='epsg:3577',
        					time=(date_start, date_end), 
        					measurements = ['BS', 'PV', 'NPV', 'UE'],
        					resolution = (-25,25))
        #Test if there are any scenes for Landsat 8
        if len(ds_fgc8) > 0:
            #If there are scenes the access Pixel Quality for those Landsat 8 scenes
            dffgc8 = ds_fgc8.to_dataframe()
            del ds_fgc8
            ds_pq8 = dc.load(product='ls8_pq_albers',
            					x=(x3577), 
            					y=(y3577),
            					crs='epsg:3577',
            					time=(date_start, date_end), 
            					resolution = (-25,25))
            dfpq8 = ds_pq8.to_dataframe()
            #Merge data frames for Fractional Cover and Pixel Quality for Landsat 8
            dfinner8 = pandas.merge(dffgc8, dfpq8, on='time', how='inner')
            del dffgc8, dfpq8
            dfinner8.insert(0, 'sensor', 'ls8')
            dfinner8.insert(0, 'id', ident)
            #Append dataframe to output csv
            if outcount == 0:
                dfinner8.to_csv(fout, header=True)
                outcount = outcount + 1
                del dfinner8
            else:
                dfinner8.to_csv(fout, header=False)
                del dfinner8
        else:
            del ds_fgc8
                
        
        #Access Fractional Cover for Landsat 7
        ds_fgc7 = dc.load(product='ls7_fc_albers',
        					x=(x3577), 
        					y=(y3577),
        					crs='epsg:3577',
        					time=(date_start, date_end), 
        					measurements = ['BS', 'PV', 'NPV', 'UE'],
        					resolution = (-25,25))
        #Test if there are any scenes for Landsat 7
        if len(ds_fgc7) > 0:
            #If there are scenes the access Pixel Quality for those Landsat 7 scenes
            dffgc7 = ds_fgc7.to_dataframe()
            del ds_fgc7
            ds_pq7 = dc.load(product='ls7_pq_albers',
            					x=(x3577), 
            					y=(y3577),
            					crs='epsg:3577',
            					time=(date_start, date_end), 
            					resolution = (-25,25))
            dfpq7 = ds_pq7.to_dataframe()
            del ds_pq7
            #Merge data frames for Fractional Cover and Pixel Quality for Landsat 7
            dfinner7 = pandas.merge(dffgc7, dfpq7, on='time', how='inner')
            del dffgc7, dfpq7
            dfinner7.insert(0, 'sensor', 'ls7')
            dfinner7.insert(0, 'id', ident)
            #Append dataframe to output csv
            if outcount == 0:
                dfinner7.to_csv(fout, header=True)
                outcount = outcount + 1
                del dfinner7
            else:
                dfinner7.to_csv(fout, header=False)
                del dfinner7
        else:
            del ds_fgc7
        

        #Access Fractional Cover for Landsat 5
        ds_fgc5 = dc.load(product='ls5_fc_albers',
        					x=(x3577), 
        					y=(y3577),
        					crs='epsg:3577',
        					time=(date_start, date_end), 
        					measurements = ['BS', 'PV', 'NPV', 'UE'],
        					resolution = (-25,25))
        #Test if there are any scenes for Landsat 5
        if len(ds_fgc5) > 0:
            #If there are scenes the access Pixel Quality for those Landsat 5 scenes
            dffgc5 = ds_fgc5.to_dataframe()
            ds_pq5 = dc.load(product='ls5_pq_albers',
            					x=(x3577), 
            					y=(y3577),
            					crs='epsg:3577',
            					time=(date_start, date_end), 
            					resolution = (-25,25))
            dfpq5 = ds_pq5.to_dataframe()
            del ds_pq5
            #Merge data frames for Fractional Cover and Pixel Quality for Landsat 5
            dfinner5 = pandas.merge(dffgc5, dfpq5, on='time', how='inner')
            del dffgc5, dfpq5
            dfinner5.insert(0, 'sensor', 'ls5')
            dfinner5.insert(0, 'id', ident)
            #Append dataframe to output csv
            if outcount == 0:
                dfinner5.to_csv(fout, header=True)
                outcount = outcount + 1
                del dfinner5
            else:
                dfinner5.to_csv(fout, header=False)
                del dfinner5
        else:
            del ds_fgc5
del line, lines, x3577, y3577, path_out, path_in, outcount, lstVars, linecount, ident, date_end, date_start

fout.close()
print("Output complete")
fin.close()
del dc
