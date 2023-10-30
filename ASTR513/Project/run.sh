for name in $(cat data/names.txt);
do
    PATH=data/hostdata/$name
    sbatch run_prospector.slurm $PATH
done
