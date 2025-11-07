import argparse
import asyncio
import multiprocessing
import subprocess
import sys
import time

from ENG110_python import get_eng110_data


async def measure_total(samples: int) -> str:
    """
    Returns measurements from ENG110 power meter as a csv-formatted string. Includes
    power readings (W) and timestamp sampled once per second.

    Format: time (HH:MM:SS), power draw (W)
    """

    csv = ""

    for _ in range(samples):
        p = get_eng110_data()
        t = time.localtime()

        csv += "{}:{}:{},{:.2f}\n".format(
            str(t.tm_hour).zfill(2),
            str(t.tm_min).zfill(2),
            str(t.tm_sec).zfill(2),
            p[2],
        )

        while t.tm_sec == time.localtime().tm_sec:  # while time is same waits 0.1 secs
            await asyncio.sleep(0.1)

    return csv


async def measure_gpu(samples: int) -> str:
    """
    Runs nvidia-smi and returns measurements as csv-formatted string.

    Format: time (HH:MM:SS), gpu id, power draw (W), gtemp (C), mtemp (C)
    """

    proc = await asyncio.create_subprocess_shell(
        f"nvidia-smi dmon -i 0 -s p -o T --format=csv,nounit,noheader -c {samples}",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    csv = stdout.decode().replace(" ", "")

    return csv


def run_bench() -> None:
    """
    Run benchmarking script. Should be called as a separate process.
    """

    time.sleep(15)  # for measuring pre-benchmark idle power draw
    proc = subprocess.run(
        [
            "python3",
            "benchmark_LJ.py",
            "default",
        ],
        capture_output=True,
    )


async def main(samples: int, identifier: str) -> None:
    # Start benchmark as its own process
    proc_bench = multiprocessing.Process(target=run_bench)
    proc_bench.start()

    # Start measurement tools
    asyncio.create_task(measure_gpu(samples))
    asyncio.create_task(measure_total(samples))

    # Wait for measurements to be done
    proc_gpu, proc_total = await asyncio.gather(
        measure_gpu(samples), measure_total(samples)
    )

    # Wait for benchmark to be done
    while proc_bench.is_alive():
        await asyncio.sleep(0.5)
    proc_bench.join()

    # Save data to files
    with open(f"csv/{identifier}-gpu.csv", "w") as f:
        f.write("time,gpu,power,gtemp,mtemp\n" + proc_gpu)
    with open(f"csv/{identifier}-total.csv", "w") as f:
        f.write("time,power\n" + proc_total)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "-i",
        "--id",
        type=str,
        nargs="?",
        default="default",
        metavar="name",
        help="unique identifier for this run",
    )
    p.add_argument(
        "-s",
        "--samples",
        type=int,
        nargs="?",
        default=435,
        metavar="n",
        help="amount of samples to run (1 sample/sec)",
    )
    args = p.parse_args()

    if args.samples <= 0:
        p.print_help()
        sys.exit(1)

    asyncio.run(main(samples=args.samples, identifier=args.id))
