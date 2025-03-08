from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, quiz, summary

app = FastAPI(
    title="LearnScribe Backend",
    description="FastAPI backend for the Learnsribe project.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
