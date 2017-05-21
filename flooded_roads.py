"""
Identify roads that are flooded during hurricane surges using openstreetmap data
"""
import geopandas as gpd
import shapefile
import overpass

filepath = './data/shapefiles/nwptHIA09.shp'

# Define RI CRD dict so that fiona can build a pyproj string
crs = {'proj': 'tmerc',
       'lat_0': '41.08333333333334',
       'lon_0': '-71.5',
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
hur_data = hur_data.to_crs(crs={'init': 'epsg:4326'})


# Get road map data
api = overpass.API()
box = hur_data.total_bounds  # Get the total bounds of the hurricane dataset
map_query = overpass.MapQuery(box[1], box[0], box[3], box[2])  # box edges are west, south, north, east
response = api.Get(map_query)
map_data = gpd.GeoDataFrame.from_features(response['features'])

# response is all map data, extracting roads and prune empty columns, then filter the useful columns
road_data = map_data[map_data.highway.notnull()].dropna(axis=1, how='all')
bad_roads = gpd.sjoin(road_data, hur_data)  # find the map elements that intersect
bad_roads = bad_roads[bad_roads.geom_type =='LineString']  # get just ways, not points
bad_roads = bad_roads[['name', 'highway', 'HURR_CAT', 'geometry']]  # strip away useless columns

# write to file
bad_roads.to_file('./data/road_impact.geojson', driver="GeoJSON")
