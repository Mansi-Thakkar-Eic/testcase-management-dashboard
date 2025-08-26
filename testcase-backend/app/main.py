from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.suites import router as suites_router
from app.api.v1.testcases import router as testcases_router
import os
from app.db import engine, Base  # adjust import paths as per your project

# This will create all tables if they don’t exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TestCase Manager API", version="1.0.0")

# ✅ FIXED CORS
origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(suites_router, prefix="/api/v1", tags=["suites"])
app.include_router(testcases_router, prefix="/api/v1", tags=["testcases"])

# Root route
@app.get("/")
def root():
    return {"message": "Welcome to TestCase Manager API. Go to /docs for API documentation."}

# Health check
@app.get("/api/health")
def health():
    return {"status": "ok"}
