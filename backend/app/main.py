from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .routers import auth

app = FastAPI(
    title="LearnScribe Backend",
    description="FastAPI backend for the Learnsribe project.",
    version="0.1.0",
)


@app.get("/", tags=["Health Check"])
def health_check():
    return JSONResponse({"status": "OK", "message": "LearnScribe backend is running."})


# Include the authentication router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])