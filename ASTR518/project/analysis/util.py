"""
Some helpful utility code for the reduction and reduction analysis
"""

import os
import glob

from dataclasses import dataclass
from collections.abc import MutableMapping

import numpy as np
import matplotlib.pyplot as plt

import ccdproc as ccdp

from astropy.nddata import CCDData
from astropy.visualization import hist
from astropy.stats import mad_std
from astropy import units as u

ccdp_combine_kwargs = dict(
    method="average",
    sigma_clip=True,
    sigma_clip_low_thresh=5,
    sigma_clip_high_thresh=5,
    sigma_clip_func=np.ma.median,
    sigma_clip_dev_func=mad_std
)

class Kuiper:

    # "static" variables
    gain = 3.1 * u.electron/u.adu
    throughput = 0.8578 # assumed from Bok
    quantum_efficiency = 0.7 # assumed from QE curve
    def __init__(self, aperture_radius:int=5):
        self.aperture_radius = aperture_radius
        self.npix = np.pi*aperture_radius**2
        self.electron_to_photons = 1/(self.throughput*self.quantum_efficiency)
class CustomCCDData(CCDData):
    
    def show_image(self, ax=None, fig=None, **kwargs):
        
        if ax is None:
            fig, ax = plt.subplots()
            
        cmap = ax.imshow(self.data, cmap="gray", **kwargs)
        
        fig.colorbar(cmap)
        
        #ax.set_yticklabels([])
        #ax.set_xticklabels([])
            
        return fig, ax

@dataclass
class ReductionFileSet:
    file_list:str
    filter_name:str

class ReductionFileList(MutableMapping):
    
    def __init__(self, file_list:list[ReductionFileSet]):
         self.__dict__ = {
             file.filter_name:file.file_list for file in file_list
         }
    
    def __setitem__(self, filter_name, file_list):
        self.__dict__[filter_name] = file_list
    
    def __getitem__(self, filter_name):
        return self.__dict__[filter_name]
    
    def __delitem__(self, filter_name):
        del self.__dict__[filter_name]
    
    def __iter__(self):
        return iter(self.__dict__)
    
    def __len__(self):
        return len(self.__dict__)
    
    @staticmethod
    def from_list(file_list, filter_names=None):
        if filter_names is None:
            return ReductionFileList([ReductionFileSet(file_list, "none")])
        
        # note this organization algorithm won't work for more complex 
        # data directories but I'll simplify it here
        return ReductionFileList([
            ReductionFileSet(
                file_list=[file for file in file_list if filt in os.path.basename(file)],
                filter_name=filt
            ) for filt in filter_names
        ])
        
@dataclass
class ReductionFiles:
    datadir:str
    
    # filepaths
    target_files:ReductionFileList = None
    flat_files:ReductionFileList = None
    bias_files:ReductionFileList = None
    dark_files:ReductionFileList = None

    def read_and_organize(
        self, 
        target_name:str, 
        flat_name:str="FLAT", 
        bias_name:str="BIAS", 
        dark_name:str="DARK", 
        filter_names:list[str]=["b","r","u","v"]
    ) -> None:
      
        # find the target files
        target_files = glob.glob(os.path.join(self.datadir, f"*{target_name}*fits"))
        assert len(target_files), f"Missing target files, check the target_name is {target_name}!"
        self.target_files = ReductionFileList.from_list(target_files, filter_names=filter_names)
    
        # find the flat files
        flat_files = glob.glob(os.path.join(self.datadir, f"*{flat_name}*"))
        assert len(flat_files), f"Missing flat files, check the flat_name is {flat_name}!"
        self.flat_files = ReductionFileList.from_list(flat_files, filter_names=filter_names)
        
        # find the bias files
        bias_files = glob.glob(os.path.join(self.datadir, f"*{bias_name}*"))
        assert len(bias_files), f"Missing bias files, check the bias_name is {bias_name}!"
        self.bias_files = ReductionFileList.from_list(bias_files)
        
        # find the dark files
        dark_files = glob.glob(os.path.join(self.datadir, f"*{dark_name}*"))
        assert len(dark_files), f"Missing dark files, check the dark_name is {dark_name}!"
        self.dark_files = ReductionFileList.from_list(dark_files)


def single_dark_calib_stack(exptime_key, files, combined_bias):
    

    darks_calib = [
        ccdp.subtract_bias(CustomCCDData.read(dark_file), combined_bias) 
        for dark_file in files.dark_files["none"] if exptime_key in dark_file
    ]

    combined_dark = ccdp.combine(
        darks_calib,
        **ccdp_combine_kwargs
    )
    
    return combined_dark

def single_flat_calib_and_combine(files, filter_name, combined_darks, exptime):
    
    flats_calib = [
        ccdp.subtract_dark(
            CustomCCDData.read(file), 
            combined_darks, 
            dark_exposure=exptime, 
            data_exposure=exptime,
        ) for file in files.flat_files[filter_name]
    ]
    
    combined_flat = ccdp.combine(
        flats_calib,
        **ccdp_combine_kwargs
    )
    
    return combined_flat

# this list is modified from the OTTER code I've written to find data for transients
# https://github.com/astro-otter/otter/blob/main/src/otter/util.py#L731
VIZIER_LARGE_CATALOGS = [
    "AC2000.2",
    "AKARI",
    "ASCC-2.5",
    "B/DENIS",
    "CMC14",
    "Gaia-DR1",
    "GLIMPSE",
    "GSC-ACT",
    "GSC1.2",
    "GSC2.2",
    "GSC2.3",
    "HIP",
    "HIP2",
    "IRAS",
    "NOMAD1",
    "PanSTARRS-DR1",
    "PGC",
    "Planck-DR1",
    "PPMX",
    "PPMXL",
    "SDSS-DR12",
    "SDSS-DR7",
    "SDSS-DR9",
    "Tycho-2",
    "UKIDSS",
    "USNO-A2",
    "USNO-B1",
]
