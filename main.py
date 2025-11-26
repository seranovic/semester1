import argparse
import asyncio
import sys

from bp1 import benchmarking
from bp1.data_structures import Context
from bp1.measuring import measure_gpu, measure_total
from bp1.writing import write_to_csv


def parse_args() -> argparse.Namespace:
    # Top level parser
    p = argparse.ArgumentParser()
    p.add_argument(
        "-p",
        "--prefix",
        type=str,
        nargs="?",
        help="identifying prefix for this run (can overwrite data if not unique)",
    )
    # p.add_argument(
    #     "-v",
    #     "--verbose",
    #     action="store_true",
    #     help="increase output verbosity",
    # )
    p.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="run benchmark with small system sizes (~30-60 seconds per run)",
    )
    sub_ps = p.add_subparsers(
        required=True,
        dest="backend",
        help="backend",
    )

    # gamdpy parser
    # p_gamdpy = sub_ps.add_parser("gamdpy")
    # p_gamdpy.add_argument(
    #     "-a",
    #     "--autotune",
    #     action="store_true",
    #     help="enable autotuning",
    # )

    # lammps parser
    p_lammps = sub_ps.add_parser("lammps")
    # p_gamdpy.add_argument(
    #     "-g",
    #     "--gpu",
    #     action="store_true",
    #     help="enable GPU-acceleration",
    # )

    args = p.parse_args()

    if not args.prefix and not args.debug:
        print("Error: specify identifier or debug mode")
        sys.exit(1)

    if args.debug:
        args.prefix = "debug"
        # args.verbose = True

    return args


async def main(args: argparse.Namespace) -> None:
    ctx = Context()

    tasks = [
        asyncio.create_task(benchmarking.run_batch(ctx, debug=args.debug)),
        asyncio.create_task(measure_gpu(ctx)),
        asyncio.create_task(measure_total(ctx)),
        asyncio.create_task(
            write_to_csv(
                ctx,
                prefix=args.prefix,
                backend=args.backend,
            )
        ),
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
