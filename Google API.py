# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 16:04:26 2021

@author: jakob
"""
#Source: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from ast import literal_eval

#Use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

#Find the workbook by name and open the first sheet
sheet = client.open("scrape").sheet1

#convert data to pandas dataframe
data = sheet.get_all_values()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)

#change types to int
df['Year'] = df['Year'].astype(int)
df.loc[df['INES level'] == '', 'INES level'] = 0
df['INES level'] = df['INES level'].astype(int)

#add missing data (INES level)
df.loc[df.Incident == "Erwin", "INES level"] = 2
df.loc[df.Incident == "Onagawa", "INES level"] = 2
df.loc[df.Incident == "Greifswald", "INES level"] = 2
df.loc[df.Incident == "Lucens", "INES level"] = 4
df.loc[df.Incident == "Chapelcross", "INES level"] = 4
df.loc[df.Incident == "Monroe", "INES level"] = 4
df.loc[df.Incident == "Santa Susana Field Laboratory", "INES level"] = 4
df.loc[df.Incident == "Chalk River", "INES level"] = 5
df.loc[df.Incident == "Vinča", "INES level"] = 4

#add missing data (location)
df.loc[df.Incident == "Fleurus", "Location"] = '50.483070, 4.549670'
df.loc[(df.Incident == "Charlestown"), "Location"] = '41.436111,-71.694444'
df.loc[df.Incident == "Vinča", "Location"] = '44.758292, 20.5962'
df.loc[df.Incident == "Santa Susana Field Laboratory", "Location"] = '34.230822, -118.696375'
df.loc[df.Incident == "Saint Laurent des Eaux", "Location"] = '47.720556, 1.578611'
df.loc[df.Incident == "Kyshtym", "Location"] = '55.7125, 60.848056'
df.loc[df.Incident == "Chalk River", "Location"] = '46.0502, -77.361'
df.loc[df.Incident == "Cadarache", "Location"] = '43.6875, 5.761944'
df.loc[df.Incident == "Lucens", "Location"] = '46.692822, 6.826892'
df.loc[df.Incident == "Windscale Pile", "Location"] = '54.4237, -3.4982'
df.loc[df.Incident == "Yanangio", "Location"] = '-11.2212, -75.4695'

#put latitude and longitude data in seperate columns
df['Location'] = [literal_eval(x) for x in df['Location']]
df[['latitude', 'longitude']] = pd.DataFrame(df['Location'].tolist())

#save data to csv
df.to_csv("Nuclear accidents.csv", index=False)