from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class State:
    """Explicit engineering units: K, MPa, m³/kg, kJ/kg, kJ/(kg K)."""

    temperature_k: float
    pressure_mpa: float
    v: float
    u: float
    h: float
    s: float
    phase: str
    region: int
    quality: float | None
    input_pair: str
    warnings: tuple[str, ...] = ()

    @property
    def temperature_c(self) -> float:
        return self.temperature_k - 273.15

    @property
    def density(self) -> float:
        return 1.0 / self.v

    def to_dict(self) -> dict:
        return asdict(self)
