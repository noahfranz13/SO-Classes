# ASTR513 Term Project
This is the directory holding all of my code for the ASTR513 term project.
The goal of this project was to reproduce the results from
https://doi.org/10.3847/1538-4357/abc258

## Environment Setup
This project uses a conda environment to ensure consistency. Before installing
the conda environment, we need to execute the following commands to install SPS
```
export SPS_HOME="/path/where/you/want/to/download/fsps"
git clone https://github.com/cconroy20/fsps.git $SPS_HOME
```
Then, to create and activate this environment run
```
conda env create -f environment.yml
conda env activate
```
Finally, to ensure we have all of the necessary filter files run
```
CONDAPATH=$(dirname $(dirname $(which conda)))
cp data/filters/*.par $CONDAPATH/lib/python3.11/site-packages/sedpy/data/filters/
```

## Executing the Code
### Running prospector
To run prospector on the arizona HPC just run `./run.sh` from the HPC. Note that if you do not have access to the arizona HPC all of the data is available in
`./data/out/`.

### Extracting the Model Photometry
To extract the photometry from the FSPS model run `./gen_syn_phot.sh` on the arizona HPC. Once again, note that the data exists in `data/model` for those who do not want to wait on the models to generate the photometry again.

### Analysis
All other analysis for my presentation (plots, tables, etc.) is in `analysis.ipynb`.