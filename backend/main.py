from fastapi import FastAPI

app = FastAPI(title="CompliCopilot API", version="0.1.0")

@app.get("/")
def root():
    return {"status": "ok", "service": "backend", "version": "0.1.0"}
