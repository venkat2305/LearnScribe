from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .routers import auth, quiz, attempt

app = FastAPI(
    title="LearnScribe Backend",
    description="FastAPI backend for the Learnsribe project.",
    version="0.1.0",
)


@app.get("/", tags=["Health Check"])
def health_check():
    return JSONResponse({"status": "OK", "message": "LearnScribe backend is running."})


# Authentication routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Quizzes routes
app.include_router(quiz.router, prefix="/quiz", tags=["Quizzes"])

# Attempt routes
app.include_router(attempt.router, prefix="/attempt", tags=["Attempts"])
