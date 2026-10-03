from fastapi import FastAPI
from pydantic import BaseModel
try:
    from .risk_engine import RiskEngine
except ImportError:
    from risk_engine import RiskEngine

app = FastAPI(title="AI/NLP Financial Risk Engine", version="1.0")
engine = RiskEngine()

class AnalyzeRequest(BaseModel):
    text: str
    source: str = "api"
    entity: str = "Unknown"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return engine.analyze(req.text, req.source, req.entity).__dict__