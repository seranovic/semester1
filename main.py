import argparse
import asyncio
import os
import subprocess
import sys
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


async def run_bench(backend: str, debug: bool, autotuner: bool) -> None:
    """
    Run benchmarking script.
    """

    command = ["python3", f"benchmark_{backend}.py"]

    if debug:
        command.append("debug")
        sleep_time = 5
        stdout = None
        stderr = None
    else:
        sleep_time = 15
        stdout = asyncio.subprocess.PIPE
        stderr = asyncio.subprocess.PIPE

    if autotuner:
        command.append("autotuner")

    if debug:
        print(f"Waiting for {sleep_time} seconds...")
    await asyncio.sleep(sleep_time)  # for measuring pre-benchmark idle power draw

    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=stdout,
        stderr=stdout,
    )
    await proc.communicate()


async def main(args) -> None:
    identifier = args.id
    backend = ""
    debug = False
    autotuner = False

    if args.backend == "gamdpy":
        backend = "gamdpy"
        if args.autotuner:
            autotuner = True
    else:
        backend = "lammps"

    if args.debug:
        debug = True

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
        proc_bench = asyncio.create_task(
            run_bench(backend=backend, debug=debug, autotuner=autotuner)
        )

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
        nargs="?",
        metavar="identifier",
        help="identifier for this run (will overwrite data if not unique)",
    )
    p.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="run benchmark with small system sizes (~30-60 seconds per run)",
    )
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

    if not args.id and not args.debug:
        print("Error: specify identifier or debug mode")
        sys.exit(1)

    if args.debug:
        args.id = "debug"

    asyncio.run(main(args))
