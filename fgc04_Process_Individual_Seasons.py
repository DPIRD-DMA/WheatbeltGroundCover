"""
Title: TVC Threshold by Zone - Individual seasonal analysis
Created By: Nick Middleton
Created For: Department of Primary Industries and Regional Development, Wester Australia
Date: November 2019
Updated 2021   (Justin Laycock)
Purpose: The primary purpose of the following procedure is to produce data to answer three questions:
         1.	How much of a landscape is above/below a given groundcover target, or between two cover intervals?
         2.	Where in the landscape do you find groundcover above/below a groundcover target, or between two cover thresholds?
         3.	What is the difference between one year/season and another or the median of a set time period?

         This script processes Pre-Processed AusCover Seasonal Fractional Groundcover datasets to create a summary of the proportion
         of land that is below/between a threshold/s of Total Vegetation Cover percentage based on the polygons in a feature class. 
         A single or range of percentage vegetation cover threshold must be specified to create threshold classes for processing. For instance,
         [50,70] will become 0-50%, 51-70% and 71-100% cover classes.
         The per cent of land in each cover class for a polygon feature is possible by specifying the pathway to the polygon layer, and the field name. 
         The product of the analysis is a table (duplicated in .dbf & .xls) which contain the unique identifier for the input polygon, 
         the area in each class range (that was not NULL), the total area assessed (that was not NULL) and the area as hectares with the threshold value as headers.
         The output raster is coloured using a .clr file that specifies the pixel value and the RGB colour  (i.e. 1 166 97 26)
 
     
Inputs:  A percentage to vegetation cover threshold ("lsTVCThreshold") OR range of thresholds
                There may be one or more thresholds and the program will create classes to be assessed based on these thresholds
                For instance if the following ise used for thresholds [40,70] then:
                The program classifies the amount the amount of land for 0 to 40 % cover, 40 to 70 % cover and 70 to 100 % cover.
         Pathway to a workspace where the outputs will be generated ("pathOut")
         A polygon data set containing the features for which summaries will be generated ("pathPoly")
         A field name within the polygon data set that contains unique identifiers for each polygon ("strFieldName")
         A raster data set containing values of percentage total vegetative ground cover ("pathTVC")
         A data set (raster or polygon) to be used as a mask for the analysis ("pathMask")
             -Note: pathTVC is used as a maks if pathMask is not specified.
         Pathway to the .clr file to colour the image

Outputs: A table (duplicated as tabulate_records.xls & tabulate_records.dbf )
              -The unique polygon identifier "VALUE"
              -The area under each class VALUE_1..VALUE_X (depending on how many classes are specified).  Area units will be in square metres.
              -The total area assessed (may not match polygon due to null values in "pathTVC") in square metres
              -The tabulated outputs includes both the area in m2 and Hectares. However, it is recommended that the per cent value is used for 
               comparison as the total area is not consistent through time.
        A log file (log.txt) which holds metadata about the analysis.

              NOTE:  The area generated will be in square meters based on the projection of the FGC data (Australian Albers).  The area represents the
                     Combination of cells/extent from both the input polygons and the seasonal FCG rasters.  Seasonal FGC rasters may not have complete
                     coverage for the SW Agricultural Zone, thus they will have a reduced area assessed.  FOR THIS REASON WHEN COMPARING DIFFERENT YEARS
                     THE PERCENTAGES BELOW AND ABOVE THE THRESHOLD SHOULD BE USED AND NOT THE AREA.
        
NOTE:
For more infromation regarding the AusCover data see:
http://data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Seasonal+Fractional+Cover

This script uses the arcpy package from ESRI and requires the Spatial Analyst extension.
              
This script is in development and care should be taken when using.
              
No guarentees are given and users should do their own validation.
"""
#Import packages
import arcpy
import os
from arcpy.sa import *
from datetime import datetime

#BE WARNED - Overwite is TRUE so it will overwrite existing data
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

