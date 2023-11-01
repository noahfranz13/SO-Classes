#!/bin/bash
#SBATCH --job-name=prospector_%j
#SBATCH --ntasks=1
#SBATCH --nodes=1             
#SBATCH --mem=32gb                    
#SBATCH --time=01:00:00   
#SBATCH --partition=standard
#SBATCH --account=kdalexander
#SBATCH -e %j.err
#SBATCH -o %j.out

python3 get_prospector_spec_phot.py -p $1 -f $(cat syn_bands.txt) --mp 20 -o data/model
