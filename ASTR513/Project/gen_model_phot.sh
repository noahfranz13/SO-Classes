#!/bin/bash

for f in data/out/*.h5
do
    sbatch gen_model_phot.slurm $f
done