#USER DEFINED VARIABLES
########################################################################################################################################################
#Threshold percentage of Total Vegetative Ground Cover
#Value between class should be defined and not the upper
#And lower limits.  I.e. [40,70] will generate statistics for
#The classes 0-40, 41-70, 71-100.
lsTVCThreshold = [10,20,30,40,50,60,70,80,90] # [10,20,30,40,50,60,70,80,90]
#Folder containing FGC Total Vegetation Cover percentage GeoTIFFs
'''#Folder where outputs will be created'''
pathOut = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\out\05Threshold_1987-2021"
#Pathway to a polygon data set containing the extents for which summary statistics will be calculated
# pathPoly = r"C:\Projects\Remote_Sensing_Resource_Condition\fgc\data\masks\SLZone_DPIRD_017_Albers_SmallClip.shp"
#pathPoly = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\masks\WA_Wheatbelt_2010_albers3577.shp"
pathPoly = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\masks\SLZone_DPIRD_017_Albers.shp"

#Name of field/column in the polygon data set.  Note this is case senstive
strFieldName  = "mu_name" #"MAPUNIT" #"DRD_REGION"  #"mu_name"

'''Pathway to Total Vegetation Cover GeoTIFF to be used in the analysis.   **Folder'''
# pathTVC = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\TVC_satellite\Dam"
pathTVC = r"E:\FGC\TVC"         #"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\TVC_satellite\TempProcessing"#  "E:\fgc\data\derived\acfgcs\landsat_seasonal\acfgcs_201906201908_TVCpc.tif"
#pathTVC = r"L:\DigitalEarthAustralia\fgc\data\TVC_satellite\TVC_miniArea"
'''A mask to constrain the analysis by.'''
pathMask = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\masks\arable_albers_JL.tif" #"C:\Projects\Remote_Sensing_Resource_Condition\!Cadaster\Dams_3577.shp"#"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\masks\arable_albers_JL.tif"
#ColourImage ** Path to the .clr file that will colour the image from brown to green
pathTVCColour = r"C:\Projects\Remote_Sensing_Resource_Condition\fgc\layer_files\TVC_10pc_10class.clr"
#########################################################################################################################################################
if not os.path.exists(pathOut):
    raise Exception("Path to the output directory {} does not exist.  Please correct the path".format(pathOut))
if not arcpy.Exists(pathPoly):
    raise Exception("Path to the polygon data set {} does not exist.  Please correct the path".format(pathPoly))
print ("Marker 1")
desc = arcpy.Describe(pathPoly)
flds = desc.fields
fldin = 'no'
for fld in flds:
    if fld.name == strFieldName:
        fldin = 'yes'
if fldin == 'no':
    raise Exception("The field {} does not exist in the polygon data set {}.  Please check the name of the field".format(strFieldName, pathOut))

if not os.path.exists(pathTVC):
    raise Exception("Path to the Total Vegetation Cover GeoTIFF data set {} does not exist.  Please correct the path".format(pathTVC))

######     JL;  I found this in NickM other codes
#Create a list of all Total Vegetative Cover percentage GeoTIFFs in the workspace   NOTE it is looking for *TVCpc.tif
arcpy.env.workspace = pathTVC
lsAllTVC = arcpy.ListDatasets("*TVCpc.tif")

if len(lsAllTVC) == 0:
    arcpy.CheckInExtension("Spatial")
    raise Exception("No Total Vegetation Cover GeoTIFFs exist in the directory {}".format(pathTVC)) #check if needs a tif file

print ("Marker 2")
print ("List of images for processing : " + str(lsAllTVC))

#If there is a mask set by the user then set environment for that mask and its extent.
      
if len(pathMask) > 0:
    if arcpy.Exists(pathMask):
        arcpy.env.mask = pathMask
        arcpy.env.extent = pathMask
    else:
        arcpy.CheckInExtension("Spatial")
        raise Exception("The nominated mask data set: ", pathMask, "doesn't exist.  please correct the path to the mask and try again.")
else:
    arcpy.env.mask = pathTVC+"/"+lsAllTVC[0]     #JL2020 The 0 was 1
