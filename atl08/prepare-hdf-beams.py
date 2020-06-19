#!/usr/bin/env python

import argparse
import h5py
import numpy as np
from pathlib import PurePath

# Script to convert downloaded IceSat-2 granules to digest per beam into a PDAL pipeline
# Credit Joachim Meyer https://github.com/jomey
#
BEAM_CHOICES=[
    'gt1r',
    'gt1l',
    'gt2r',
    'gt2l',
    'gt3r',
    'gt3l',
]

def input_data(file, beam):
    with h5py.File(file, "r") as fi:
        x = fi[f"./{beam}/land_segments/longitude"][:]
        y = fi[f"./{beam}/land_segments/latitude"][:]
        z = fi[f"./{beam}/land_segments/canopy/h_canopy"][:]
        return dict(X=x, Y=y, Z=z, beam=np.full(len(x), beam))


def convert_hdf_columns(file):
    input_file = PurePath(file)
    output_file = input_file.parent / (input_file.stem + f'_xyz.h5')
    all_beams = input_data(file, BEAM_CHOICES[0])
    for idx in range(1, len(BEAM_CHOICES)):
        next_beam = input_data(file, BEAM_CHOICES[idx])
        all_beams['X'] = np.concatenate([all_beams.get('X'), next_beam['X']])
        all_beams['Y'] = np.concatenate([all_beams.get('Y'), next_beam['Y']])
        all_beams['Z'] = np.concatenate([all_beams.get('Z'), next_beam['Z']])
        all_beams['beam'] = np.concatenate([all_beams.get('beam'), next_beam['beam']])
    with h5py.File(output_file, 'w') as f:
        f['X'] = all_beams.get('X')  # write data
        f['Y'] = all_beams.get('Y')
        f['Z'] = all_beams.get('Z')
        f['beam'] = str(all_beams.get('beam'))

def arguments():
    parser = argparse.ArgumentParser("Script to setup HDF file conversion")
    parser.add_argument(
        '--input-file', type=str, required=True, help="Path to input file"
    )
    return parser.parse_args()

if __name__ == '__main__':
    arguments = arguments()
    convert_hdf_columns(arguments.input_file)

