import asyncio
import time

from lammps import lammps

from .data_structures import ComputePlan, Context


def setup_lennard_jones_system(lmp: lammps, nx: int, ny: int, nz: int) -> None:
    """
    Set configuration commands for LJ benchmark.
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


def run_benchmark(lmp: lammps, steps: int) -> int:
    """
    Run benchmark and return elapsed time.
    """

    start = time.time()
    lmp.cmd.run(steps)
    elapsed = time.time() - start

    return elapsed


async def run_batch(
    ctx: Context,
    systems: list[dict[tuple[int, int, int], ComputePlan]],
    debug: bool = False,
    gpu_accel: bool = False,
) -> None:
    """
    Run batch of benchmarks and save data to shared to state.
    """

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
        lmp = lammps(cmdargs=["-log", "none"])
        await asyncio.to_thread(setup_lennard_jones_system, lmp, *system["nxyz"])
        n_atoms = await asyncio.to_thread(lmp.get_natoms)

        async with ctx.lock:
            d.is_running = True
            d.n_atoms = n_atoms

        time_in_sec = 0
        while time_in_sec < target_time_in_sec:
            steps = int(magic_number / n_atoms)
            time_in_sec = await asyncio.to_thread(run_benchmark, lmp, steps)
            magic_number *= (2 * target_time_in_sec) / time_in_sec
        await asyncio.to_thread(lmp.close)

        async with ctx.lock:
            d.is_running = False
            d.tps = steps / time_in_sec

        await asyncio.sleep(sleep_time)

    ctx.stop_event.set()


if __name__ == "__main__":
    pass
