import os
import sys
import json
import argparse
from multiprocessing import Pool

import numpy as np
import astropy.units as u

import prospect.io.read_results as reader
from prospect.plotting.utils import sample_posterior
from sedpy.observate import load_filters
from prospector_params import build_model, build_sps

# define some global variables
# this is bad practice but should speed stuff up a lot!!
# this is because all this data won't need to be pickled everytime
# _predict_single is called
res = None
model = None
sps = None
new_filts = None

def _predict_single(data):
    '''
    function to enable multiprocessing
    '''

    # unpack inputs
    theta, z = data
    
    spec_wl = (1 + z) * sps.wavelengths
    # Regenerate model spectra from the Prospector result file - spectra
    # are generated in observed frame
    spec, phot, _ = model.predict(theta, obs=res['obs'], sps=sps)
    # Convert from maggies to nJy
    spec, phot = spec * 3631e9, phot * 3631e9
    # Integrate over the new filters to calculate photometry - sedpy takes
    # wavelength in Angstroms and flux in erg / s / cm^2 / A
    obs_flam = (spec * u.nJy).to(u.erg / u.s / u.cm**2 / u.AA,
                                 u.spectral_density(spec_wl * u.AA)).value
    # extract the new photometry
    # convery to nanomaggies
    new_phot = [(filt.ab_mag(spec_wl, obs_flam) * u.ABmag).to(u.nJy).value/3631
                for filt in new_filts]
    
    return phot, new_phot, spec_wl, spec

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_spec', '-n', type=int, default=1000,
                        help='The number of model spectra to generate')
    parser.add_argument('--filts', '-f', nargs='*', help='The filters ' +
                        'for which to calculate photometry')
    parser.add_argument('--prospector_file', '-p', type=str,
                        help='The Prospector result file from which to ' +
                        'get model spectra')
    parser.add_argument('--outdir', '-o', help='full path to output directory',
                        required=False, default=None, type=str)
    parser.add_argument('--mp', '-mp', type=int, help='number of cores to use', default=1,
                        required=False)
    args = parser.parse_args()    
    prospector_file = args.prospector_file

    # use some global variables
    global res
    global model
    global sps
    global new_filts
    
    # Read in the Prospector file and sort out the free parameters
    res, obs, model = reader.results_from(prospector_file)
    free_params = np.array(res.get('theta_labels'))

    # add a param file to the res object
    res['run_params']['param_file'] = 'prospector_params.py'
    
    # Fix the filters so they're compatible with sedpy - you may not need to do
    # this, I have some problem with pickling
    res['obs']['filters'] = load_filters(res['obs']['filternames'])
    
    if model is None:
        res['object_redshift'] = res['obs']['redshift']
        model = build_model(**res) #reader.get_model(res)
    
    # extract the redshift
    if 'zred' in free_params:
        free_z = True
        i_z = np.where(free_params == 'zred')[0][0]
    else:
        free_z = False
        # z = 0 # just find rest values
        z = model.init_config['zred']['init']
    
    # And get the FSPS object
    sps = build_sps(**res) #reader.get_sps(res)

    # Set up the new filters with sedpy so I can calculate photometry
    # First make sure there are no duplicates between the new filters and the
    # filters already in the result file
    new_filts = np.unique(np.setdiff1d(args.filts, res['obs']['filternames']))
    
    # Actually do sedpy now
    new_filts = load_filters(new_filts)

    # Sample some parameter vectors from the chain, generate spectra for
    # each of them with lines, and generate model photometry with sedpy
    thetas = sample_posterior(res.get('chain'),
                              weights=res.get('weights', None),
                              nsample=args.n_spec)

    # Figure out the appropriate redshift to use and redshift the
    # wavelength array

    if free_z:
        zarr = thetas[:,i_z]
    else:
        zarr = [z]*args.n_spec

    # package this data to pass to multiprocessing
    input_data = list(zip(thetas, zarr))

    # multiprocess (or not)
    if args.mp > 1:
        with Pool(args.mp) as p:
            out = p.map(_predict_single, input_data)
    else:
        out = [_predict_single(row) for row in input_data]

    # unpack the outputs
    phot, new_phot, all_spec_wls, all_specs = list(zip(*out))

    phot, new_phot = list(np.array(phot).T), list(np.array(new_phot).T)
    
    all_phot = {filt: [] for filt in res['obs']['filternames'] + args.filts}
    # Add the photometry to the dictionary
    for i, filt in enumerate(res['obs']['filternames']):
        all_phot[filt] = phot[i].tolist()
    for i, filt in enumerate(new_filts):
        all_phot[filt.name] = new_phot[i].tolist()
        
    # compute the u-r color
    all_phot['u_r'] = -np.emath.logn(2.51, np.array(all_phot['sdss_u0']) / np.array(all_phot['sdss_r0']))

    # derive the mean and 1sigma values for each band
    for filt, data in all_phot.items():
        middle = 0.5 
        alpha = 0.682 # 1 sigma
        q1 = np.quantile(data, middle-(alpha/2))
        q2 = np.quantile(data, middle)
        q3 = np.quantile(data, middle+(alpha/2))
        all_phot[filt] = [q2, q3-q2, q2-q1]
        
    # write this out to files
    forfile = all_phot # maybe write other stuff later??

    name = os.path.basename(prospector_file).split('.')[0] 

    if args.outdir is None:
        outdir = os.path.dirname(prospector_file)
    else:
        outdir = args.outdir

    outpath = os.path.join(outdir, name+'.json')
    
    with open(outpath, 'w') as f:
        json.dump(forfile, f, indent=4)
    
if __name__ == '__main__':
    sys.exit(main())
