import asyncio
from dataclasses import dataclass, field


@dataclass
class PowerData:
    gpu: Optional[float] = None
    total: Optional[float] = None
    is_running: bool = False
    n_atoms: Optional[int] = None
    tps: Optional[int] = None


@dataclass
class Context:
    power_data: PowerData = field(default_factory=PowerData)
    stop_event: asyncio.Event = asyncio.Event()
    lock: asyncio.Lock = asyncio.Lock()
