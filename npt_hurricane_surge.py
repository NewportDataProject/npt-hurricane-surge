"""
Analyze Newport County Hurricane Surge Data

Data Source: http://www.rigis.org/data/inundation09

Coordinate reference system = 
RI State 1983 string:
+proj=tmerc +lat_0=41.08333333333334 +lon_0=-71.5 +k=0.99999375 +x_0=100000 +y_0=0 +datum=NAD83 +units=us-ft +no_defs

The RI EPSG code isn't in the pyproj list, so you need to hard-code the string in as a dict.

"""

import geopandas as gpd
import shapefile

filepath = './data/shapefiles/nwptHIA09.shp'

# Define RI CRD dict so that fiona can build a pyproj string
crs = {'proj': 'tmerc',
       'lat_0': '41.08333333333334',
       'lon_0': '71.5',
       'k': '0.99999375',
       'x_0': '100000',
       'y_0': '0',
       'datum': 'NAD83',
       'units': 'us-ft'}

reader = shapefile.Reader(filepath)

# Extract the column names for the data
fields = reader.fields[1:]
field_names = [field[0] for field in fields]

buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=atr))
hur_data = gpd.GeoDataFrame.from_features(buffer, crs=crs)

# Convert to WGS84
hur_data.to_crs(crs={'init': 'epsg:4326'})

hur_data.to_file('./data/hur_data.geojson', driver="GeoJSON")
