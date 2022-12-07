"""
Created By: Nick Middleton
Created For: Department of Primary Industries and Regional Development, Western Australia
Date: April 2019
Updated 2021 (Justin Laycock)

Purpose: This script processes AusCover Landsat Seasonal Fractional Ground cover datasets to create four derived
         raster data sets:
                           Bare Soil percentage (BSpc)
                           Photosynthetic Vegetation Cover percentage (PVpc)
                           Non-Photosynthetic Vegetation Cover percentage (NPVpc)
                           Total Vegetative Cover percentage (TVCpc)
                           Unexplained Error (UE)
        All values in the output images are between 0 and 100, which differs from the original AusCover where values
        can be less than 0 and greater than 100 for the vegation cover and bare soil data.  Original Auscover data also has 100 added to each band which
        has been subtracted as part of this process.  The final Total Vegetative Percentage cover data has also been truncated at a maximum value of 100.

The user must specify the following input variables:
         Folder pathway to the imagery to be processed (pathIn)
	Folder pathway to the save outputs (pathOut)
	Pathway and file name of a raster mask (pathMask)
	The nominated start year (yearStart)
	The nominated last year (yearend) 

        
NOTE:
For more infromation regarding the AusCover data see:
http://data.auscover.org.au/xwiki/bin/view/Product+pages/Landsat+Seasonal+Fractional+Cover

This script uses the arcpy package from ESRI and requires the Spatial Analyst extension.
              
This script is in development and care should be taken when using.
              
No guarentees are given and users should do their own validation.
"""

#Import necessary packages
import arcpy
import os



##################################################################################################################
#USER DEFINED VARIABLES

#User nominated path to directory containing AusCover data to process
pathIn = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\raw_satellite_fgc\New_Download4_processing"
####pathIn = r"C:\Projects\Remote_Sensing_Resource_Condition\Field_Validation_2021\process"
#User nominated path to a directory where output datasets will be written.
pathOut = r"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\TVC_satellite\TempProcessing"
####pathOut = r"C:\Projects\Remote_Sensing_Resource_Condition\Field_Validation_2021\process"
#User nominated path to raster data set to act as a mask and extent for the out data sets
#Note that original cell size and positioning is maintained.
pathMask = r"" #"C:\Projects\Remote_Sensing_Resource_Condition\FGC\data\masks\SW_Albers.shp" #"C:\Projects\Remote_Sensing_Resource_Condition\fgc\data\masks\raster2019\Arable_AgProp_albers3577_Shp\WA_ArableAreas_Private_Wheatbelt2010.shp"

#User nominated start and end year for images to process
yearStart = 2000
yearEnd = 2022
####################################################################################################################
if not os.path.exists(pathIn):
    raise Exception("Path to directory {} containing raw AusCover Seasonal Fractional Ground cover datasets does not exist.  Please correct the path".format(pathIn))
if not os.path.exists(pathOut):
    raise Exception("Path to output directory {} does not exist.  Please correct the path".format(pathOut))
arcpy.CheckOutExtension("Spatial")


#ANALYSIS ENVIRONMENT
#Will overwrite existing outputs
arcpy.env.overwriteOutput = True
#Set compression for GeoTIFF output
arcpy.env.compression = "LZ77"
#Ensure that NoData values set to 255 in outputs
arcpy.env.nodata = "MAXIMUM"
#Set the workspace to the folder containing the input FGC seasonal GeoTIFFs from AusCover
arcpy.env.workspace = pathIn

#If there is a mask set by the user then set environemnt for that mask and its extent. 
if len(pathMask) > 0:
    if arcpy.Exists(pathMask):
        arcpy.env.mask = pathMask
        arcpy.env.extent = pathMask
    else:
        arcpy.CheckInExtension("Spatial")
        raise Exception("The nominated mask data set: ", pathMask, "doesn't eixist.  please correct the path to the mask and try again.")

#Create and empty list for input raster data sets to tbe processed.
lsRas = []
#Create a list of all AusCOver Seasonal Fractional Ground Cover data set in the input directory. 
lsCurRaster = arcpy.ListDatasets("lztmre_wa_" + "*" + "dima2.tif")
if len(lsCurRaster) == 0:
    arcpy.CheckInExtension("Spatial")
    raise Exception("No raw AusCover Seasonal Fractional Ground Cover datasets exist int the directory {}".format(pathIn))

