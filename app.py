# app.py
from fastapi import FastAPI, UploadFile, File
from clo_analytics_service2 import load_course_data, load_grades_csv, compute_clo
import pandas as pd
import os
import io

app = FastAPI()

@app.post("/process_clo")
async def process_clo(course_code: str, file: UploadFile = File(...)):
    """Receive a cleaned CSV from Blazor, run CLO analytics, and return table."""
    try:
        # 1️⃣ Save uploaded file temporarily
        contents = await file.read()
        temp_path = os.path.join("/tmp", file.filename)
        with open(temp_path, "wb") as f:
            f.write(contents)

        # 2️⃣ Load course configuration
        clo_df, assessments = load_course_data(course_code)

        # 3️⃣ Run CLO analytics
        df = load_grades_csv(temp_path, list(assessments.keys()))
        result = compute_clo(df, clo_df, assessments)

        # 4️⃣ Return as JSON
        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
