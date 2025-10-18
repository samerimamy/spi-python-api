from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from clo_analytics_service2 import load_course_data, load_grades_csv, compute_clo
import tempfile, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Python Analytics Server is running"}

@app.post("/process_clo")
async def process_clo(course_code: str = Form(...), file: UploadFile = File(...)):
    """Receive a cleaned CSV from Blazor, run CLO analytics, and return table."""
    try:
        tmp_dir = tempfile.gettempdir()
        filename = os.path.basename(file.filename).replace("\\", "_").replace("/", "_")
        temp_path = os.path.join(tmp_dir, filename)

        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        clo_df, assessments = load_course_data(course_code)
        df = load_grades_csv(temp_path, list(assessments.keys()))
        result = compute_clo(df, clo_df, assessments)

        os.remove(temp_path)
        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
