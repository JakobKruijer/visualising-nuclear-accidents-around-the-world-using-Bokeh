# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 19:41:53 2021

@author: jakob
"""
#import libraries
import pandas as pd
from bokeh.io import show, output_file
from bokeh.plotting import figure, ColumnDataSource, curdoc
from bokeh.palettes import Spectral4, Colorblind5
from bokeh.layouts import row, column
from bokeh.models import HoverTool, Select, RangeSlider, Div, Slider, LabelSet
from bokeh.models.widgets import Tabs, Panel
from bokeh.transform import factor_cmap
from bokeh.tile_providers import get_provider, CARTODBPOSITRON_RETINA
from pyproj import Proj, transform


#import datasets
df_nuclear_production = pd.read_csv('nuclear-energy-generation.csv')
df_fossil_production = pd.read_csv('fossil-fuel-production.csv')
df_fossil_emissions = pd.read_csv('co2-emissions-by-fuel-line.csv')
df_nuclear_accidents = pd.read_csv('Nuclear accidents.csv')

#rename columns and drop unused columns
df_nuclear_production = df_nuclear_production.rename(columns={"Electricity from nuclear (TWh)" : "Nuclear_Production"})
df_fossil_production = df_fossil_production.rename(columns={"Coal Production - EJ" : "Coal_Production",
                                                   "Gas Production - EJ" : 'Gas_Production',
                                                   'Oil Production - Tonnes' : 'Oil_Production'})
df_fossil_emissions = df_fossil_emissions.rename(columns={'CO2 emissions from oil' : 'Oil_Emissions',
                                                        'CO2 emissions from coal' : 'Coal_Emissions',
                                                        'CO2 emissions from gas' : 'Gas_Emissions'})
df_fossil_emissions = df_fossil_emissions.drop(columns=['CO2 emissions from flaring', 
                                                        'CO2 emissions from cement', 
                                                        'CO2 emissions from other industry'])

#filter for fewer countries (wanted to have all countries but could not make the checkboxgroup widget work)
df_fossil_emissions = df_fossil_emissions.loc[df_fossil_emissions['Entity'].isin(["Netherlands",
                                                                                      'France', 
                                                                                      'Belgium', 
                                                                                      'Germany', 
                                                                                      'Spain'])]

#sort the fossil emissions dataframe by country and year and filter out data from before 1965
df_fossil_emissions = df_fossil_emissions.sort_values(['Entity','Year'])
df_fossil_emissions = df_fossil_emissions[df_fossil_emissions.Year >= 1965]

#merge nuclear production data wit fossil production data
df_production = pd.merge(df_nuclear_production, df_fossil_production, on=["Entity", "Code", "Year"], how = 'outer')

#filter for fewer countries (wanted to have all countries but could not make the checkboxgroup widget work)
df_production = df_production.loc[df_production['Entity'].isin(["Netherlands",
                                'France', 
                                'Belgium', 
                                'Germany', 
                                'Spain'])]

#convert all units to Terawatt Hours (TWh)
df_production['Coal_Production'] = 277.7778 * df_production['Coal_Production']
df_production['Gas_Production'] = 277.7778 * df_production['Gas_Production']
df_production["Oil_Production"] = 1.163e-5 * df_production["Oil_Production"]

#covert tonnes of CO2 emmited to millions of tonnes 
df_fossil_emissions['Oil_Emissions'] = df_fossil_emissions['Oil_Emissions'] / 1000000
df_fossil_emissions['Gas_Emissions'] = df_fossil_emissions['Gas_Emissions'] / 1000000
df_fossil_emissions['Coal_Emissions'] = df_fossil_emissions['Coal_Emissions'] / 1000000

#replace nan values with 0
df_production = df_production.fillna(0)
df_fossil_emissions = df_fossil_emissions.fillna(0)

#LINEPLOT
#put all production data in lists of lists (needed for mulit_line)
list_production = df_production.transpose().values.tolist()

list2 = list_production[2]
list3 = list2[:56]
Year = [list3, list3, list3, list3, list3] 

list4 = list_production[3]
i=0
Nuclear=[]
while i<len(list4):
  Nuclear.append(list4[i:i+56])
  i+=56
  
list5 = list_production[4]
i=0
Coal=[]
while i<len(list5):
  Coal.append(list5[i:i+56])
  i+=56

list6 = list_production[5]
i=0
Gas=[]
while i<len(list6):
  Gas.append(list6[i:i+56])
  i+=56

list7 = list_production[6]
i=0
Oil=[]
while i<len(list7):
  Oil.append(list7[i:i+56])
  i+=56 

#put all emissions data in to lists of lists (needed for multi_line)
list_emissions = df_fossil_emissions.transpose().values.tolist()
  
list8 = list_emissions[3]
i=0
Oil_emissions=[]
while i<len(list8):
  Oil_emissions.append(list8[i:i+55])
  i+=55

list9 = list_emissions[4]
i=0
Coal_emissions=[]
while i<len(list9):
  Coal_emissions.append(list9[i:i+55])
  i+=55

list10 = list_emissions[5]
i=0
Gas_emissions=[]
while i<len(list10):
  Gas_emissions.append(list10[i:i+55])
  i+=55

#create list of countries to use as legend data in the line plot
legend=sorted(list(df_production['Entity'].value_counts().index))

#color pallete used in line graph
color = list(Colorblind5)

#CDS for line graph
source_line = ColumnDataSource(data= {
    'xs' : Year,
    "ys" : Nuclear,
    'color' : color,
    'legend' : legend})

#defining ranges for line plot
xmin, xmax = min(df_production.Year), max(df_production.Year)
ymin, ymax = 0, max(max(Nuclear)) + 100

#create the figure for the line plot
p_line = figure(title='Nuclear power generation (TWh) between 1965 and 2020',
           plot_height=600,
           plot_width=700,
           x_axis_label= 'Year',
           x_range=(xmin, xmax),
           y_range=(ymin, ymax),
           toolbar_location="above",
           tools="pan,wheel_zoom,box_zoom,save,reset,tap",
           active_scroll="wheel_zoom")

#plot the lines
p_line.multi_line(xs = 'xs',
             ys = 'ys',
             line_color = 'color',
             line_width = 2,
             legend = 'legend',
             source = source_line)

#line plot styling
p_line.yaxis.axis_label = 'Nuclear energy production (TWh)'
p_line.legend.location = 'top_left'
p_line.legend.title = "Country"
p_line.legend.title_text_font_style = "bold"
p_line.legend.title_text_font_size = "20px"
p_line.legend.background_fill_color = "whitesmoke"
p_line.toolbar.logo = None
p_line.toolbar.autohide = True


#BARPLOT
#list of energy types (barplot x-axis data)
energy_sources = ['Nuclear', 'Coal', 'Gas', 'Oil']

#cumulative of total production and emissions (barplot y-axis data)
total_nuclear_production = df_production['Nuclear_Production'].sum()
total_coal_production  = df_production['Coal_Production'].sum()
total_gas_production = df_production['Gas_Production'].sum()
total_oil_production = df_production['Oil_Production'].sum()
total_production = [total_nuclear_production, total_coal_production, total_gas_production, total_oil_production]

#devide by 100 to go from million to billion
total_coal_emissions = df_fossil_emissions['Coal_Emissions'].sum() / 100
total_gas_emissions = df_fossil_emissions['Gas_Emissions'].sum() / 100
total_oil_emissions = df_fossil_emissions['Oil_Emissions'].sum() / 100
total_emissions = [0, total_coal_emissions, total_gas_emissions, total_oil_emissions]

#remove decimals so that the value above the bars doenst show the whole float
total_production = list(map(int, total_production))
total_emissions = list(map(int, total_emissions))

#CDS for barplot
source_bar = ColumnDataSource(data= {
    'energy_sources' : energy_sources,
    'total' : total_production})

#defining ranges for the bar plot
ymin2, ymax2 = 0, max(total_production) + 10000

#create the figure for the bar plot
p_bar = figure(x_range=energy_sources,
            plot_height=600,
            plot_width=600,
            x_axis_label='Energy type',
            y_axis_location="right",
            y_range=(ymin2, ymax2),
            title="Total energy production (TWh) from 1965 till 2020 by energy type",
            toolbar_location=None, tools="")

#plot the bars
p_bar.vbar(x='energy_sources', top='total', width=0.9, source=source_bar, legend_field="energy_sources",
       line_color='white', fill_color=factor_cmap('energy_sources', palette=Spectral4, factors=energy_sources))

#bar plot styling
p_bar.yaxis.axis_label = "Terawatt hour (TWh)"
p_bar.xaxis.major_label_text_font_style = 'bold'
p_bar.xgrid.grid_line_color = None
p_bar.legend.orientation = "horizontal"
p_bar.legend.location = "top_center"
p_bar.legend.background_fill_color = "whitesmoke"
p_bar.ygrid.grid_line_dash = [6, 4]

#put value above the bars
labels_bar = LabelSet(x='energy_sources', y='total', text='total', text_font_style = 'bold', text_align='center', y_offset=8, source=source_bar, render_mode='canvas')
p_bar.add_layout(labels_bar)


#MAPPLOT
#get location data of the world and use that as x and y ranges, source: https://coderzcolumn.com/tutorials/data-science/plotting-maps-using-bokeh
inProj = Proj(init='epsg:3857')
outProj = Proj(init='epsg:4326')

world_lon1, world_lat1 = transform(outProj,inProj,-180,-85)
world_lon2, world_lat2 = transform(outProj,inProj,180,85)

cartodb = get_provider(CARTODBPOSITRON_RETINA)

#create figure for the map
p_map = figure(title='Nuclear accidents around the world in 2011',
           plot_width=800, plot_height=700,
           toolbar_location="above",
           tools="pan,wheel_zoom,box_zoom,save,reset",
           active_scroll="wheel_zoom",
           x_range=(world_lon1, world_lon2),
           y_range=(world_lat1, world_lat2),
           x_axis_type="mercator", y_axis_type="mercator",
           x_axis_label='Latitude', y_axis_label='Longitude')

#add map to figure
p_map.add_tile(cartodb)

#map figure styling
p_map.toolbar.autohide = True
p_map.toolbar.logo = None
p_map.xaxis.axis_label_text_font_style = 'bold'
p_map.yaxis.axis_label_text_font_style = 'bold'

#convert latitude and longitude data to Mercator coördinates and put in df
lons, lats = [], []
for lon, lat in list(zip(df_nuclear_accidents["longitude"], df_nuclear_accidents["latitude"])):
    x, y = transform(outProj,inProj,lon,lat)
    lons.append(x)
    lats.append(y)
    
df_nuclear_accidents["MercatorX"] = lons
df_nuclear_accidents["MercatorY"] = lats

#Make column to use as size for circles 
df_nuclear_accidents['INES level_px'] = df_nuclear_accidents['INES level'] *10
df_nuclear_accidents.loc[df_nuclear_accidents['INES level_px']== 0, "INES level_px"] = 10

#assign different colors for each INES level
colormap = {0: '#57595d', 1: '#008000', 2: '#99cc00', 3: '#ffcc00', 4 :'#ff9900', 5: "#ff6600", 6 : "#ff0000", 7 : "#ff00ff"}
df_nuclear_accidents['colors'] = [colormap[x] for x in df_nuclear_accidents['INES level']]

#define the start layout and use that data in the columndatasource
df_start = df_nuclear_accidents[df_nuclear_accidents['Year'] == 2011]
source_map = ColumnDataSource(df_start)

#plot circles
p_map.circle(x="MercatorX", y="MercatorY",
         size='INES level_px',
         fill_color='colors', line_color='colors',
         fill_alpha=0.3,
         source=source_map)

#legend with text explanation
p_legend = figure(title='INES level', plot_width=200, plot_height=820, x_range=(0, 2),
           y_range=(0, 10))
p_legend.toolbar.active_drag = None
p_legend.toolbar.logo = None
p_legend.toolbar_location = None
p_legend.grid.visible = False
p_legend.axis.visible = False
p_legend.outline_line_color = None
p_legend.title.align = "center"

source4 = ColumnDataSource(data=dict(x=[1,1,1,1,1,1,1,1],
                                     y=[0.8,1.6,2.7,3.9,5.3,6.6,7.8,9.2],
                                     size=[20,25,30,35,40,50,60,70],
                                     color=['#57595d', '#008000', '#99cc00', '#ffcc00', '#ff9900', "#ff6600", "#ff0000", "#ff00ff"],
                                     line_color=['#57595d', '#008000', '#99cc00', '#ffcc00', '#ff9900', "#ff6600", "#ff0000", "#ff00ff"],
                                     text=['','1','2','3','4','5','6','7']))
p_legend.circle(x='x', y='y', size='size', color='color',  fill_alpha=0.3, line_color='color', source=source4)
text_legend = Div(text='<br><br><p>Major release of radio active material with widespread health and environmental effects requiring implementation of planned and extended countermeasures.</p><br><p>Significant release of radioactive material likely to require implementation of planned countermeasures.</p><br><p>Limited release of radioactive material likely to require implementation of some planned countermeasures. Several deaths from radiation.</p><br><p>Minor release of radioactive material unlikely to result in implementation of planned countermeasures other than local food controls. At least one death from radiation.</p><br><p>Exposure in excess of ten times the statutory annual limit for workers. Non-lethal deterministic health effect (e.g., burns) from radiation.</p><br><p>Exposure of a member of the public in excess of 10 mSv. Exposure of a worker in excess of the statutory annual limits.</p><br><p>Anomaly</p><br><p>No INES level available</p>',
           width=300, height=700)
labels = LabelSet(x='x', y='y', y_offset=-9, text='text', text_align='center', source=source4, render_mode='canvas')
p_legend.add_layout(labels)


#Callback for interactivity
def callback (attr, old, new):
    #collect values from dropdown menus and slider line plot
    y = select_production.value + select_emissions.value
    year_start, year_end = slider_line_plot.value
    
    #adjust x-range based on new slider value
    p_line.x_range.start = year_start
    p_line.x_range.end = year_end
    
    #collect value from slider map and adjust data accordingly
    yr = slider_map_plot.value     
    new_data_map = df_nuclear_accidents[df_nuclear_accidents['Year'] == yr]
    p_map.title.text = 'Nuclear accidents around the world in ' + str(yr)        
    source_map.data = new_data_map

    #define what data should be used when values from the production dropdown menu are selected
    if y == 'Nuclear' or y == 'Coal' or y ==  'Gas' or y == 'Oil' or y== '':
        p_line.y_range.end = max(max(eval(y))) + 100
    
        p_line.yaxis.axis_label = y + " energy production (TWh)"
        p_line.title.text = y + ' power generation (TWh) between ' + str(year_start) + ' and ' + str(year_end)
        p_bar.title.text = 'Total energy production (TWh) from 1965 till 2020 by energy type'

        new_data_line = {
            'xs' : Year,            
            'ys' : eval(y),
            'color' : color,
            'legend' : legend}
        source_line.data = new_data_line

        p_bar.y_range.end = max(total_production) + 10000
        p_bar.yaxis.axis_label = "Terawatt hour (TWh)"

        new_data_bar = {
            'energy_sources' : energy_sources,
            'total' : total_production}
        source_bar.data = new_data_bar
        
    #define what data should be used when values from the emissions dropdown menu are selected
    else:
        p_line.y_range.end = max(sum(eval(y),[])) + 100
            
        p_line.yaxis.axis_label = y + " (million tonnes of CO2)"
        p_line.title.text = y + ' between ' + str(year_start) + ' and ' + str(year_end)
        p_bar.title.text = 'Total CO2 emissions from 1965 till 2019 by energy type'
    
        new_data_line = {
                'xs' : Year,            
                'ys' : eval(y),
                'color' : color,
                'legend' : legend}
        source_line.data = new_data_line
       
        p_bar.y_range.end = max(total_emissions) + 50
        p_bar.yaxis.axis_label = "Billion tonnes of CO2"
            
        new_data_bar = {
                'energy_sources' : energy_sources,
                'total' : total_emissions}
        source_bar.data = new_data_bar

#defining widgets            
select_production = Select(options=['Nuclear', 'Coal', 'Gas', 'Oil', ''], width=200, value='Nuclear', title='Energy production (TWh)')
select_emissions = Select(options=['Coal_emissions', 'Gas_emissions', 'Oil_emissions', ''], width=200, value='', title='CO2 emissions')
slider_line_plot = RangeSlider(start=1965, end=2020, value=(1965,2020), step=1, title="Year")
slider_map_plot = Slider(title = 'Year',start = 1952, end = 2011, step = 1, value = 2011)   

#hovertool for the map plot
hover_map = HoverTool(tooltips=[("Power plant", "@Incident"), ("Country", "@Country"), ('Year', '@Year'), ('INES level', '@{INES level}')]) 
p_map.add_tools(hover_map)

#connect widgets to the callback function
select_production.on_change('value', callback)
select_emissions.on_change('value', callback)
slider_line_plot.on_change('value', callback)
slider_map_plot.on_change('value', callback)

text_header = Div(text='<H1>Energy exploration tool<H1>', width=200, height=100)
text_line = Div(text='<p align="justify">Use this tool to explore energy production and emissions throughout the years. Select an energy type from the dropdown menu and use the slider to indicate what timeframe you want to explore further. Click on a line to hide all other lines. Learn more about nuclear accidents around the world by clicking the tab at the top of the page.<p>',
                        width=200, height=300)
text_map = Div(text='<p align="justify">Use this map to exlpore nuclear accidents around the world. The accidents are indicated by circles. The bigger the circle, the more severe the accident. See the legend for more information on the impact of the accidents and use the slider to filter through the years.<p>',
                        width=200, height=300)


#create layouts for each tab
layout_line_bar = column(text_header, row(column(text_line, select_production, select_emissions), column(p_line, slider_line_plot), p_bar))
layout_map = column(text_header, row(text_map, column(p_map, slider_map_plot), p_legend, text_legend))

#create tabs and final layout
tab1 = Panel(child=layout_line_bar, title='Energy production vs emissions')
tab2 = Panel(child=layout_map, title='Nuclear accidents around the world')
layout = Tabs(tabs=[tab1, tab2])

#add layout to the document
curdoc().add_root(layout)
output_file('line.html')
show(layout)