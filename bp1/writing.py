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

    await asyncio.sleep(0.5)

    d = ctx.power_data

    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filename = f"{prefix}-{backend}"
    if autotune:
        filename += "-at"
    elif gpu_accel:
        filename += "-gpu"

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
                    d.gpu,
                    d.total,
                    d.is_running,
                    d.n_atoms,
                    d.tps,
                ]
            )
            i += 1
            await asyncio.sleep(1)


if __name__ == "__main__":
    pass