logFile = os.path.join(pathOut, "log.txt")
f = open(logFile, mode='w')
f.write("Input Total Vegetation Cover GeoTIFF = " + pathTVC + "\n")
f.write("Polygon data set containing features to be assessed = " + pathPoly + "\n")
f.write("Field uniquely identifiying features = " + strFieldName + "\n")
if len(pathMask) > 0:
    f.write("Data set used as a mask = " + pathMask + "\n")
else:
    f.write("No additional mask used.")
f.write("Class breaks used in the analysis = " + str(lsTVCThreshold) + "\n")
f.write("List of images for processing : " + str(lsAllTVC) + "\n")
print ("Marker 3")
print ("Enviroment Mask : " + arcpy.env.mask)

#Set workspace to folder containing FGC TVC rasters
arcpy.env.workspace = pathOut
#Standard compression fro GeoTIFFs
arcpy.env.compression = "LZ77"
#Ensure No Data values will be set to 255 for unsigned 8 bit GeoTIFFs
arcpy.env.nodata = "MAXIMUM"
#Set raster analysis properties based on the TVC    JL2020 changed the [0] below, it was 1
arcpy.env.cellSize = pathTVC+"/"+lsAllTVC[0]
print("Environment Cell Size : "+ arcpy.env.cellSize)
arcpy.env.outputCoordinateSystem = pathTVC+"/"+lsAllTVC[0]
arcpy.env.snapRaster = pathTVC+"/"+lsAllTVC[0]
arcpy.env.extent = pathPoly

#convert the user selected polygons to raster data set"pathPolyConvert"
pathPolyConvert = "polyunits"
arcpy.PolygonToRaster_conversion(pathPoly, strFieldName, pathPolyConvert, "MAXIMUM_AREA")

  ##
  # SET UP REMAP TABLE FOR RECLASSIFYING TVC RASTER TO THRESHOLDS
  #Based on the user defined thresholds a new list of lists is created where the sub-lists have the
  #structure required by arcgis relcassification for ranges with a strucutre of [x,y,a] where:
  #x = lower limit
  #y = upper limit
  #a = output reclassified value for range
  #
#The new sub-lists will allways classify the fist range as being from 0 to the first class break that
#the user nominates.  The final sub-list will always be from the last class break the user nominates to 100.
intLen = len(lsTVCThreshold) 
#dictionary for column headers

ls2 = []
counter = 0
while counter <= intLen:
   if counter == 0:
        a = 0
        b = lsTVCThreshold[counter]
        ls2.append([a,b,counter + 1])  
   elif counter == intLen:
        a = lsTVCThreshold[counter -1]
        b = 100
        ls2.append([a,b,counter + 1])
   else:
        a = lsTVCThreshold[counter - 1]
        b = lsTVCThreshold[counter]
        ls2.append([a,b,counter + 1])
   counter += 1
print ("Cover Classes") 
print (ls2)

lim_strings = ['{}_{}'.format(bkt[0],bkt[1]) for bkt in ls2]
val_dict = {k+1:v for k,v in enumerate(lim_strings)}
#ls2 is a remap table, used for each of the rasters.  


### THIS IS WHERE TO START THE LOOP
#Looping over all tif names in lsAllTVC

