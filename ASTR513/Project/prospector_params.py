'''
Param functions for prospector
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

def build_model(object_redshift=None, fixed_metallicity=None, add_duste=False,
                add_neb=False, luminosity_distance=0.0, **extras):
    """Construct a model.  This method defines a number of parameter
    specification dictionaries and uses them to initialize a
    `models.sedmodel.SedModel` object.

    :param object_redshift:
        If given, given the model redshift to this value.

    :param add_dust: (optional, default: False)
        Switch to add (fixed) parameters relevant for dust emission.

    :param add_neb: (optional, default: False)
        Switch to add (fixed) parameters relevant for nebular emission, and
        turn nebular emission on.

    :param luminosity_distance: (optional)
        If present, add a `"lumdist"` parameter to the model, and set it's
        value (in Mpc) to this.  This allows one to decouple redshift from
        distance, and fit, e.g., absolute magnitudes (by setting
        luminosity_distance to 1e-5 (10pc))
    """
    if object_redshift is None:
        raise ValueError('object_redshift is missing!!')
    
    # --- Get a basic delay-tau SFH parameter set. ---
    # This has 5 free parameters:
    #   "mass", "logzsol", "dust2", "tage", "tau"
    # And two fixed parameters
    #   "zred"=0.1, "sfh"=4
    # See the python-FSPS documentation for details about most of these
    # parameters.  Also, look at `TemplateLibrary.describe("parametric_sfh")` to
    # view the parameters, their initial values, and the priors in detail.
    model_params = TemplateLibrary["parametric_sfh"]

    # use Chabrier IMF instead of The default Kroupa IMF
    model_params['imf_type']['init'] = 1 # default is 2, we want 1

    # Use the Calzetti et al. dust model
    model_params['dust_type']['init'] = 2 # default is 0, calzetti is 2
        
    # Add lumdist parameter.  If this is not added then the distance is
    # controlled by the "zred" parameter and a WMAP9 cosmology.
    if luminosity_distance > 0:
        model_params["lumdist"] = {"N": 1, "isfree": False,
                                   "init": luminosity_distance, "units":"Mpc"}

    # Adjust model initial values (only important for optimization or emcee)
    model_params["dust2"]["init"] = 0.9
    model_params["logzsol"]["init"] = -1.7
    model_params["tage"]["init"] = 0.2
    model_params["mass"]["init"] = 1e9
    model_params["tau"]["init"] = 1e-1

    # give it a redshift
    model_params["zred"]['isfree'] = False
    model_params["zred"]['init'] = object_redshift
    
    # If we are going to be using emcee, it is useful to provide an
    # initial scale for the cloud of walkers (the default is 0.1)
    # For dynesty these can be skipped
    model_params["mass"]["init_disp"] = 1e7
    model_params["tau"]["init_disp"] = 1
    model_params["tage"]["init_disp"] = 1
    model_params["dust2"]["init_disp"] = 0.1
    model_params["logzsol"]["init_disp"] = 0.1

    # adjust priors
    model_params["tage"]["prior"] = priors.LogUniform(mini=(1e8/1e9), maxi=(10**(10.1)/1e9)) # 0.1 to 12.6 Gyr
    model_params["dust2"]["prior"] = priors.TopHat(mini=0.0, maxi=1.0)
    model_params["tau"]["prior"] = priors.LogUniform(mini=1e-1, maxi=1e1) # 0.1 - 10 Gyr
    model_params["mass"]["prior"] = priors.LogUniform(mini=1e8, maxi=1e12)
    model_params["logzsol"]["prior"] = priors.TopHat(mini=-1.8, maxi=0.2)

    # Change the model parameter specifications based on some keyword arguments
    if fixed_metallicity is not None:
        # make it a fixed parameter
        model_params["logzsol"]["isfree"] = False
        #And use value supplied by fixed_metallicity keyword
        model_params["logzsol"]['init'] = fixed_metallicity

    if object_redshift != 0.0:
        # make sure zred is fixed
        model_params["zred"]['isfree'] = False
        # And set the value to the object_redshift keyword
        model_params["zred"]['init'] = object_redshift

    if add_duste:
        # Add dust emission (with fixed dust SED parameters)
        model_params.update(TemplateLibrary["dust_emission"])

    if add_neb:
        # Add nebular emission (with fixed parameters)
        model_params.update(TemplateLibrary["nebular"])

    # Now instantiate the model using this new dictionary of parameter specifications
    model = sedmodel.SpecModel(model_params)

    return model

def build_obs(data, tdename=None, **extras):
    """Load photometry from an ascii file.  Assumes the following columns:
    `objid`, `filterset`, [`mag0`,....,`magN`] where N >= 11.  The User should
    modify this function (including adding keyword arguments) to read in their
    particular data format and put it in the required dictionary.

    :param objid:
        The object id for the row of the photomotery file to use.  Integer.
        Requires that there be an `objid` column in the ascii file.

    :param phottable:
        Name (and path) of the ascii file containing the photometry.

    :param luminosity_distance: (optional)
        The Johnson 2013 data are given as AB absolute magnitudes.  They can be
        turned into apparent magnitudes by supplying a luminosity distance.

    :returns obs:
        Dictionary of observational data.
    """
    
    # Build output dictionary.
    obs = {}
    # This is a list of sedpy filter objects.    See the
    # sedpy.observate.load_filters command for more details on its syntax.
    obs['filters'] = load_filters(data['filternames'])
    # This is a list of maggies, converted from mags.  It should have the same
    # order as `filters` above.
    obs['maggies'] = np.array(data['maggies'])
    # HACK.  You should use real flux uncertainties
    obs['maggies_unc'] = np.array(data['maggies_unc'])
    # Here we mask out any NaNs or infs
    obs['phot_mask'] = np.array(data['photmask'])
    # We have no spectrum.
    obs['wavelength'] = None
    obs['spectrum'] = None

    # Add unessential bonus info.  This will be stored in output
    #obs['dmod'] = catalog[ind]['dmod']
    obs['objid'] = tdename

    # This ensures all required keys are present and adds some extra useful info
    obs = fix_obs(obs)

    return obs

def build_sps(zcontinuous=1, compute_vega_mags=False, **extras):
    from prospect.sources import CSPSpecBasis
    sps = CSPSpecBasis(zcontinuous=zcontinuous,
                       compute_vega_mags=compute_vega_mags,
                       **extras)
    return sps

def build_noise(**extras):
    return None, None

def build_all(**kwargs):

    return (build_obs(**kwargs), build_model(**kwargs),
            build_sps(**kwargs), build_noise(**kwargs))
