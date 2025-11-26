import asyncio
import csv
import os

from .data_structures import Context


async def write_to_csv(
    ctx: Context,
    prefix: str,
    backend: str,
    autotune: bool = False,
    gpu_accel: bool = False,
) -> None:
    """
    Continuously write data to csv.
    """

    d = ctx.power_data

    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filename = f"{prefix}-{backend}"
    if autotune:
        filename += f"-{at}"
    elif gpu_accel:
        filename += f"-{gpu}"

    with open(f"{data_dir}/{filename}.csv", "w", buffering=1) as f:
        w = csv.writer(f)
        w.writerow(
            [
                "time",
                "gpu",
                "total",
                "is_running",
                "n_atoms",
                "tps",
            ]
        )

        i = 0
        while not ctx.stop_event.is_set():
            w.writerow(
                [
                    i,
                    f"{d.gpu:.2f}",
                    f"{d.total:.2f}",
                    d.is_running,
                    d.n_atoms,
                    d.tps,
                ]
            )
            i += 1
            await asyncio.sleep(1)


if __name__ == "__main__":
    pass
