import asyncio
from dataclasses import dataclass, field

type ComputePlan = dict[int, int, float, bool, bool, str]


@dataclass
class PowerData:
    gpu: float | str = ""
    total: float | str = ""
    is_running: bool = False
    n_atoms: int | str = ""
    tps: float | str = ""


@dataclass
class Context:
    power_data: PowerData = field(default_factory=PowerData)
    stop_event: asyncio.Event = asyncio.Event()
    lock: asyncio.Lock = asyncio.Lock()
