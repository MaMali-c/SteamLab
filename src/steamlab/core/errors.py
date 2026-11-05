"""User-facing errors carry both English and Persian descriptions."""


class SteamLabError(ValueError):
    def __init__(self, english: str, persian: str):
        self.english = english
        self.persian = persian
        super().__init__(f"{english} ({persian})")


class InputError(SteamLabError):
    """Invalid, unsupported, or non-finite input."""


class CalculationError(SteamLabError):
    """The backend could not produce a consistent finite result."""


class SaturationAmbiguity(SteamLabError):
    def __init__(self, temperature_k: float, pressure_mpa: float):
        self.temperature_k = temperature_k
        self.pressure_mpa = pressure_mpa
        super().__init__(
            f"Near saturation: Tsat = {temperature_k - 273.15:.6f} °C. "
            "Select P–x or T–x and enter vapor quality; no state has been assumed.",
            "نزدیک خط اشباع هستید؛ حالت فشار–کیفیت یا دما–کیفیت را انتخاب کنید "
            "و کیفیت بخار را وارد کنید. هیچ حالتی حدس زده نشده است.",
        )
