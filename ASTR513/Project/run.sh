# run prospector on each object
for name in $(cat data/names.txt);
do
    INPATH=data/hostdata/$name
    OUTPATH=data/out/third_run
    
    echo $INPATH $OUTPATH
    sbatch run_prospector.slurm $INPATH $OUTPATH
done
