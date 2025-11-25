import asyncio

from data_structures import Context
from ENG110_python import get_eng110_data


async def measure_gpu(ctx: Context) -> None:
    """
    Continuously measure GPU power draw with nvidia-smi and save to shared state.
    """

    while not ctx.stop_event.is_set():
        proc = await asyncio.create_subprocess_shell(
            "nvidia-smi -i 0 --query-gpu=power.draw --format=csv,nounits,noheader",
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        measurement = float(stdout.decode().replace("\n", ""))

        async with ctx.lock:
            ctx.power_data.gpu = measurement

        await asyncio.sleep(1)


async def measure_total(ctx: Context) -> None:
    """
    Continuously measure total power draw with ENG110 power meter and save to shared
    state.
    """

    while not ctx.stop_event.is_set():
        measurement = float(f"{get_eng110_data()[2]:.2f}")

        async with ctx.lock:
            ctx.power_data.total = measurement

        await asyncio.sleep(1)


if __name__ == "__main__":
    pass
