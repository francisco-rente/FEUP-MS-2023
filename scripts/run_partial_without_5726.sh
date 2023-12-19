#!/bin/bash
set -o xtrace
count=1
for i in "$@"; do
    qsub -l nodes=$i:ppn=2 -d . -l walltime=24:00:00 -F "$# ${count} 5726" run_partial_adjacency_matrix.sh
    (( count++ ))
done
