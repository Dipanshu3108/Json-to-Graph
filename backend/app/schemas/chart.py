from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, field_validator, model_validator


class Dataset(BaseModel):
    label: str
    data: list[float]

    @field_validator("data")
    @classmethod
    def data_must_be_nonempty(cls, values: list[float]) -> list[float]:
        if not values:
            raise ValueError("dataset.data must contain at least one value")
        return values


class ScatterPoint(BaseModel):
    x: float
    y: float
    label: Optional[str] = None


class ScatterDataset(BaseModel):
    label: str
    data: list[ScatterPoint]


class ChartInput(BaseModel):
    labels: list[str]
    datasets: list[Dataset]

    @model_validator(mode="after")
    def labels_match_data_length(self) -> "ChartInput":
        for ds in self.datasets:
            if len(ds.data) != len(self.labels):
                raise ValueError(
                    f"Dataset '{ds.label}' has {len(ds.data)} values "
                    f"but there are {len(self.labels)} labels"
                )
        return self


class ScatterInput(BaseModel):
    datasets: list[ScatterDataset]


ChartTypeStr = Literal["bar", "line", "pie", "doughnut", "area", "scatter"]


class ValidateRequest(BaseModel):
    chartType: ChartTypeStr
    data: dict


class ValidateResponse(BaseModel):
    valid: bool
    errors: list[dict]
    normalizedData: Optional[Union[dict, None]] = None


class RepairRequest(BaseModel):
    chartType: ChartTypeStr
    data: Any


class RepairResponse(BaseModel):
    fixed: bool
    normalizedData: Optional[dict] = None
    changes: list[str] = []
    error: Optional[str] = None


class GenerateCodeRequest(BaseModel):
    chartType: str
    data: Any
    theme: Optional[str] = "default"


class GenerateCodeResponse(BaseModel):
    code: str
    error: Optional[str] = None
