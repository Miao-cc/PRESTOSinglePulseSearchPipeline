#!/bin/bash
#SBATCH --job-name=PSPSP
#SBATCH -p q30
#SBATCH -n 72
##SBATCH -N 1
#SBATCH --output=a.err
#SBATCH --error=a.out

echo -e "JOB NAME:$SLURM_JOB_NAME,Job ID:$SLURM_JOBID,Allocate Nodes:$SLURM_JOB_NODELIST"

## combie fits
sh combineFile.sh

## single pulse search
lowDM=500
highDM=640
DMstep=0.5
filename=haha.fits
python singlePulseSearch.py ${filename} ${lowDM} ${highDM} ${DMstep}
