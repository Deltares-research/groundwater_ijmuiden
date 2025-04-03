import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
import pyproj
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Calibri"
import numpy as np
from sklearn.linear_model import LinearRegression
from pathlib import Path

path_mc = Path(r'N:/Projects/11207500/11207510/B. Measurements and calculations')
path_oi = Path(r'N:/Projects/11207500/11207510/F. Other information')

# background layers
water = gpd.read_file(path_oi.joinpath(r'gis-layers/Structuurvisie__Grote_wateren.shp'))
water['color'] = ['skyblue','lightblue','lightblue','lightblue','lightblue','lightblue']
land = gpd.read_file(path_oi.joinpath(r'gis-layers/land.shp'))

# data
metadata = pd.read_excel(path_mc.joinpath(r'01_metadata/peilbuizen_metadata.xlsx'), index_col=0)

bemonstering = pd.read_excel(path_mc.joinpath(r'05_waterkwaliteitmonsters/bemonstering_10-08-2022.xlsx'),
                             header=0, skiprows=[1]).set_index('Peilbuis')
bemonstering.replace('n.a.', np.NaN, inplace=True)
bemonstering.columns = bemonstering.columns.str.replace('\n \n', '').str.replace('\n', '')

handmetingen = pd.read_csv(path_mc.joinpath(r'02_handmetingen/handmetingen_23052023.csv'),
                           skiprows = 19, delimiter = ';', encoding = "ISO-8859-1",index_col = 0)
handmetingen = handmetingen.rename(columns={'Electrical Conductivity[ÂµS/cm]':'electrical_conductivity [µS/cm]'})

#%% relatie EC, chloride-concentratie

data = bemonstering.join(handmetingen[['electrical_conductivity [µS/cm]']])
data = data.dropna(subset = ['Chloride', 'electrical_conductivity [µS/cm]'])

x = data.sort_values('electrical_conductivity [µS/cm]')['electrical_conductivity [µS/cm]'].values/1000
y = data.sort_values('electrical_conductivity [µS/cm]')['Chloride'].values  
length = len(x)
reg = LinearRegression().fit(x.reshape(length, 1),y.reshape(length, 1))
reg.coef_
reg.intercept_

fig, ax = plt.subplots(nrows=1, ncols=1,dpi = 400, figsize=(8.27,11.69/3),sharey=True, sharex= True)
ax.scatter(x,y, color = 'red')
ax.plot(x,reg.predict(x.reshape(length, 1)), color='blue', linewidth=2, ls = '--')
ax.set_xlabel('EC [mS/cm]')
ax.set_ylabel('Chloride [mg/L]')
ax.set_yscale('log')

ax.hlines(150,0,40, color = 'black')
ax.hlines(300,0,40, color = 'black')
ax.hlines(1000,0,40, color = 'black')
ax.hlines(10000,0,40, color = 'black')
ax.annotate(text='zoet',xy=(35,60))
ax.annotate(text='zoet-\nbrak',xy=(35,170))
ax.annotate(text='brak',xy=(35,470))
ax.annotate(text='brak-zout',xy=(35,2200))
ax.annotate(text='zout',xy=(35,12000))
ax.set_xlim([0,40])
ax.set_ylim([0,20000])
ax.set_title('Relatie EC en Chloride-concentratie',fontweight="bold", size = 10)

#%% load data to plot
data = metadata[['X-coord', 'Y-coord']]
data = data.join(handmetingen[['electrical_conductivity [µS/cm]']])
data = data.join(bemonstering[['Chloride']])
for peilbuis_id in data.index.to_list():    
    try:
        fresh_water_head = pd.read_csv(path_mc.joinpath(f'03_divers/zoetwaterstijghoogte/{peilbuis_id}.csv'), parse_dates=True, index_col=0)
        data.loc[peilbuis_id, 'mean_fresh_water_head (m NAP)'] = fresh_water_head['fresh_water_head (m NAP)'].mean()
    except FileNotFoundError:
        continue

