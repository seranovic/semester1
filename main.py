import argparse
import asyncio
import io
import multiprocessing
import subprocess
import time

from ENG110_python import get_eng110_data


async def measure_total(stop_event: asyncio.Event, f: io.TextIOWrapper) -> None:
    """
    Get power draw measurements from ENG110 power meter and write to file in csv-format.

    Format: time (s), power draw (W)
    """

    f.write("time,power\n")
    i = 1

    while not stop_event.is_set():
        p = get_eng110_data()
        t = time.localtime()

        f.write("{},{:.2f}\n".format(i, p[2]))

        # Pause sampling until next second
        while t.tm_sec == time.localtime().tm_sec and not stop_event.is_set():
            await asyncio.sleep(0.1)

        i += 1


async def measure_gpu(stop_event: asyncio.Event, f: io.TextIOWrapper) -> None:
    """
    Get power draw measurements from nvidia-smi and write to file in csv-format.

    Format: time (s), power draw (W)
    """

    f.write("time,power\n")
    i = 1

    while not stop_event.is_set():
        proc = await asyncio.create_subprocess_shell(
            f"nvidia-smi -i 0 --query-gpu=power.draw --format=csv,nounits,noheader",
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        t = time.localtime()

        f.write("{},{}".format(i, stdout.decode()))

        # Pause sampling until next second
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
        proc_gpu = asyncio.create_task(measure_gpu(stop_event, f_gpu))
        proc_total = asyncio.create_task(measure_total(stop_event, f_total))

        # Stop measurement tasks when benchmark has concluded
        while proc_bench.is_alive():
            await asyncio.sleep(0.5)
        stop_event.set()

        # Wait for measurement tasks
        await asyncio.gather(proc_gpu, proc_total)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "-i",
        "--id",
        type=str,
        nargs="?",
        metavar="string",
        default="default",
        help="identifier for this run (will overwrite data if not unique)",
    )
    args = p.parse_args()

    asyncio.run(main(identifier=args.id))
