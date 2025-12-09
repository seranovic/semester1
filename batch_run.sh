#! /usr/bin/env bash

prefix="pow9pow21"
batches=3
backends=("gamdpy" "gamdpy -a" "lammps" "lammps -g")

for b in "${backends[@]}"; do
    for i in $(seq 1 $batches); do
        python3 main.py -p "$prefix-$i" $b
        if ! [[ $b == "${backends[@]: -1}" && $i -eq $batches ]]; then
            sleep 30
        fi
    done
done
