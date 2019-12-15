import h5py
import json

# There are 149887 photons in ATL03 gt1r (this property is unique for ATL03
# len(set(atl03f['gt1r']['geolocation']['segment_id']))
# There are 921647 signal photons in the ATL08 gt1r track, but only 72079 unique
# Each ATL08 land_segment has a beginning and ending segment id, which appears
# to be 4 photon segments, e.g. 1004095 - 1004099

filename = '_20190905152748_10620408_002_01.h5'
collection = 'ATL03'
f = h5py.File(f"hdfs/{collection}{filename}", 'r')

# 7053 - number of dem_h in 1 ATL08 track
# takes 15 seconds to process (roughly 500ms / dem)
# len(f['gt1r']['heights']['h_ph']) --> 9,978,040 --> would take over 2 days to
# generate geojson and would be very big. perhaps if we can store photons by
# np.sum(list(f['gt1r']['geolocation']['segment_ph_cnt'])) --> 9,978,040
limit = 1000
resolution = 0.00001
ph_idx_max = 9978040
feature_collection = {
    "type": "FeatureCollection",
    "totalFeatures": limit,
    "features": []
}
features_list = []
#feature_type = 'polygon'
feature_type = 'point'

# Should do this for gt1l, gt2r, gt2l, gt3r, gt3l
track = 'gt1r'

if collection == 'ATL03':
    heights = f[track]['heights']
elif collection == 'ATL08':
    land_segments = f[track]['land_segments']

def gen_feature_geometry(latitude, longitude):
    if feature_type == 'polygon':
        max_long = longitude + resolution/2
        min_long = longitude - resolution/2
        max_lat = latitude + resolution/2
        min_lat = latitude - resolution/2
        return {
            "type": "Polygon",
            "coordinates": [ 
                [
                    [ max_long, min_lat ],
                    [ max_long, max_lat ],
                    [ min_long, max_lat ],
                    [ min_long, min_lat ],
                    [ max_long, min_lat ]
                ]
            ]
       }
    else:
       return {
           "type": "Point",
           "coordinates": [ longitude, latitude ] 
       }
   

outfilename = f"{collection}{filename.replace('h5', 'geojson')}"
for idx in range(100000, 150000):
    feature = {
        "type": "Feature",
        "id": idx,
        "geometry_name": "geolocation",
        "properties": {
            "filename": filename,
            "collection": collection,
            "track": track
        }
    }
    
    if collection == 'ATL03':
        geolocation = f[track]['geolocation'] 
        heights = f[track]['heights']
        # determine the segment id, to be used to store the geojson
        segment_id = int(geolocation['segment_id'][idx])
        ph_idx_beg = int(geolocation['ph_index_beg'][idx])
        ph_idx_end = ph_idx_beg + int(geolocation['segment_ph_cnt'][idx])
        # add to the geojson for that segment id by iterating through
        # reference_photon_index to reference_photon_index + segment_ph_ct
        for ph_idx in range(ph_idx_beg, ph_idx_end):
            if ph_idx < ph_idx_max:
                latitude = float(heights['lat_ph'][ph_idx])
                longitude = float(heights['lon_ph'][ph_idx])
                feature_geometry = gen_feature_geometry(latitude, longitude)
                feature['geometry'] = feature_geometry
                height = float(heights['h_ph'][ph_idx])
                feature['properties']['photon_height_meters'] = height
                feature['properties']['segment_id'] = segment_id
                features_list.append(feature)
        if len(features_list) > 0:
            feature_collection['features'] = features_list
            seg_outfilename = f"{segment_id}_{outfilename}"
            with open(f"geojsons/{seg_outfilename}", 'w') as outfile:
                json.dump(feature_collection, outfile)
                outfile.close()
        features_list = []
    elif collection == 'ATL08':
        latitude = float(land_segments['latitude'][idx])
        longitude = float(land_segments['longitude'][idx])
        feature_geometry = gen_feature_geometry(latitude, longitude)
        feature['geometry'] = feature_geometry
        height = float(land_segments['dem_h'][idx])
        feature['properties']['dem_meters'] = height
        feature['properties']['beginning_segment_id'] = float(land_segments['segment_id_beg'][idx])
        feature['properties']['ending_segment_id'] = float(land_segments['segment_id_end'][idx])
        features_list.append(feature)
        if len(features_list) > 0:
            feature_collection['features'] = features_list
            with open(f"geojsons/{outfilename}", 'w') as outfile:
                json.dump(feature_collection, outfile)
                outfile.close()
        features_list = []

f.close()

