from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from clo_analytics_service2 import load_course_data, load_grades_csv, compute_clo
import os
import pandas as pd
import io
import requests

# ---------------------------------------------------
# FastAPI App Configuration
# ---------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow requests from Blazor and local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# Root Test Endpoint
# ---------------------------------------------------
@app.get("/")
def root():
    return {"message": "Python Analytics Server is running"}


# ---------------------------------------------------
# 1️⃣ Local Upload Endpoint (existing functionality)
# ---------------------------------------------------
@app.post("/process_clo")
async def process_clo(course_code: str = Form(...), file: UploadFile = File(...)):
    """Receive a Blackboard CSV from Blazor, clean it, save permanently, and compute CLO results."""
    try:
        # Define upload directory (adjust to your Blazor wwwroot path)
        uploads_dir = r"D:\Experiment\Students_Performance_Indicator\Students_Performance_Indicator\wwwroot\uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        # Save uploaded file
        original_name = os.path.basename(file.filename).replace("\\", "_").replace("/", "_")
        raw_path = os.path.join(uploads_dir, original_name)
        contents = await file.read()

        with open(raw_path, "wb") as f:
            f.write(contents)
        print(f"✅ Raw file saved: {raw_path}")

        # Create cleaned file path
        name_root, ext = os.path.splitext(original_name)
        cleaned_name = f"{name_root}_cleaned{ext}"
        cleaned_path = os.path.join(uploads_dir, cleaned_name)
        print(f"🧹 Cleaned file target: {cleaned_path}")

        # Process and clean data
        clo_df, assessments = load_course_data(course_code)
        df = load_grades_csv(raw_path, list(assessments.keys()))

        # Save cleaned data for reference
        df.to_csv(cleaned_path, index=False)

        # Compute CLO results
        result = compute_clo(df, clo_df, assessments)

        return {
            "message": "CLO Analysis Complete (Local Upload)",
            "cleaned_file": cleaned_name,
            "records": result.to_dict(orient="records")
        }

    except Exception as e:
        print(f"❌ Error in process_clo: {e}")
        return {"error": str(e)}


# ---------------------------------------------------
# 2️⃣ Cloud-Based Endpoint (OneDrive integration)
# ---------------------------------------------------
@app.post("/process_from_cloud")
async def process_from_cloud(course_code: str = Form(...), file_name: str = Form(...)):
    """
    Download the cleaned file directly from your OneDrive/SharePoint folder,
    process CLO analytics, and return the results to Blazor.
    """
    try:
        # 1️⃣ Base shared OneDrive link
        base_url = (
            "https://pmuedusa-my.sharepoint.com/:f:/g/personal/"
            "salimamy_pmu_edu_sa/Eg0kaLQDci5Ej0RVIFI7HIoBR0w3Kylu7trkIB_Urb1spA"
        )

        # 2️⃣ Construct full file URL
        file_url = f"{base_url}/{file_name}?e=d06MP7"
        print(f"🔗 Fetching file from OneDrive: {file_url}")

        # 3️⃣ Download the CSV file
        response = requests.get(file_url)
        if response.status_code != 200:
            print(f"❌ Failed to download file from OneDrive (HTTP {response.status_code})")
            return {"error": f"Failed to download file from OneDrive. Status: {response.status_code}"}

        # 4️⃣ Load the CSV into a DataFrame
        df = pd.read_csv(io.BytesIO(response.content))
        print(f"✅ CSV loaded from OneDrive. Shape: {df.shape}")

        # 5️⃣ Load course configuration and compute CLOs
        clo_df, assessments = load_course_data(course_code)
        result = compute_clo(df, clo_df, assessments)

        # 6️⃣ Return result back to Blazor
        return {
            "message": f"CLO Analysis Complete (from OneDrive file: {file_name})",
            "records": result.to_dict(orient="records")
        }

    except Exception as e:
        print(f"❌ Error in process_from_cloud: {e}")
        return {"error": str(e)}
