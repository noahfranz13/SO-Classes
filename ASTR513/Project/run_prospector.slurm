#!/bin/bash
#SBATCH --job-name=prospector_%j
#SBATCH --ntasks=1
#SBATCH --nodes=1             
#SBATCH --mem=32gb                    
#SBATCH --time=00:30:00   
#SBATCH --partition=standard
#SBATCH --account=kdalexander
#SBATCH -e %j.err
#SBATCH -o %j.out

python3 run_prospector.py --file $1
