#!/bin/bash

FILENAME=$1
python3 prepare-hdf-beams.py --input-file ${FILENAME}.h5
pdal pipeline atl08-hdf-to-geojson.json \
  --readers.hdf.filename=${FILENAME}_xyz.h5 \
  --writers.text.filename=${FILENAME}.geojson
tippecanoe -o ${FILENAME}.mbtiles ${FILENAME}.geojson --force

