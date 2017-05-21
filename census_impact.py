"""
Datasets accessed from RIGIS.
"""

import geopandas as gpd
import shapefile
import overpass

surge_file = './data/shapefiles/nwptHIA09.shp'
census_file = './data/shapefiles/censusSF1_2010/censusSF1_2010.shp'

# Define RI CRD dict so that fiona can build a pyproj string
crs = {'proj': 'tmerc',
       'lat_0': '41.08333333333334',
       'lon_0': '-71.5',
       'k': '0.99999375',
       'x_0': '100000',
       'y_0': '0',
       'datum': 'NAD83',
       'units': 'us-ft'}

# Load in storm surge data
reader = shapefile.Reader(surge_file)

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
hur_data = hur_data.to_crs(crs={'init': 'epsg:4326'})

# Load in Census Data
reader = shapefile.Reader(census_file)

# Extract the column names for the data
fields = reader.fields[1:]
field_names = [field[0] for field in fields]

buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=atr))
census_data = gpd.GeoDataFrame.from_features(buffer, crs=crs)
census_data = census_data.to_crs(crs={'init': 'epsg:4326'})

# join datasets by spatial intersection
impacted_tracts = gpd.sjoin(census_data, hur_data)

# Group by hurricane level
grouped_impact = impacted_tracts.groupby('HURR_CAT')

#TODO: