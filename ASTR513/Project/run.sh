for name in $(cat data/names.txt);
do
    INPATH=data/hostdata/$name
    FILE=$(basename -- $INPATH)
    OUTFILENAME="${FILE%.*}.h5"
    OUTPATH="data/out/${OUTFILENAME}"
    
    echo $INPATH $OUTPATH
    sbatch run_prospector.slurm $INPATH $OUTPATH
done
