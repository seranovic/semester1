import argparse
import asyncio
from io import TextIOWrapper
import multiprocessing
import subprocess
import time
from typing import Callable

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


async def write_to_file(
    stop_event: asyncio.Event, out: TextIOWrapper, measure_func: Callable[None, str]
) -> None:
    """
    Write power draw measurements to file in once per second.

    Format: time,power
        time:   timestamp in seconds
        power:  power draw in watts
    """

    out.write("time,power\n")
    i = 0

    while not stop_event.is_set():
        measurement = await measure_func()
        out.write(f"{i},{measurement}\n")

        # Pause sampling until next second
        t = time.localtime()
        while t.tm_sec == time.localtime().tm_sec and not stop_event.is_set():
            await asyncio.sleep(0.1)

        i += 1


def run_bench() -> None:
    """
    Run benchmarking script. Should be called as a separate process.
    """

    time.sleep(15)  # for measuring pre-benchmark idle power draw
    proc = subprocess.run(
        ["python3", "benchmark_LJ.py", "default"], capture_output=True
    )


async def main(identifier: str) -> None:
    # Start benchmark as its own process
    proc_bench = multiprocessing.Process(target=run_bench)
    proc_bench.start()

    # Stop event for measuring tasks
    stop_event = asyncio.Event()

    # Stream to files
    with (
        open(f"data/{identifier}-gpu.csv", "w", buffering=1) as f_gpu,
        open(f"data/{identifier}-total.csv", "w", buffering=1) as f_total,
    ):

        # Start measurement tasks
        proc_gpu = asyncio.create_task(write_to_file(stop_event, f_gpu, measure_gpu))
        proc_total = asyncio.create_task(
            write_to_file(stop_event, f_total, measure_total)
        )

        # Stop measurement tasks when benchmark has concluded
        while proc_bench.is_alive():
            await asyncio.sleep(0.5)
        stop_event.set()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "id",
        type=str,
        nargs="?",
        metavar="identifier",
        default="default",
        help="identifier for this run (will overwrite data if not unique)",
    )
    args = p.parse_args()

    asyncio.run(main(identifier=args.id))
