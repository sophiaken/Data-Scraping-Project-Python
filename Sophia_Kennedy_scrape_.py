#import packages
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from pandas.io.html import read_html
import functools
import collections
import re


#List initialization
rank1=[]
estimate1=[]
state1=[]
city=[]
census1=[]
change1=[]
land1=[]
density1=[]
location1=[]


#function to parse the data
def get_data(link):
    web_url=requests.get(link).text
    soup=BeautifulSoup(web_url,'html.parser')
    [s.extract() for s in soup('sup')]
    return soup


#Data extraction from the main table
def get_details(table):
    ths = table.find_all('th')
    headings = [th.text.strip() for th in ths] 
    #iteratiing over the rows to get the required data
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if not tds:
            continue
        #data in each and every row is striped and are stored in the variable
        rank,City,State,estimate,census,change,land_miles,land_km,density_miles,density_km,location = [td.text.strip() for td in tds] 
        #data of each and every variable is stored in the list
        rank1.append(rank)
        city.append(City)
        estimate1.append(estimate)
        state1.append(State)
        census1.append(census)
        change1.append(change)
        land1.append(land_miles)
        density1.append(density_miles)
        location1.append(location)

        
        # accented characters: extract the correct string form.
        if '!' in City:
            City = City[City.index('!')+1:]
        #Creating a dataframe for the first main table in wikipedia page
        df = pd.DataFrame(list(zip(rank1,city,estimate1,state1,census1,change1,land1,density1,location1)),columns =['Rank','city','Total','State','census','change','Land','Density','location'])
    return df[:10]



#Additional data from each and every city in the main table(Here only 10 cities)
def getAdditionalDetails(url):
    gy=['Website','Elevation','Land','Time zone']
    ky=['Mayor','Water']
    
    #iterating through the list of links
    for i in url:
        content = get_data('https://en.wikipedia.org' + i)  
        table = content.find('table', {'class': 'infobox geography vcard'}) #extracting data from the infobox
        for tr in table.find_all('tr'):
            trs=tr.find('td')
            ths=tr.find('th')
            if trs and ths in tr:
                ty=ths.text.strip()
                y=ty.split()
                #Strips the required data
                if ty in gy:
                    result[ty][i.strip('/wiki/')]=trs.text.strip()   
                elif y in ky:
                    result[ty][i.strip('/wiki/')]=trs.text.strip()   
    #creates the dataframe for the details in the infobox for each and every city
    u=pd.DataFrame(result)
    u['city'] = u.index
    u['city']=u['city'].str.split(',').str[0] #Stripping the additional data along the city name eg. Phoenix, Arizona where Arizona is stripped
    return pd.merge(data_frame,u,left_on='city',right_on='city') #Merging the acquired dataframe with main dataframe and returning it
 


 #created a seperate function for extracting data from links in the paragraph about cities , 
 #have extracted only climate but the same function can be used to extract many required data    
def get_main_details(links):
    climate=['Humid subtropical climate','Mediterranean climate','Humid continental climate','Semi-arid climate','Desert climate'] #define the climates as list
    for i in links:
        content=get_data('https://en.wikipedia.org' + i)
        head=content.find(id='Climate')
        p=content.find_all('a')
        for link in p:
            title = link.get('title')
            if title in climate:
                climate_link[i.strip('/wiki/')]=title
    climate_df=pd.DataFrame.from_dict(climate_link,orient='index',columns=['Climate'])
    climate_df['city'] = climate_df.index
    climate_df['city']=climate_df['city'].str.split(',').str[0]
    return climate_df
    
            
#Nested dictionary for storing the data where keys are cities and column headings whereas the values are the data
result = collections.defaultdict(dict)
climate_link={}
city_link=[]
#Extracting data from the main wikipedia page by calling get_data function
content = get_data('https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population')
#Chooses only the first table in the page
tables = content.find_all('table', class_='wikitable sortable')[0]
#Main data frame creation
data_frame=pd.DataFrame()
#Adding the data as rows and columns into the main dataframe
data_frame=get_details(tables)
data_frame=data_frame.replace(' ', '_', regex=True)


#data extraction from the links in the main table 
table = content.find('table', {'class': 'wikitable sortable'})
rows = table.find_all('tr')
data_content = []
for row in rows:
    cells = row.find_all('td')
    if len(cells) > 1:
        cells[1].get_text()
        country_link = cells[1].find('a')
        country_info = [cell.text.strip('\n') for cell in cells]
        data_content.append(country_link.get('href'))

#call to get the data from the info box of each and every city
additional_details = getAdditionalDetails(data_content[:10])
details_paragraph=get_main_details(data_content[:10])
pdp=pd.merge(additional_details,details_paragraph,left_on='city',right_on='city')
print(pdp)
#Converting the dataframe in to a csv file
pdp.to_csv('cities.csv', sep='\t', encoding='utf-8')

    
