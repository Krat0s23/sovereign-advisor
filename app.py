from fastapi import FastAPI
from pydantic import BaseModel
from recommend import recommend

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "IBM Sovereign Advisor API Running"
    }


class UserInput(BaseModel):
    geo: str
    compliance: str
    workload: str
    ownership: str
    growth: str
    data_residency: str


@app.post("/recommend")
def get_recommendation(data: UserInput):

    result = recommend(
        data.geo,
        data.compliance,
        data.workload,
        data.ownership,
        data.growth,
        data.data_residency
    )

    return result

