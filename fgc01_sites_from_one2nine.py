""" Hi
Created By: Nick Middleton
Created For: Department of Primary Industries and Regional Development, Western Australia
Date: April 2019
Purpose: This script reads a set of sample site IDs and their associated coordinates in longitude and latitude
         and transforms the coordinates to Australian Albers metres.  The script writes the results to a new text
         file using the in the structure of id, x, y .  The process is replicated anoth eight times for each input 
         point creating neighbouring points offset by a user nominated "cell size", creating points by that offset
         in the eight cardinal directions.  For the additional points the id is tagged with a suffix with structure
         "--ne" where "ne" indicates the newly created point is to the north east of the original point.
        
        The script is designed to help users who want to extract data from raster data sets of the same "cell size".
        
        This script will not work through ArcGIS so run in QGIS or other Python install with osgeo Package installed.
        
NOTE:
This script expects an input comma seperated text file with the structure id, longituted, latitude and a
Datum of WGS 84 for the coordinates.
              
This script is in development and care should be taken when using.
              
No guarentees are given and users should do their own validation.
"""
#Import necessary packages
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

##################################################################################################################
#USER DEFINED VARIABLES

#Text file takes the structure id,x,y with x and y in decimal degrees 
path_in = r"C:\Projects\Remote_Sensing_Resource_Condition\Field_Validation_2020\Data from JRSRP\fgc_sites.csv"
#Output text file (CSV) which is created by this script
path_out = r"C:\Projects\Remote_Sensing_Resource_Condition\Field_Validation_2020\Data from JRSRP\fgc_sites_one2nine.csv"
#Set the "cell size" which the points will try to mirror.
## Data Cube Landsat = 25
## AusCover Landsat = 30
## MODIS = 500
## Sentinel 2 = 10
cw = 25 # width of a cell.
##################################################################################################################

#Open the input fiel for reading and ouput file for writting.
fin = open(path_in, "r")
fout = open(path_out, "w")

#Read all the lines of the input file into a single object "lines"
lines = fin.readlines()
#Set a counter to help identify if the line is the first of the input file
counter = 0
for line in lines:
    #If first line of the intput file write out the following header
    if counter == 0:
        fout.write("id, x, y,\n")
        counter = counter + 1
    #For all other lines calculate new coordinates and write out id, x, y
    else:
        #Split input line into componenet variables
        in_vars = line.split(",")
        ident = in_vars[0]
        longitude = float(in_vars[1])
        latitude = float(in_vars[2])
        
        #Set input and output spatial references to allow osr and ogr to perfrom transformation.
        source = osr.SpatialReference()
        source.ImportFromEPSG(4326)
        target = osr.SpatialReference()
        target.ImportFromEPSG(3577)
        #Transfrom the coordinates from longitude and latitude to x and y in Australain Albers metres
        transform = osr.CoordinateTransformation(source, target)
        point = ogr.CreateGeometryFromWkt("POINT ({} {})".format(longitude, latitude))
        point.Transform(transform)
        x = point.GetX()
        y = point.GetY()
        #Write the ids and coordinates out to the text file.
        fout.write("{}, {}, {}\n".format(str(ident), x, y))
        fout.write("{}, {}, {}\n".format(ident + '--w', x-cw, y))
        fout.write("{}, {}, {}\n".format(ident + '--e', x+cw, y))
        fout.write("{}, {}, {}\n".format(ident + '--s', x, y-cw))
        fout.write("{}, {}, {}\n".format(ident + '--n', x, y+cw))
        fout.write("{}, {}, {}\n".format(ident + '--ne', x+cw, y+cw))
        fout.write("{}, {}, {}\n".format(ident + '--nw', x-cw, y+cw))
        fout.write("{}, {}, {}\n".format(ident + '--sw', x-cw, y-cw))
        fout.write("{}, {}, {}\n".format(ident + '--se', x+cw, y-cw))
#CLose the input and output files.
fout.close()
fin.close()
print("Process finished.")
