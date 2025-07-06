# main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agentic_workflow import agentic_workflow
from asyncio import to_thread

app = FastAPI()

# Enable CORS for your frontend (e.g., React at localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    message = data.get("message")

    if not session_id or not message:
        raise HTTPException(status_code=400, detail="Missing 'session_id' or 'message'")

    # Run the blocking agentic_workflow in a separate thread
    result = await to_thread(agentic_workflow, message, session_id)
    return {"result": result}
