@echo off
echo Starting FastAPI Server
start cmd /k uvicorn model_service:app --host 0.0.0.0 --port 5501
echo FastAPI Server started

echo Starting Streamlit app
start cmd /k uvicorn server:app --host 0.0.0.0 --port 5500
echo Streamlit App started

