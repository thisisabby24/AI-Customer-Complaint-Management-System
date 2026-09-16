from app.assistant_routes import router as assistant_router
from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.routes import router


app = FastAPI(

    title=
        "AI Complaint Management System",

    version=
        "1.0.0"

)


app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


app.include_router(
    router
)
app.include_router(assistant_router)


@app.get("/")
def root():

    return {

        "message":
            "AI Complaint Management System API is running"

    }