src_crs = pyproj.CRS("EPSG:28992")
target_crs = pyproj.CRS("EPSG:3857")
trans = pyproj.Transformer.from_crs(src_crs, target_crs, always_xy=True)
geometry = [Point(trans.transform(x, y)) for x, y in zip(data['X-coord'], data['Y-coord'])]
plot_gdf = gpd.GeoDataFrame(data, geometry=geometry, crs=target_crs)


#%% plot fresh water head
markersize = 20
textsize = 10
titlesize = 12
xmin, ymin = trans.transform(101000, 497750)
xmax, ymax = trans.transform(103500, 499100)
basemap = ctx.providers.CartoDB.Positron
variable = 'electrical_conductivity [µS/cm]'
title = 'Elektrische geleidbaarheid [µS/cm]'

##
mask_aquifer_1 = plot_gdf.dropna(subset=[variable]).index.str.contains('_1') 
mask_aquifer_2 = plot_gdf.dropna(subset=[variable]).index.str.contains('_2') 
mask_aquifer_3 = plot_gdf.dropna(subset=[variable]).index.str.contains('_3') 

fig, ax = plt.subplots(dpi=400, figsize=(11.69, 6.27))
plot_gdf.dropna(subset=[variable]).plot(ax=ax, color='black', marker='o', markersize=markersize)

for idx, row in plot_gdf.dropna(subset=[variable])[mask_aquifer_1].iterrows():
    ax.annotate(text=str(np.round(row[variable],2)), xy=(row['geometry'].x, row['geometry'].y),
                xytext=(1, 3), textcoords="offset points", size=textsize, color='black')

for idx, row in plot_gdf.dropna(subset=[variable])[mask_aquifer_2].iterrows():
    ax.annotate(text=str(np.round(row[variable],2)), xy=(row['geometry'].x, row['geometry'].y), 
                xytext=(1, -7), textcoords="offset points", size=textsize,color='maroon')

for idx, row in plot_gdf.dropna(subset=[variable])[mask_aquifer_3].iterrows():
    ax.annotate(text=str(np.round(row[variable],2)), xy=(row['geometry'].x, row['geometry'].y), 
                xytext=(1, -16), textcoords="offset points", size = textsize,color='navy')
    
if variable == 'mean_fresh_water_head (m NAP)':
    ax.annotate(text='Noordzeekanaal \n (ca. -0.40 [m NAP])', xy=trans.transform(102850,497900), size=textsize, color='darkslategrey', ha='center')
    ax.annotate(text='Noordzee \n (-1.35 - 1.80 [m NAP])', xy=trans.transform(101350,498000), size=textsize, color='darkslategrey', ha='center')  
elif variable == 'electrical_conductivity [µS/cm]':   
    ax.annotate(text='Noordzeekanaal \n (16700 [µS/cm])', xy=trans.transform(102850,497900), size=textsize, color='darkslategrey', ha='center')
    ax.annotate(text='Noordzee \n (34500 [µS/cm])', xy=trans.transform(101350,498000), size=textsize, color='darkslategrey', ha='center')
elif variable == 'Chloride':   
    ax.annotate(text='Noordzeekanaal \n (5814 [mg/L])', xy=trans.transform(102850,497900), size=textsize, color='darkslategrey', ha='center')
    ax.annotate(text='Noordzee \n (12584 [mg/L])', xy=trans.transform(101350,498000), size=textsize, color='darkslategrey', ha='center')
    
ax.annotate(text=' x.xx: freatisch pakket', xy=trans.transform(101020,499070), size=textsize, color='black')
ax.annotate(text=' x.xx: 1e watervoerende pakket', xy=trans.transform(101020,499010), size=textsize, color='maroon')
ax.annotate(text=' x.xx: 2e watervoerende pakket', xy=trans.transform(101020,498950), size=textsize, color='navy')

ax.set_xlim([xmin,xmax])
ax.set_ylim([ymin,ymax])
ax.set_title(title,fontweight="bold", size=titlesize)
ctx.add_basemap(ax, source=basemap)
ax.axis('off')
plt.tight_layout()
output_name = variable.split(' ')[0]
fig.savefig(path_mc.joinpath(f'06_webviewer/maps_figures/map_{output_name}.png'))


