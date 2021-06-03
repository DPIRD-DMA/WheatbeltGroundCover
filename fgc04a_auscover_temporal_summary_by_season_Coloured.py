"""
Created By: Nick Middleton
Created For: Department of Primary Industries and Regional Development, Western Australia
Date: Ocotber 2019
Purpose: This script analyses seasonal Total Vegetation Cover (TVC) percentage rasters over a user nominated period of time, either
         1.) FOR A SINGLE SEASON OVER A NUMBER OF YEARS
         The result are set of rasters that indicate how many times a pixel has a valid pixel value during that period, how
         many of those valid pixels were below a user nominated threshold and, what this ratio is and opitionally what the median
         TVC is across that period and how anomalous the final raster in the dates range is from the median.
         
Inputs:  Start Year for the analysis (yearStart)
         End year for the analysis (yearEnd)
         Pathway to a folder containing TVC GeoTIFFs (pathIn)
         Pathway to a folder where all outputs will be written (pathOut)
         Pathway to data set to act as a mask for the Analysis (pathMask) OPTIONAL
         A single season whcihc will be analysed for the years between the start and end years
         OR
         Start and and End season that will seee the analysis done for all seasons between the start and end years.
         A integer percentage threshold cover value
NOTE:
For more infromation regarding the AusCover data see:
http://data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Seasonal+Fractional+Cover

This script uses the arcpy package from ESRI and requires the Spatial Analyst extension.
              
This script is in development and care should be taken when using.
              
No guarentees are given and users should do their own validation.
"""
# Import packages
import arcpy
import os
#Note that existing files will be overwritten if they exist
arcpy.env.overwriteOutput = True

#USER DEFINED VARIABLES
##################################################################################################################################################
#Start year for analysis
yearStart = 2009
#End year for analysis
yearEnd = 2018
#JL2020 add the anomaly as it compares the current with history
anomalyImage = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\TVC_satellite\SW_TVC\acfgcs_201903201905_TVCpc.tif"
#Folder containing input Total Vegetation Cover GeoTIFFs   **NOTE it is looking for *TVCpc.tif
pathIn = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\TVC_satellite\SW_TVC"
#Folder in which analysis GeoTIFFs will be created
pathOut = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\out\04TemporalSummary_Autumn2019"
#A mask to constrain the analysis by.
pathMask = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\masks\arable_albers_JL.tif"#r" #or does this need to be a shp file? - seems to be ok
seasonSingle = "Autumn" #"Autumn", "Spring", "Winter", "Summer"
#User defined Total Vegetative Cover threshold percentage
intThreshold = 50
#Do you want to asess the final Raster agaist the median for the list?
assess = True    #True
###################################################################################################################################################
if not os.path.exists(pathIn):
    raise Exception("Path to directory {} containing Total Vegetation Cover GeoTIFFs does not exist.  Please correct the path".format(pathIn))
if not os.path.exists(pathOut):
    raise Exception("Path to output directory {} does not exist.  Please correct the path".format(pathOut))

#SPATIAL ANALYSIS VARIABLES
arcpy.CheckOutExtension("Spatial")
#Default compression for GeoTIFFs
arcpy.env.compression = "LZ77"
#Ensure that NoData values set to 255 in outputs
arcpy.env.nodata = "MAXIMUM"
#Set workspace to the path to generate list of GeoTIFFs to be processed
arcpy.env.workspace = pathIn

#Dictionary of Seasons and their start months. e.g. 03 = March
dicSeason = dict([("Summer", "12"), ("Autumn", "03"), ("Winter", "06"), ("Spring", "09")])

#If there is a mask set by the user then set environment for that mask and its extent. 
if len(pathMask) > 0:
    if arcpy.Exists(pathMask):
        arcpy.env.mask = pathMask
        arcpy.env.extent = pathMask
    else:
        arcpy.CheckInExtension("Spatial")
        raise Exception("The nominated mask data set: ", pathMask, "doesn't eixist.  please correct the path to the mask and try again.")
        
