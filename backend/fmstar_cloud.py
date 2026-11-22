from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="FMStar AI Studio API",
    description="FMStar Backend Server",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # سيتم تقييدها لاحقاً
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "FMStar AI Studio",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": "fmstar-backend"
    }

@app.get("/api/v1/providers")
async def providers():
    return {
        "providers": [
            {
                "name": "Claude",
                "status": "not_configured"
            },
            {
                "name": "Gemini",
                "status": "not_configured"
            },
            {
                "name": "OmniRoute",
                "status": "not_configured"
            }
        ]
    }

@app.get("/api/v1/models")
async def models():
    return {
        "models": []
    }
  
