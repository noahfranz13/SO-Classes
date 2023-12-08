#!/bin/bash
#SBATCH --job-name=prospect
#SBATCH --ntasks=1
#SBATCH --nodes=1             
#SBATCH --mem=32gb                    
#SBATCH --time=24:00:00   
#SBATCH --partition=standard
#SBATCH --account=kdalexander
#SBATCH -e %x_%j.err
#SBATCH -o %x_%j.out

module load anaconda 
source /home/u7/nfranz/.bashrc
source activate runProspector

python3 run_prospector.py --file $1 --outdir $2 --niters 10000
