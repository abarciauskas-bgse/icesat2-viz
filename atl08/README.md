# Create mbtiles from ICESat-2 ATL08

## Pre-requisites

* URS Earthdata login for downloading ATL08 files
* python modules: h5py, numpy for generating h5 file of all beams
* [yarn](https://yarnpkg.com/)
* [pdal](https://pdal.io/) for generating geojson from HDF files. You will need
  the HDF plugin installed, this may require building from source and ensuring
  the `PDAL_DRIVER_PATH` is set.
* [tippecanoe](https://github.com/mapbox/tippecanoe) for generating mbtiles from geojsons
* [tileserver-gl](https://tileserver.readthedocs.io/) as an http server for the mbtiles
* [deck.gl](https://github.com/visgl/deck.gl) (just for viz): `npm install @deck.gl/core @deck.gl/layers @deck.gl/mesh-layers @deck.gl/geo-layers`

## Generate mbtiles for each granule

Takes about ~15 minutes on my mac for 135 ATL08 files

```bash
# Expects EARTHDATA username / password in ~/.netrc
python3 nsidc-download_ATL08.003_2020-06-17.py
# move files to hdfs/atl08_003
./hdf-to-mbtiles.sh
```

## Join all

Takes ~10 minutes on my mac

```bash
tile-join -o atl08.mbtiles hdfs/atl08_003/*.mbtiles
```

## Run the tileserver

```bash
tileserver-gl atl08.mbtiles
```

## Visualize them using deck.gl

```bash
cd deck-viz
yarn
npm start
```

