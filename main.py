import asyncio

from bp1 import benchmarking
from bp1.data_structures import Context
from bp1.measuring import measure_gpu, measure_total
from bp1.writing import write_to_csv


async def main() -> None:
    ctx = Context()

    tasks = [
        asyncio.create_task(benchmarking.run_batch(ctx)),
        asyncio.create_task(measure_gpu(ctx)),
        asyncio.create_task(measure_total(ctx)),
        asyncio.create_task(write_to_csv(ctx)),
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
