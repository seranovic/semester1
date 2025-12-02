import asyncio

import gamdpy as gp
import numba
import numpy as np
from numba import cuda, config

from .data_structures import ComputePlan, Context


def setup_lennard_jones_system(
    nx: int, ny: int, nz: int
) -> tuple[gp.Configuration, gp.PairPotential]:
    """
    Setup and return configuration and potential function for the LJ benchmark.
    """

    # Generate configuration with a FCC lattice
    c1 = gp.Configuration(D=3)
    c1.make_lattice(gp.unit_cells.FCC, cells=[nx, ny, nz], rho=0.8442)
    c1["m"] = 1.0
    c1.randomize_velocities(temperature=1.44)

    # Setup pair potential
    pair_func = gp.apply_shifted_potential_cutoff(gp.LJ_12_6_sigma_epsilon)
    sig, eps, cut = 1.0, 1.0, 2.5
    pair_pot = gp.PairPotential(pair_func, params=[sig, eps, cut], max_num_nbs=500)

    return c1, pair_pot


def run_benchmark(
    c1: gp.Configuration,
    pair_pot: gp.PairPotential,
    compute_plan: ComputePlan,
    steps: int,
) -> tuple[float, float, int]:
    """
    Run LJ benchmark and return elapsed time and timesteps.
    """

    # Set up the integrator
    integrator = gp.integrators.NVE(dt=0.005)

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

    nbflag0 = pair_pot.nblist.d_nbflag.copy_to_host()
    for block in sim.run_timeblocks():
        pass

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
    return tps, time_in_sec, steps


async def run_batch(
    ctx: Context,
    systems: list[dict[tuple[int, int, int], ComputePlan]],
    debug: bool = False,
    autotune: bool = False,
) -> None:
    """
    Run batch of benchmarks and save data to shared state.
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
            setup_lennard_jones_system, *system["nxyz"]
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
            tps, time_in_sec, steps = await asyncio.to_thread(
                run_benchmark, c1, LJ_func, compute_plan, steps
            )
            magic_number *= (2 * target_time_in_sec) / time_in_sec

        async with ctx.lock:
            d.is_running = False
            d.tps = tps

        await asyncio.sleep(sleep_time)

    ctx.stop_event.set()


if __name__ == "__main__":
    pass
