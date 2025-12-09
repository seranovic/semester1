import asyncio
import time

from .data_structures import ComputePlan, Context


async def setup_lennard_jones_system(
    gpu_accel: bool, nx: int, ny: int, nz: int
) -> tuple[str, int]:
    """
    Return configuration commands for LJ benchmark and number of atoms.
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

    pair_style      lj/cut{"/gpu" if gpu_accel else ""} 2.5
    pair_coeff      1 1 1.0 1.0 2.5

    neighbor        0.3 bin
    neigh_modify    delay 0 every 20 check no

    fix             1 all nve
    """
    n_atoms = 4 * nx * ny * nz

    return config, n_atoms


async def run_benchmark(
    config: str, steps: int, gpu_accel: bool, n_procs: int = 12
) -> int:
    """
    Run benchmark and return elapsed time.
    """

    cmd = [
        "mpirun",
        "-np",
        str(n_procs),
        "lmp",
        "-log",
        "none",
    ]
    if gpu_accel:
        cmd.extend(["-pk", "gpu", "1"])

    config += f"run {steps}"

    start = time.time()
    proc = await asyncio.create_subprocess_exec(*cmd, stdin=asyncio.subprocess.PIPE)
    _, _ = await proc.communicate(config.encode())
    elapsed = time.time() - start

    return elapsed


async def run_batch(
    ctx: Context,
    systems: list[dict[tuple[int, int, int], ComputePlan]],
    debug: bool = False,
    gpu_accel: bool = False,
) -> None:
    """
    Run batch of benchmarks and save data to shared state.
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
        config, n_atoms = await setup_lennard_jones_system(gpu_accel, *system["nxyz"])

        async with ctx.lock:
            d.is_running = True
            d.n_atoms = n_atoms

        time_in_sec = 0
        while time_in_sec < target_time_in_sec:
            steps = int(magic_number / n_atoms)
            time_in_sec = await run_benchmark(config, steps, gpu_accel)
            magic_number *= (2 * target_time_in_sec) / time_in_sec

        async with ctx.lock:
            d.is_running = False
            d.tps = steps / time_in_sec

        await asyncio.sleep(sleep_time)

    ctx.stop_event.set()


if __name__ == "__main__":
    pass
