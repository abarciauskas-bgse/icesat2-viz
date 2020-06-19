hdf_files=$(ls hdfs/atl08_003/*[0-9].h5)

for file in $hdf_files
do
  filename_no_suffix=${file%".h5"}
  echo $filename_no_suffix
  ./hdf-to-mbtiles.sh $filename_no_suffix
done
