#!/bin/bash
#SBATCH --job-name=prosp_analysis
#SBATCH --ntasks=20
#SBATCH --nodes=1             
#SBATCH --mem=32gb                    
#SBATCH --time=01:00:00   
#SBATCH --partition=standard
#SBATCH --account=kdalexander
#SBATCH -e %x_%j.err
#SBATCH -o %x_%j.out

module load anaconda
source /home/u7/nfranz/.bashrc
source activate runProspector

python3 get_prospector_spec_phot.py -p $1 -f $(cat syn_bands.txt) --mp $SLURM_NPROCS -o data/model
