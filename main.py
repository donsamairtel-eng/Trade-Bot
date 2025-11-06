from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CoinSwitch Trading Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket clients
websocket_clients: List[WebSocket] = []

async def broadcast(message: dict):
    for client in websocket_clients:
        try:
            await client.send_json(message)
        except:
            pass

@app.get("/")
async def root():
    return {"message": "CoinSwitch Trading Bot", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/status")
async def get_status():
    return {
        "is_running": False,
        "environment": os.getenv("ENVIRONMENT", "SANDBOX"),
        "circuit_breaker_triggered": False,
        "daily_loss": 0,
        "open_positions": 0
    }

@app.post("/start")
async def start_bot():
    return {"message": "Bot started", "environment": os.getenv("ENVIRONMENT", "SANDBOX")}

@app.post("/stop")
async def stop_bot():
    return {"message": "Bot stopped"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "status_update",
            "status": {
                "is_running": False,
                "environment": os.getenv("ENVIRONMENT", "SANDBOX")
            }
        })
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
