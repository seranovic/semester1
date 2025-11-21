import argparse
import asyncio
import os
import subprocess
import time
from io import TextIOWrapper

from ENG110_python import get_eng110_data


async def measure_total() -> str:
    """
    Get power draw measurement from ENG110 power meter.
    """

    measurement = "{:.2f}".format(get_eng110_data()[2])

    return measurement


async def measure_gpu() -> str:
    """
    Get power draw measurement from nvidia-smi.
    """

    proc = await asyncio.create_subprocess_shell(
        "nvidia-smi -i 0 --query-gpu=power.draw --format=csv,nounits,noheader",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    measurement = stdout.decode().replace("\n", "")

    return measurement


async def write_to_file(stop_event: asyncio.Event, out: TextIOWrapper) -> None:
    """
    Write power draw measurements to file once per second.

    Format: time,gpu,total
        time:   timestamp in seconds
        gpu:    gpu power draw in watts
        total:  total power draw in watts
    """

    out.write("time,gpu,total\n")
    i = 0  # tick counter
    dt = 1  # tick rate in seconds
    t_start = time.time()

    while not stop_event.is_set():
        t_sched = t_start + i * dt  # scheduled measurement

        gpu, total = await asyncio.gather(measure_gpu(), measure_total())
        out.write(f"{int(t_sched-t_start)},{gpu},{total}\n")

        # Pause sampling for dt seconds
        t_current = time.time()
        t_next = t_sched + dt  # next measurement
        t_sleep = t_next - t_current
        if t_sleep > 0 and not stop_event.is_set():
            await asyncio.sleep(t_sleep)

        i += 1


async def run_gamdpy_bench(autotuner: bool) -> None:
    """
    Run gamdpy benchmarking script.
    """

    command = ["python3", "benchmark_gamdpy.py"]
    if autotuner:
        command.append("autotuner")

    await asyncio.sleep(15)  # for measuring pre-benchmark idle power draw
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()


async def run_lammps_bench() -> None:
    """
    Run lammps benchmarking script.
    """

    command = ["python3", "benchmark_lammps.py"]

    await asyncio.sleep(15)  # for measuring pre-benchmark idle power draw
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()


async def main(args) -> None:
    identifier = args.id
    backend = ""
    autotuner = False

    if args.backend == "gamdpy":
        backend = "gamdpy"
        if args.autotuner:
            autotuner = True
    else:
        backend = "lammps"

    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filename = f"{identifier}-{backend}"
    if autotuner:
        filename += "-at"

    # Stream to file
    with open(f"{data_dir}/{filename}.csv", "w", buffering=1) as f:

        # Stop event for measuring tasks
        stop_event = asyncio.Event()

        # Start writing measurements to disk
        task_measure = asyncio.create_task(write_to_file(stop_event, f))

        # Start benchmark
        if backend == "gamdpy":
            proc_bench = asyncio.create_task(run_gamdpy_bench(autotuner=autotuner))
        else:
            proc_bench = asyncio.create_task(run_lammps_bench())

        # Stop measurement tasks when benchmark has concluded
        await proc_bench
        stop_event.set()
        await task_measure


if __name__ == "__main__":
    # Top level parser
    p = argparse.ArgumentParser()
    p.add_argument(
        "-i",
        "--id",
        type=str,
        # nargs=1,
        metavar="identifier",
        required=True,
        help="identifier for this run (will overwrite data if not unique)",
    )
    # TODO: add debug flag for small system size runs
    sub_ps = p.add_subparsers(required=True, dest="backend")

    # gamdpy parser
    p_gamdpy = sub_ps.add_parser("gamdpy")
    p_gamdpy.add_argument(
        "-a",
        "--autotuner",
        action="store_true",
        help="use autotuner",
    )

    # lammps parser
    p_lammps = sub_ps.add_parser("lammps")
    # TODO: add gpu-accel flag

    args = p.parse_args()

    asyncio.run(main(args))
