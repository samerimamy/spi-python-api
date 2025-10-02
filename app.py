import os
import uvicorn
from fastapi import FastAPI, UploadFile, File
import pandas as pd

app = FastAPI()   # <- uvicorn looks for this "app"

@app.get("/")
async def root():
    return {"message": "Welcome to SPI Python API"}

@app.post("/analyze_csv/")
async def analyze_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    avg_score = df['Score'].mean()
    max_score = df['Score'].max()
    min_score = df['Score'].min()
    fail_rate = (df['Score'] < 50).mean() * 100

    return {
        "average": round(avg_score, 2),
        "highest": max_score,
        "lowest": min_score,
        "failure_rate": round(fail_rate, 2)
    }

# ✅ Ensure Render uses the correct port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
