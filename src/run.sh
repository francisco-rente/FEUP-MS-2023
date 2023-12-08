#!/bin/bash
count=1
for i in "$@"; do
    qsub -l nodes=$i:ppn=2 -d . -l walltime=24:00:00 -F "$# ${count}" run_matrix.sh
    (( count++ ))
done
