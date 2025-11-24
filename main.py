import asyncio
import time
from dataclasses import dataclass
from typing import Callable

from ENG110_python import get_eng110_data


@dataclass
class PowerData:
    gpu: float | None = None
    total: float | None = None
    is_running: bool = False


async def timed_task(
    stop_event: asyncio.Event, func: Callable, *args, **kwargs
) -> None:
    """
    Call a function with tick index and custom args once a second until stop event is
    triggered.

    Format: func(tick_index: int, *args, **kwargs)
    """

    i = 0  # tick counter
    dt = 1  # tick rate in seconds
    t_start = time.time()

    while not stop_event.is_set():
        t_sched = t_start + i * dt  # scheduled measurement

        await func(i, *args, **kwargs)

        # Pause sampling for dt seconds
        t_current = time.time()
        t_next = t_sched + dt  # next measurement
        t_sleep = t_next - t_current
        if t_sleep > 0 and not stop_event.is_set():
            await asyncio.sleep(t_sleep)

        i += 1


async def run_bench(stop_event: asyncio.Event) -> None:
    """
    TEMP: Placeholder for running benchmark.
    """

    await asyncio.sleep(5)
    stop_event.set()


async def update_total_draw(i: int, power_data: PowerData, lock: asyncio.Lock) -> None:
    """
    Update power draw measurement from ENG110 power meter.
    """

    measurement = "{:.2f}".format(get_eng110_data()[2])
    async with lock:
        power_data.total = measurement


async def update_gpu_draw(i: int, power_data: PowerData, lock: asyncio.Lock) -> None:
    """
    Update power draw measurement from nvidia-smi.
    """

    proc = await asyncio.create_subprocess_shell(
        "nvidia-smi -i 0 --query-gpu=power.draw --format=csv,nounits,noheader",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    measurement = stdout.decode().replace("\n", "")
    async with lock:
        power_data.gpu = measurement


async def tail_data(i: int, power_data: PowerData, lock: asyncio.Lock):
    """
    TEMP: Print data once per second.

    Format: time,gpu,total,is_running
        time:       timestamp in seconds
        gpu:        gpu power draw in watts
        total:      total power draw in watts
        is_running: if md simulation is running
    """

    async with lock:
        print(i, power_data.gpu, power_data.total, power_data.is_running)


async def main():
    power_data = PowerData()
    lock = asyncio.Lock()
    stop_event = asyncio.Event()

    tasks = [
        asyncio.create_task(run_bench(stop_event)),
        asyncio.create_task(timed_task(stop_event, update_gpu_draw, power_data, lock)),
        asyncio.create_task(
            timed_task(stop_event, update_total_draw, power_data, lock)
        ),
        asyncio.create_task(timed_task(stop_event, tail_data, power_data, lock)),
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
