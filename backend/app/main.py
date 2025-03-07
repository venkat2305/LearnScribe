from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .routers import auth, quiz, summary

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

# Summary routes
app.include_router(summary.router, prefix="/summary", tags=["Summaries"])
