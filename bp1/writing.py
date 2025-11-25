import asyncio
import csv


async def write_to_csv(ctx: Context) -> None:
    """
    Continuously write data to csv.
    """
    d = ctx.power_data
    filename = "debug.csv"

    with open(filename, "w", buffering=1) as f:
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
