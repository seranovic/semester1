import argparse
import asyncio
import sys

import pandas as pd

from bp1 import benchmark_gamdpy, benchmark_lammps, ComputePlan, Context
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
    p_gamdpy = sub_ps.add_parser("gamdpy")
    p_gamdpy.add_argument(
        "-a",
        "--autotune",
        action="store_true",
        help="use autotuned compute plans",
    )

    # lammps parser
    p_lammps = sub_ps.add_parser("lammps")
    p_lammps.add_argument(
        "-g",
        "--gpu",
        action="store_true",
        help="enable GPU-acceleration",
    )

    args = p.parse_args()

    if not args.prefix and not args.debug:
        print("Error: specify prefix")
        sys.exit(1)

    if args.debug:
        args.prefix = "debug"

    return args


async def main(args: argparse.Namespace) -> None:
    ctx = Context()

    autotune = False
    gpu_accel = False

    if hasattr(args, "autotune"):
        autotune = args.autotune

    if hasattr(args, "gpu"):
        gpu_accel = args.gpu

    compute_plans: list[ComputePlan] = pd.read_csv(
        "at_compute_plans.csv",
        dtype={
            "n": int,
            "pb": int,
            "tp": int,
            "skin": float,
            "UtilizeNIII": bool,
            "gridsync": bool,
            "nblist": str,
        },
        index_col="n",
    ).to_dict(orient="records")

    systems: list[dict[tuple[int, int, int], ComputePlan]] = [
        {"nxyz": (4, 4, 8), "compute_plan": compute_plans[0]},
        {"nxyz": (4, 8, 8), "compute_plan": compute_plans[1]},
    ]
    if not args.debug:
        systems.extend(
            [
                {"nxyz": (8, 8, 8), "compute_plan": compute_plans[2]},
                {"nxyz": (8, 8, 16), "compute_plan": compute_plans[3]},
                {"nxyz": (8, 16, 16), "compute_plan": compute_plans[4]},
                {"nxyz": (16, 16, 16), "compute_plan": compute_plans[5]},
                {"nxyz": (16, 16, 32), "compute_plan": compute_plans[6]},
                {"nxyz": (16, 32, 32), "compute_plan": compute_plans[7]},
                {"nxyz": (32, 32, 32), "compute_plan": compute_plans[8]},
                {"nxyz": (32, 32, 64), "compute_plan": compute_plans[9]},
                {"nxyz": (32, 64, 64), "compute_plan": compute_plans[10]},
                {"nxyz": (64, 64, 64), "compute_plan": compute_plans[11]},
                {"nxyz": (64, 64, 128), "compute_plan": compute_plans[12]},
                # out of memory error when run with higher system sizes
            ]
        )

    async with asyncio.TaskGroup() as tg:
        if args.backend == "lammps":
            tg.create_task(
                benchmark_lammps.run_batch(
                    ctx, systems=systems, debug=args.debug, gpu_accel=gpu_accel
                )
            )
        else:
            tg.create_task(
                benchmark_gamdpy.run_batch(
                    ctx, systems=systems, debug=args.debug, autotune=autotune
                )
            )
        tg.create_task(measure_gpu(ctx)),
        tg.create_task(measure_total(ctx)),
        tg.create_task(
            write_to_csv(
                ctx,
                prefix=args.prefix,
                backend=args.backend,
                autotune=autotune,
                gpu_accel=gpu_accel,
            )
        ),


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