#Filter the input list by the years of interest.
for i in range(yearStart,yearEnd + 1):
    for a in lsCurRaster:
        if str(i) == a[11:15]:
            print("Adding the data set", a, "to the analysis")
            lsRas.append(a)
del lsCurRaster
if len(lsRas) == 0:
    arcpy.CheckInExtension("Spatial")
    raise Exception("No raw AusCover Seasonal Fractional Ground Cover datasets exist between {} and {} in the directory {}".format(yearStart, yearEnd, pathIn))
#Set the workspace to the user nominated folder.
arcpy.env.workspace = pathOut

#Iterate through the list of input GeoTIFFs, taking each band and processing it to -100 from the values and
#truncate the minimum values to 0 and the maximum values to 100 for the BS, NPV and PV
#For the input GeoTIFFs the bands store thr following information:
#Band 1 = Bare Soil (BS)
#Band 2 = Photosynthetic Vegetation (PV)
#Band 3 = Non-Photosynthetic Vegetation (NPV)
#Band 4 = unexplainde error (UE)

#The process also sums the truncated PV and NPV values to create a Total Vegetative Cover (TVC)data set.
#Note that there is potential for the TVC dataset to exceed 100 but it has been trimmed to 100.

for img in lsRas:
    print(str(img))
    strDate = str(img)[11:23]
#    rasBS = arcpy.sa.Raster(os.path.join(pathIn,img,"Band_1"))
#    arcpy.env.cellSize = rasBS
#    arcpy.env.snapRaster = rasBS
#    pathOutBS = os.path.join(pathOut, "acfgcs_"+ strDate + "_BSpc.tif")
#    rasTempBS = rasBS - 100
#    #Trim BS to minimum of 0 and maximum of 100
#    rasOutBS = arcpy.sa.Con(rasTempBS < 0, 0, arcpy.sa.Con(rasTempBS > 100, 100, rasTempBS))
#    arcpy.CopyRaster_management(rasOutBS, pathOutBS, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
#    del rasOutBS, rasBS, rasTempBS
#    print("BS done")
    
    rasPV = arcpy.sa.Raster(os.path.join(pathIn,img,"Band_2"))
    arcpy.env.cellSize = rasPV
    arcpy.env.snapRaster = rasPV
    pathOutPV = os.path.join(pathOut, "acfgcs_"+ strDate + "_PVpc.tif")
    rasTempPV = rasPV - 100
    #Trim PV to minimum of 0 and maximum of 100
    rasOutPV = arcpy.sa.Con(rasTempPV < 0, 0, arcpy.sa.Con(rasTempPV > 100, 100, rasTempPV))
    arcpy.CopyRaster_management(rasOutPV, pathOutPV, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
    del rasTempPV, rasPV
    print("PV done")
    
    rasNPV = arcpy.sa.Raster(os.path.join(pathIn,img, "Band_3"))
    arcpy.env.cellSize = rasNPV
    arcpy.env.snapRaster = rasNPV
    pathOutNPV = os.path.join(pathOut, "acfgcs_"+ strDate + "_NPVpc.tif")
    rasTempNPV = rasNPV - 100
    #Trim NPV to minimum of 0 and maximum of 100
    rasOutNPV = arcpy.sa.Con(rasTempNPV < 0, 0, arcpy.sa.Con(rasTempNPV > 100, 100, rasTempNPV))
    arcpy.CopyRaster_management(rasOutNPV, pathOutNPV, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
    del rasNPV, rasTempNPV
    print("NPV done")
    
    rasTempTC = rasOutPV + rasOutNPV
    #Trim TVC to a maximum of 100
    rasTC = arcpy.sa.Con(rasTempTC > 100, 100, rasTempTC)
    pathOutTC = os.path.join(pathOut, "acfgcs_"+ strDate + "_TVCpc.tif")
    arcpy.CopyRaster_management(rasTC, pathOutTC, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
    del rasOutPV, rasOutNPV, rasTC, rasTempTC
    print("TVC done")
    
#    rasUE = arcpy.sa.Raster(os.path.join(pathIn,img, "Band_4"))
#    arcpy.env.cellSize = rasUE
#    arcpy.env.snapRaster = rasUE
#    pathOutUE = os.path.join(pathOut, "acfgcs_"+ strDate + "_UE.tif")
#    arcpy.CopyRaster_management(rasUE, pathOutUE, pixel_type="8_BIT_UNSIGNED", scale_pixel_value="NONE")
#del rasUE
print("Completed Conversion")

arcpy.CheckInExtension("Spatial")