#Create a list of all Total Vegetative Cover percentage GeoTIFFs in the workspace   NOTE it is looking for *TVCpc.tif
lsAllTVC = arcpy.ListDatasets("*TVCpc.tif")
if len(lsAllTVC) == 0:
    arcpy.CheckInExtension("Spatial")
    raise Exception("No Total Vegetation Cover GeoTIFFs exist in the directory {}".format(pathIn))

#Create an empty list to which GeoTIFFs of interest will be added (in the year range and from the correct season)
lsRas = []

strYesMonth = dicSeason[seasonSingle]
for i in range(yearStart,yearEnd + 1):
    for a in lsAllTVC:
        if str(i) == a[7:11] and a[11:13] == strYesMonth:
            print("Adding the data set", a, "to the analysis")
            lsRas.append(a)
            
#Delete the list of all TVC GeoTIFFs
del lsAllTVC

lenLsRas = len(lsRas)
if lenLsRas == 0:
    arcpy.CheckInExtension("Spatial")
    raise Exception("No Total Vegetation Cover GeoTIFFs exist for that year date or for the season {}".format(seasonSingle))          

strSuffix = seasonSingle + str(yearStart) + "_to_" + str(yearEnd) + ".tif"



#If the user wantes to assess the final raster/season agianst the range of seasons and years do the following.
#If the user wantes to assess the final raster/season gaiants the range of seasons and years do the following.
if lenLsRas >= 3:
    print("More than 3 Total Vegetation Cover GeoTIFFs in the selection.  Calculating a MEDIAN and ANOMOLY rasters.")
    #Create a pixel by pixel median
    rasMedian = arcpy.sa.CellStatistics(lsRas, statistics_type="MEDIAN", ignore_nodata="DATA")
    
##  Colour The Median
    pathTVCmedianCol = r"C:\Projects\Remote_Sensing_Resource_Condition\fgc\layer_files\clr_TVC_median.clr"
    arcpy.AddColormap_management(rasMedian, "#" , pathTVCmedianCol)

    
    
    
    #Create a raster of the last raster in the list which should be final one by date
    pathMedian = os.path.join(pathOut, "median_" + strSuffix)
    arcpy.CopyRaster_management(rasMedian, pathMedian, pixel_type="16_BIT_SIGNED", scale_pixel_value="NONE")
    print("Saved the median data set to:", pathMedian)
