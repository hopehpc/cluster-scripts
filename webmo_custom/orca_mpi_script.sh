#!/bin/bash

export OMP_NUM_THREADS=$SLURM_NPROCS    #Orca uses OpenMPI, so OMP_NUM_THREADS needs to be defined
#echo OMP_NUM_THREADS is: $OMP_NUM_THREADS

# Create file with a list of nodes for each processing core
#   If there are N cores, there must be N lines to this file
#   even if all cores are on the same node.
# Assume that we are already in the directory the job will
#   run from.
# Assume that all cores are on a single node. If this is not
#   the case, then just warn user and exit.
#echo SLURM_NNODES is $SLURM_NNODES
if [ $SLURM_NNODES -eq 1 ]
then
  # First put name of node into a new file
  #echo Creating $SLURM_JOB_NAME.nodes file
  echo $SLURM_NODELIST > $SLURM_JOB_NAME.nodes
  # Now append N-1 more copies of that node into the same file
  for ((i=1;i<$SLURM_NPROCS;i++))
  do
    echo $SLURM_NODELIST >> $SLURM_JOB_NAME.nodes
  done
else
  echo The ORCA MPI script is not designed for jobs that
  echo span more than one node. Please restrict your job
  echo to use only a single compute node. You can use 
  echo all of the cores on that node. 
fi

