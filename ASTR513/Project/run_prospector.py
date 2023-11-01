'''
Script to run prospector on a give json file
'''
import os, sys, glob, json, time
from multiprocessing import Pool, cpu_count
import numpy as np
import pandas as pd
import argparse
from prospect.models.templates import TemplateLibrary
from prospect.models import priors, sedmodel
from prospect.utils.obsutils import fix_obs
from prospect.fitting import fit_model
from prospect.io import write_results as writer
from sedpy.observate import Filter, load_filters

from prospector_params import *

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', required=True)
    p.add_argument('--outfile', required=False, default=None)
    p.add_argument('--niters', required=False, default=500)
    p.add_argument('--mp', dest='mp', action='store_true')
    p.set_defaults(mp=False)
    args = p.parse_args()

    # read in the file
    with open(args.file, 'r') as f:
        j = json.load(f)

    # prep to run prospector
    tdename = args.file.split('/')[-1].split('.')[0]
    
    params = {
        # general parameters
        'verbose': True,
        'data':j,
        'tdename': tdename,
        # for emcee
        'nwalkers': 100,
        'nburn': [500],
        'niter': args.niters,
    }
    
    obs, model, sps, noise = build_all(**params)

    if args.outfile is None:
        outpath = args.file.split('.')[0] + '.h5'
    else:
        outpath = args.outfile

    print(model)
        
    # run prospector
    if args.mp:
        print('using mp')
        with Pool() as pool:
            output = fit_model(obs, model, sps, noise, dynesty=False, emcee=True, pool=pool, **params)  
    else:
        print('not using mp')
        output = fit_model(obs, model, sps, noise, dynesty=False, emcee=True, **params)  
    
    ts = time.strftime("%y%b%d-%H.%M", time.localtime())
    hfile = "{0}_{1}_result.h5".format(tdename, ts)

    writer.write_hdf5(hfile, params, model, obs,
                      output["sampling"][0], output["optimization"][0],
                      tsample=output["sampling"][1],
                      toptimize=output["optimization"][1],
                      sps=sps)

if __name__ == '__main__':
    sys.exit(main())
