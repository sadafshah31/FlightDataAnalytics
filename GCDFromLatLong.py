# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 11:34:39 2019

@author: naqiw
"""


import math
import pandas as pd
import numpy as np

try:
    # Trying to find module in the parent package
    import lib.database
    print('database')
    del database
except ImportError:
    print('Relative import failed')

try:
    # Trying to find module on sys.path
    import lib.database
    print('successful')
except ModuleNotFoundError:
    print('Absolute import failed')

##########################################################################################

def degreeToRadian(deg):
    return deg*math.pi/180

def radianToDegree(rad):
    return rad*(180/math.pi)

def degreeToNauticalMiles(deg):
    return deg*60

def radiansToMeters(radians):
    return radians*6371000

def metersToKilometers(meters):
    return meters/1000
    
    
def GCD(Angle_Radians):
    return Angle_Radians * 60

def Angle_Radians(BaseLat_Radians, BaseLon_Radians, LatA_Radians, LonA_Radians):    
    return math.acos(math.sin(BaseLat_Radians)*math.sin(LatA_Radians) + 
       math.cos(BaseLat_Radians)*math.cos(LatA_Radians)*
       math.cos((LonA_Radians)-(BaseLon_Radians)))

def timeToSeconds(dfTime)    :
    return (((pd.to_datetime(dfTime['Datetime']).dt.hour) *60*60) + 
                   (pd.to_datetime(dfTime['Datetime']).dt.minute * 60) + 
                   (pd.to_datetime(dfTime['Datetime']).dt.second))
    
def InterpolatedTimeValueAtDistanceCategory(df,NMDistanceCategory,categoryFlag):    
    df1 = df[(df[categoryFlag] == True) |((df[categoryFlag] == True).shift(1).fillna(False))]    
    
    df1['Time'] = timeToSeconds(df1)    
    
    slope = (df1['Time'].iloc[1] - df1['Time'].iloc[0]) / (df1['NauticalMiles'].iloc[0] - df1['NauticalMiles'].iloc[1])      
    InterpolatedTimeInSeconds = df1['Time'].iloc[1]+slope*(NMDistanceCategory-df1['NauticalMiles'].iloc[1])        
    return InterpolatedTimeInSeconds
###########################################################################################
airportLatitude= 25.2048
airportLongitude= 55.2708
NauticalMilesCategory1=120
NauticalMilesCategory2=250

file = r'C:\Users\naqiw\Desktop\UAE_Flightaware test\UAE_FlightAware_August\DXBArrival\read\UAE-A388_A6EEW_20190812_210952_EGKK_20190813_032542_OMDB_10_UAE10-1565412339-airline-0195_4208091_visium_fuel_timeseries_v8.2_FlightAware.csv'
filename = 'UAE-A388_A6EEW_20190812_210952_EGKK_20190813_032542_OMDB_10_UAE10-1565412339-airline-0195_4208091_visium_fuel_timeseries_v8.2_FlightAware.csv'

operator = filename[:3]
aircraftType = filename[4:8]
departureICAO = filename[31:35]
arrivalICAO = filename[52:56]

###########################################################################################
df = pd.read_csv(file)

df['Operator'] = operator
df['Aircraft'] = aircraftType
df['DepartureICAO'] = departureICAO
df['ArrivalICAO'] = arrivalICAO
df['LatitudeSmoothedRadian'] = df['Latitude Smoothed'].apply(degreeToRadian)
df['LongitudeSmoothedRadian'] = df['Longitude Smoothed'].apply(degreeToRadian)
df['airportLatitudeRadian'] = degreeToRadian(airportLatitude)
df['airportLongitudeRadian'] = degreeToRadian(airportLongitude)
df.loc[:,'Angle_Radians'] = np.vectorize(Angle_Radians, otypes=["O"]) (df['airportLatitudeRadian'],df['airportLongitudeRadian'],df['LatitudeSmoothedRadian'],df['LongitudeSmoothedRadian'])
df.loc[:,'Degrees'] = radianToDegree(df['Angle_Radians'])
df.loc[:,'NauticalMiles'] = degreeToNauticalMiles(df['Degrees'])
df.loc[:,'Meters'] = radiansToMeters(df['Angle_Radians'])
df.loc[:,'Kilometers'] = metersToKilometers(df['Meters'])
df.loc[:,'NextNMValue'] = df['NauticalMiles'].shift(-1)
df.loc[:,'NauticalMilesCategory1NMFlag'] = (df['NauticalMiles'] > int(NauticalMilesCategory1)) & (df['NextNMValue'] < int(NauticalMilesCategory1))
df.loc[:,'NauticalMilesCategory2NMFlag'] = (df['NauticalMiles'] > int(NauticalMilesCategory2)) & (df['NextNMValue'] < int(NauticalMilesCategory2))


InterpolatedTimeValueAtDistanceCategory1 = InterpolatedTimeValueAtDistanceCategory(df,NauticalMilesCategory1,'NauticalMilesCategory1NMFlag')
InterpolatedTimeValueAtDistanceCategory2 = InterpolatedTimeValueAtDistanceCategory(df,NauticalMilesCategory2,'NauticalMilesCategory2NMFlag')
DepartureDateTimesInSeconds = timeToSeconds(df)
df.loc[:,'InterpolatedTimeInSecondsAtDistanceCategory_Category1NM'] = InterpolatedTimeValueAtDistanceCategory1
df.loc[:,'InterpolatedTimeInSecondsAtDistanceCategory_Category2NM'] = InterpolatedTimeValueAtDistanceCategory2
df.loc[:,'DepartureDateTimesInSeconds'] = DepartureDateTimesInSeconds

TimeToDestinationInSecondsForCategory1 = DepartureDateTimesInSeconds - InterpolatedTimeValueAtDistanceCategory1
TimeToDestinationInSecondsForCategory2 = DepartureDateTimesInSeconds - InterpolatedTimeValueAtDistanceCategory2

df.loc[:,'TimeToDestinationInSecondsForCategory1'] = TimeToDestinationInSecondsForCategory1
df.loc[:,'TimeToDestinationInSecondsForCategory2'] = TimeToDestinationInSecondsForCategory2

df.loc[:,'TimeToDestinationInMinutesForCategory1'] = TimeToDestinationInSecondsForCategory1/60
df.loc[:,'TimeToDestinationInMinutesForCategory2'] = TimeToDestinationInSecondsForCategory2/60

df.to_csv(r'C:\Users\naqiw\Desktop\UAE_Flightaware test\UAE_FlightAware_August\DXBArrival\read\Tes1_FlightAware.csv')