@echo off
echo Starting FastAPI Server
start cmd /k uvicorn model_service:app --port 5501
echo FastAPI Server started

echo Starting Streamlit app
start cmd /k uvicorn server:app --port 5500
echo Streamlit App started

