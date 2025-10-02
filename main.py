import pandas as pd
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def root():
    return {"message": "SPI Python API is running"}

@app.post("/analyze_csv/")
async def analyze_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    avg_score = df['Score'].mean()
    max_score = df['Score'].max()
    min_score = df['Score'].min()
    fail_rate = (df['Score'] < 50).mean() * 100

    return {
        "average": round(avg_score, 2),
        "highest": int(max_score),
        "lowest": int(min_score),
        "failure_rate": round(fail_rate, 2)
    }
