import sys
import time
from typing import Callable

import numpy as np
from lammps import lammps


def setup_lennard_jones_system(lmp: Callable, nx: int, ny: int, nz: int) -> None:
    """
    Set configuration commands for LJ benchmark
    """

    config = f"""
    units           lj
    atom_style      atomic

    lattice         fcc 0.8442
    region          box block 0 {nx} 0 {ny} 0 {nz}
    create_box      1 box
    create_atoms    1 box
    mass            1 1.0

    velocity        all create 1.44 87287 loop geom

    pair_style      lj/cut 2.5
    pair_coeff      1 1 1.0 1.0 2.5

    neighbor        0.3 bin
    neigh_modify    delay 0 every 20 check no

    fix             1 all nve
    """
    lmp.commands_string(config)


def run_benchmark(lmp: Callable, steps: int) -> int:
    """
    Run benchmark and return elapsed time
    """

    start = time.time()
    lmp.cmd.run(steps)
    elapsed = time.time() - start
    return elapsed


def main(debug: str | None) -> None:
    if debug:
        nxyzs = ((4, 4, 8), (4, 8, 8))
        sleep_time = 5
    else:
        nxyzs = np.genfromtxt("nxyzs.txt", dtype=int, delimiter=",", autostrip=True)
        sleep_time = 15
    nxyzs = ((4, 4, 8), (4, 8, 8))

    target_time_in_sec = 5.0
    magic_number = 1e7

    print("      N      TPS   Steps    Time")

    for nxyz in nxyzs:
        lmp = lammps(cmdargs=["-screen", "none", "-log", "none"])
        setup_lennard_jones_system(lmp, *nxyz)
        N = lmp.get_natoms()
        time_in_sec = 0
        while time_in_sec < target_time_in_sec:
            steps = int(magic_number / N)
            time_in_sec = run_benchmark(lmp, steps)
            magic_number *= (2 * target_time_in_sec) / time_in_sec
        lmp.close()

        tps = steps / time_in_sec
        print(f"{N:7} {tps:.2e} {steps:.1e} {time_in_sec:.1e}")
        print(f"Waiting for {sleep_time} seconds...")
        time.sleep(sleep_time)


if __name__ == "__main__":
    debug = "debug" in sys.argv
    main(debug=debug)