for inTVC in lsAllTVC:  
    #inTVC =lsAllTVC[1]  #use this for testing on 1 raster
  rasNameTVC =pathTVC+"\\"+inTVC   #CHECK if path is present in the list of tifs
  print("Loop Process : " + rasNameTVC)
  # get prefix to use for naming output raster and table
  filePrefix = inTVC[:-9]
 
  #Consistent name to which FGC TVC data set are converted
  pathRasTVCThreshold = filePrefix+"tvcth.tif" 
  pathRasTable = "tabulate_records_"+filePrefix[:-1]+".dbf"

    ##fout = open(os.path.join(pathWKS, "TVCthreshold" + str(lsTVCThreshold) + season + str(yearStart) + "to" + str(yearEnd) + ".txt"), "w")
  ##fout.write("unit, TVCimage, date, season, perc_below{}, perc_above{}, area_assessed\n".format(lsTVCThreshold, lsTVCThreshold))        

  #Create a raster object in memory from the TVC GeoTIFF
  rasTVC = arcpy.Raster(rasNameTVC)

  ## Now reclassify using thresholds written into ls2
  rasTVCThreshold = Reclassify(rasTVC, "Value", RemapRange(ls2))
  ##
  ##  Colour The image using the colour file
  print("\n about to apply the colouring to the raster image")
  arcpy.AddColormap_management(rasTVCThreshold, "#" , pathTVCColour)
  print("colour has been applied \n")
  #Save the temporary raster to an ESRI GRID
  ##rasTVCThreshold.save(pathRasTVCThreshold)

  #save thresholds raster to disk
  arcpy.CopyRaster_management(rasTVCThreshold, pathRasTVCThreshold, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
  #tabulate area with in the polygons.  This creates the dbf file in the first place. 
  arcpy.sa.TabulateArea(pathPolyConvert, strFieldName, rasTVCThreshold, "Value", pathRasTable)

  # Add area to the tabulate-area table.  THis will be done for each threshold class in next loop
  intClasses = len(ls2)
  arcpy.AddField_management(pathRasTable, "total_area", "DOUBLE")
  arcpy.AddField_management(pathRasTable, "ImageDate", "TEXT")
  #arcpy.AddField_management(pathRasTable, "Value", "TEXT")
  #arcpy.AddField_management(pathPolyConvert, "MAPUNIT")
  f.write("Processed Image:  " + rasNameTVC + "\n")

  # This adds a column for each threshold's percent value.  So 2 thresholds gives 3 new columns.
  for i in ls2:   
    arcpy.AddField_management(pathRasTable, "a" + val_dict[i[2]] + "ha", "DOUBLE")
  cursor =  arcpy.UpdateCursor(pathRasTable)
  intTA = 0
  for row in cursor:
     for i in ls2:
        curField = 'VALUE_' + str(i[2])
        intTA += row.getValue(curField)
     row.setValue("total_area", intTA)
     for i in ls2:
        curFieldVal = 'VALUE_' + str(i[2])
        curFieldPC = "a" + val_dict[i[2]] + "ha"
        row.setValue(curFieldPC, (row.getValue(curFieldVal)) / 10000)
        row.setValue("ImageDate", filePrefix[5:-1])
     cursor.updateRow(row)
     intTA = 0
  del row
  del cursor
  
## END OF LOOP OVER TVC RASTERS


# Now read in dbfs, append, then write out as a csv file
#os.getcwd()  # get current working directory
#pathOut = r"C:\ALL_PROJECTS\KPI_FGC_landsat\Code_multiImage\05ThresholdSummary_test"
#arcpy.env.workspace = pathOut

# make a list of dbf tables (using the arcpy command avoids all the 'other' dbf files)
tableList = arcpy.ListTables('tabulate*')

#import these for data base and data frame functions
import pandas
from simpledbf import Dbf5

#cool 'pop' feature
#dbf = Dbf5(pathOut + '\\' + tableList.pop(1))

# this works for all tables with 9 columns (complete)
#check that all outputs have the 9 cols, or add an 'if' section.

#set up empty data frame, then fill with all the tables in the list, then stack up (concat)
li = []

for filename in tableList:
    dbfnext = Dbf5(pathOut + '\\' + filename)
    dfnew = dbfnext.to_dataframe()
    li.append(dfnew)
frame = pandas.concat(li, axis=0, ignore_index=True)

# write the data frame to a csv file
frame.to_csv (pathOut + '\\All_tabulate_records_acfgcs.csv', index = None, header=True) 

##

arcpy.CheckInExtension("Spatial")

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%c")
f.write("Analysis completed at: " + timestampStr + "\n")
f.write("Yes   The Analysis is now completed")
f.close

print ("done - Check log.txt file for other details")
