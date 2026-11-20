from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .engine import PAIRS

class CalculationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    input_pair: Literal['T_P','T_x','P_x','T_s','T_u','T_h','T_v','P_s','P_u','P_h','P_v']
    values: dict[str, float] = Field(strict=True)

    @model_validator(mode='before')
    @classmethod
    def strict_values(cls, data):
        if isinstance(data, dict) and isinstance(data.get('values'), dict):
            if any(type(v) not in (int,float) for v in data['values'].values()):
                raise ValueError('Values must be JSON numbers, not strings or booleans.')
        return data

    @model_validator(mode='after')
    def exact_keys(self):
        if set(self.values) != set(self.input_pair.split('_')):
            raise ValueError('Exactly the two properties named in input_pair are required.')
        return self

class FullState(BaseModel):
    T: float
    P: float
    h: float
    u: float
    s: float
    v: float

class Convergence(BaseModel):
    converged: bool
    residuals: dict[str,float]
    tolerances: dict[str,float]
    evaluations: int
    verified_candidates: int
    uniqueness_certified: bool

class CalculationResponse(BaseModel):
    input_pair: str
    normalized_inputs: dict[str,float]
    calculated_properties: dict[str,float]
    full_state: FullState
    region: int
    phase: str
    quality: float | None
    saturation: dict[str,float]
    solver_method: str
    convergence: Convergence
    scientific_warnings: list[str]