## JL2021
    pathMedian8Bit = os.path.join(pathOut, "median8Bit_" + strSuffix)
    arcpy.CopyRaster_management(rasMedian, pathMedian8Bit, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
    print("Saved the 8Bit median data set to:", pathMedian8Bit)
    
    #JL2020 reference to new anomaly image
    rasFinal = arcpy.sa.Int(anomalyImage)
    #Original   rasFinal = arcpy.sa.Raster(str(lsRas[-1]))
    #Calculate the Anomaly as the percentage of the final minus the median over the median.
    rasAnomaly = arcpy.sa.Int(arcpy.sa.Float(rasFinal - rasMedian))
    print("A0")
    rasAnomaly8Bit = arcpy.sa.Int(arcpy.sa.Float(rasFinal - rasMedian + 100))
    ##  Colour The 8Bit Anomaly
    pathAnomalyCol = r"C:\Projects\Remote_Sensing_Resource_Condition\fgc\layer_files\clr_Anomaly.clr"
    arcpy.AddColormap_management(rasAnomaly8Bit, "#" , pathAnomalyCol)
    ###############Colour the Anomaly###############
    
    
    #Original incorrect calculation   rasAnomaly = arcpy.sa.Int((arcpy.sa.Float(rasFinal - rasMedian) / arcpy.sa.Float(rasMedian)) * 100)
    
    #Delete the in memory median and Final
    del rasMedian
    del rasFinal
    #Decide how to name the Anomaly whether it is by season or linear date 
    pathAnomaly = os.path.join(pathOut, "anomaly_" + str(yearEnd + 1) +  strSuffix )
    #Save the result to an 
    arcpy.CopyRaster_management(rasAnomaly, pathAnomaly, pixel_type="16_BIT_SIGNED", scale_pixel_value="NONE")
    print("Saved the anomaly data set to:", pathAnomaly)
## JL2021    
    pathAnomaly8Bit = os.path.join(pathOut, "Anomaly8Bit_" + str(yearEnd + 1) +  strSuffix )
    print("A1")
    arcpy.CopyRaster_management(rasAnomaly8Bit, pathAnomaly8Bit, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
    print("Saved the 8bit anomaly data set to:", pathAnomaly8Bit)
    
    #Delete the in memory Anomaly raster
    del rasAnomaly
    del rasAnomaly8Bit
print("made anomaly and median TIF files")


#Process to create number of valid years, Number of Bad years and Bad year ratio.
#This process had to be modified to make batches of sites as it failed on JL machine.

#Set the workspace to the output folder
arcpy.env.workspace = pathOut
#Intiate a counter that assesses if the image being processed is the first.  If so it becomes the output raster
#If not then the current raster is added to the existing raster
count = 0
loop_counter = 0
valid_temp_saves = 0
temp_valid_list = []
temp_bad_list = []
#Iterate through the images of interest
total_imgs = len(lsRas)
true_count = 0
for img in lsRas:
    true_count+=1
    #Create a raster object for the current GeoTIFF
    rasCurrent = arcpy.sa.Raster(os.path.join(pathIn,img))
    #Set the cellsize to match the current raster
    arcpy.env.cellSize = rasCurrent
    #Snap cells to match the current raster
    arcpy.env.snapRaster = rasCurrent
    
    #Do a binary reclassification of the current raster to identify NULL and Valid pixels
    rasReclass = arcpy.sa.Con(arcpy.sa.IsNull(rasCurrent), 0 , 1)
    #Do a binary reclassification of the current raster to identify pixels above (0) and below (1) the user nominated threshold percentage
    rasCountBad = arcpy.sa.Con(arcpy.sa.IsNull(rasCurrent), 0, arcpy.sa.Con(rasCurrent <= intThreshold, 1, 0))
    #User the initiated counter and if it the first iteration create the output raster based on the first input raster
    print(img)
 

    if count == 0:
        rasOutValid = rasReclass
        rasOutBad  = rasCountBad
        count = count + 1
    #If it is not the first then add the current rasters to the final rasters.  Accumulating process.
    else:
        rasOutValid += rasReclass
        rasOutBad += rasCountBad
    #Delete the current rasters based n the input GeoTIFFs
    del rasReclass
    del rasCurrent
    loop_counter = loop_counter + 1
    print("finished lsrast loop",loop_counter) 

##########  alter number to suit analysis  loop counter #########    
# Change the loop counter to a max of 9 (on JL computer) to process all imagery in batches.    
    if loop_counter == 6 or true_count == total_imgs:
        
        valid_temp_saves += 1
        tempValidname = 'tempValid'+str(valid_temp_saves)+'.tif'
        tempValidDir = os.path.join(pathOut, tempValidname)
        print(tempValidDir)
        
        tempBadname = 'tempBad'+str(valid_temp_saves)+'.tif'
        tempBadDir = os.path.join(pathOut, tempBadname)
        print(tempBadDir)
        
        temp_valid_list.append(tempValidDir)
        
        temp_bad_list.append(tempBadDir)

        arcpy.CopyRaster_management(rasOutValid, tempValidDir, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
        
        arcpy.CopyRaster_management(rasOutBad, tempBadDir, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")


        loop_counter = 0
        count = 0

del rasOutValid
print(len(temp_valid_list),'file to combine')
first = True
for val in temp_valid_list:
    rasCurrent = arcpy.sa.Raster(val)
    arcpy.env.cellSize = rasCurrent
    arcpy.env.snapRaster = rasCurrent
    if first:
        rasOutValid = rasCurrent
        first = False
    else:
        rasOutValid += rasCurrent
   
    
    
print("finished entire lsrast loop")

#Delete the list of rasters which were processed
del lsRas
print("Deleted lsras")
#Set the workspace to the user identified folder where output rasters will be written
arcpy.env.workspace = pathOut
print("Env workspace is pathout")
#Create an output pathway for the count of valid pixels
pathValid = "validpixelcount_" + strSuffix
print("pathvalid - next line is path valid text")
print(pathValid)


### Colour Vaid Pixel Image
pathValPixCol = r"C:\Projects\Remote_Sensing_Resource_Condition\fgc\layer_files\clr_ValPix.clr"
arcpy.AddColormap_management(rasOutValid, "#" , pathValPixCol)



###############################################################################################################################
#Save the count of valid pixels raster out to a GeoTIFF
arcpy.CopyRaster_management(rasOutValid, pathValid, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
print("Saved the count of seasons with valid pixels data set to:", pathValid)
#Delete the in memory valid pixels raster.  This is somewhat redundant but it can help with out of memory issues
del rasOutValid
print("A-Delete Done") 
#Create an output pathway for the count of valid pixels
pathBad = "badyearcount_" + strSuffix
print("B  pathBad")


del rasOutBad
print('finished val now doing bad')
first = True
for bad in temp_bad_list:
    rasCurrent = arcpy.sa.Raster(bad)
    arcpy.env.cellSize = rasCurrent
    arcpy.env.snapRaster = rasCurrent
    if first:
       rasOutBad = rasCurrent 
       first = False
    else:   
        rasOutBad += rasCurrent
  



#Save the count of bad pixels raster out to a GeoTIFF
arcpy.CopyRaster_management(rasOutBad, pathBad, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
#print("C  copyRaster")
print("Saved the count of seasons with pixels values below the nominated threshold data set to:", pathValid)
#Delete the in memory valid pixels raster.  This is somewhat redundant but it can help with out of memory issues
del rasOutBad
print("D  DeleteOutBad")
#Re-create the rasters in memory.  Again this could be considered redundant but it can help with out of memory issues
rasBad = arcpy.sa.Raster(pathBad)
print("B0")
rasValid = arcpy.sa.Raster(pathValid)
#
#
#Calculate a ratio of the number of bad years over the number of years of valid pixels
#This ratio is in interger percentage values from 0 to 100.  Modify this block to have
#it saved a a floating point raster.

rasOutRatio = arcpy.sa.Int((arcpy.sa.Float(rasBad) / arcpy.sa.Float(rasValid)) * 100)
pathBadYrRatCLR = r"C:\Projects\Remote_Sensing_Resource_Condition\fgc\layer_files\clr_BadYrRatio.clr"
arcpy.AddColormap_management(rasOutRatio, "#" , pathBadYrRatCLR)
print("Colours added to Bad Yr Ratio")

#Create a path to save the ratio dataset out to.
pathRatio = "badyearratio_" + str(intThreshold) + "pc_" + strSuffix
#Save out the ratio raster to a ratio raster.  Remember this is an integer value
#between 0 and 100.
arcpy.CopyRaster_management(rasOutRatio, pathRatio, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
print("Saved the ratio of seasons below threshold over all seasons with valida pixels values to:", pathRatio)
#Progress print
print(pathValid, " / ", pathBad, " = ", pathRatio)
#Delete the in memory rasters
del rasOutRatio, rasBad, rasValid
print("Completed!")
#Check the Spatial Analyst Extension back in.
arcpy.CheckInExtension("Spatial")
print("Processing is complete. Median, Anomlay, valid pixel count bad year count and bad year ratio complete")