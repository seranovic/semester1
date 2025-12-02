"""
Benchmark gamdpy using the lammps LJ benchmark
Command line options:

- Nsquared : Use O(N^2) for neighbor-list update (Default)
- LinkedLists : Use O(N) linked lists for neighbor-list update

- NVE : Use NVE integrator (default)
- NVT : Use NVT integrator
- NVT_Langevin : Use NVT_Langevin integrator

"""

import asyncio
import glob
import sys

# from gamdpy.integrators import nve, nvt_nh, nvt_langevin  # OLD CODE

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import numba
from numba import cuda, config

import gamdpy as gp
import pickle
import time

from .data_structures import ComputePlan, Context


def setup_lennard_jones_system(nx, ny, nz, rho=0.8442, cut=2.5, verbose=False):
    """
    Setup and return configuration, potential function, and potential parameters for the LJ benchmark
    """

    # Generate configuration with a FCC lattice
    # Setup configuration: FCC Lattice
    c1 = gp.Configuration(D=3)
    c1.make_lattice(gp.unit_cells.FCC, cells=[nx, ny, nz], rho=rho)
    c1["m"] = 1.0
    c1.randomize_velocities(temperature=1.44)
    #  c1 = gp.make_configuration_fcc(nx=nx,  ny=ny,  nz=nz,  rho=rho, T=1.44)

    # Setup pair potential.
    # pair_func = gp.apply_shifted_force_cutoff(rp.LJ_12_6_sigma_epsilon)
    pair_func = gp.apply_shifted_potential_cutoff(gp.LJ_12_6_sigma_epsilon)
    sig, eps, cut = 1.0, 1.0, 2.5
    pair_pot = gp.PairPotential(pair_func, params=[sig, eps, cut], max_num_nbs=500)

    return c1, pair_pot


def run_benchmark(
    c1, pair_pot, compute_plan, steps, integrator="NVE", autotune=False, verbose=False
):
    """
    Run LJ benchmark
    Could be run with other potential and/or parameters, but asserts would need to be updated
    """

    # Set up the integrator
    dt = 0.005

    if integrator == "NVE":
        integrator = gp.integrators.NVE(dt=dt)
    if integrator == "NVT":
        integrator = gp.integrators.NVT(temperature=0.70, tau=0.2, dt=dt)
    if integrator == "NVT_Langevin":
        integrator = gp.integrators.NVT_Langevin(
            temperature=0.70, alpha=0.2, dt=dt, seed=213
        )

    # Setup Simulation. Total number of timesteps: num_blocks * steps_per_block
    sim = gp.Simulation(
        c1,
        pair_pot,
        integrator,
        [
            gp.MomentumReset(100),
        ],
        num_timeblocks=1,
        steps_per_timeblock=steps,
        compute_plan=compute_plan,
        storage="memory",
    )

    # Run simulation one block at a time
    for block in sim.run_timeblocks():
        pass

    if autotune:
        # sim.autotune_bruteforce(verbose=False)
        sim.autotune()

    nbflag0 = pair_pot.nblist.d_nbflag.copy_to_host()
    for block in sim.run_timeblocks():
        pass

    # print(sim.summary())

    # assert 0.55 < Tkin < 0.85, f'{Tkin=}'
    # assert 0.55 < Tconf < 0.85, f'{Tconf=}'
    # if integrator == 'NVE':  # Only expect conservation of energy if we are running NVE
    #    assert -0.01 < de < 0.01

    tps = (
        sim.last_num_blocks
        * sim.steps_per_block
        / np.sum(sim.timing_numba_blocks)
        * 1000
    )
    time_in_sec = sim.timing_numba / 1000

    nbflag = pair_pot.nblist.d_nbflag.copy_to_host()
    nbupdates = nbflag[2] - nbflag0[2]
    print(
        f"{c1.N:7} {tps:.2e} {steps:.1e} {time_in_sec:.1e}  {nbupdates:6} {steps/nbupdates:.1f} {sim.compute_plan}"
    )
    assert nbflag[0] == 0
    assert nbflag[1] == 0
    return tps, time_in_sec, steps, sim.compute_plan.copy()


async def run_batch(
    ctx: Context,
    systems: list[dict[tuple[int, int, int], ComputePlan]],
    debug: bool = False,
    autotune: bool = False,
) -> None:
    """
    Run batch of benchmarks and save data to shared to state.
    """

    config.CUDA_LOW_OCCUPANCY_WARNINGS = False

    integrator = "NVE"
    nblist = "default"

    if debug:
        sleep_time = 5
        target_time_in_sec = 5.0
    else:
        sleep_time = 15
        target_time_in_sec = 10.0

    await asyncio.sleep(sleep_time)

    magic_number = 1e7

    d = ctx.power_data

    for system in systems:
        c1, LJ_func = await asyncio.to_thread(
            setup_lennard_jones_system, *system["nxyz"], cut=2.5, verbose=False
        )

        async with ctx.lock:
            d.is_running = True
            d.n_atoms = c1.N

        time_in_sec = 0
        while time_in_sec < target_time_in_sec:
            steps = int(magic_number / c1.N)
            if autotune:
                compute_plan = system["compute_plan"]
            else:
                compute_plan = await asyncio.to_thread(gp.get_default_compute_plan, c1)
            tps, time_in_sec, steps, _ = await asyncio.to_thread(
                run_benchmark,
                c1,
                LJ_func,
                compute_plan,
                steps,
                integrator=integrator,
                verbose=False,
            )
            magic_number *= (2 * target_time_in_sec) / time_in_sec

        async with ctx.lock:
            d.is_running = False
            d.tps = tps

        await asyncio.sleep(sleep_time)

    ctx.stop_event.set()


if __name__ == "__main__":
    pass
