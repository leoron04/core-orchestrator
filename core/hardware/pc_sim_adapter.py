"""PC simulation adapter to emulate hardware interactions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    name: str
    value: float
    unit: str = ""


@dataclass
class PcSimAdapter:
    """Adapter exposing simulated sensors and actuators."""

    sensors: Dict[str, SensorReading] = field(default_factory=dict)
    actuators: Dict[str, float] = field(default_factory=dict)
    listeners: List[Callable[[SensorReading], None]] = field(default_factory=list)

    def register_sensor(self, name: str, initial_value: float = 0.0, unit: str = "") -> None:
        logger.debug("Registering sensor %s", name)
        self.sensors[name] = SensorReading(name=name, value=initial_value, unit=unit)

    def register_actuator(self, name: str, initial_value: float = 0.0) -> None:
        logger.debug("Registering actuator %s", name)
        self.actuators[name] = initial_value

    def read_sensor(self, name: str) -> SensorReading:
        reading = self.sensors.get(name)
        if not reading:
            msg = f"Unknown sensor {name}"
            raise KeyError(msg)
        logger.info("Sensor %s read as %s %s", name, reading.value, reading.unit)
        self._notify(reading)
        return reading

    def write_actuator(self, name: str, value: float) -> float:
        if name not in self.actuators:
            msg = f"Unknown actuator {name}"
            raise KeyError(msg)
        logger.info("Actuator %s set to %s", name, value)
        self.actuators[name] = value
        return value

    def _notify(self, reading: SensorReading) -> None:
        for listener in self.listeners:
            listener(reading)

    def add_listener(self, callback: Callable[[SensorReading], None]) -> None:
        logger.debug("Adding sensor listener %s", callback)
        self.listeners.append(callback)
