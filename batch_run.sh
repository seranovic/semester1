#! /usr/bin/env bash

prefix="pow9pow21"
batches=3
backends=("gamdpy" "gamdpy -a" "lammps")

for b in "${backends[@]}"; do
    for i in {1..$batches}; do
        python3 main.py -p "$prefix-$i" $b
        if ! [[ $b == "${backends[-1]}" && $i -eq 3 ]]; then
            sleep 30
        fi
    done
done
