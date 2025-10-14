from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()

connected_clients = []  # 접속된 클라이언트 저장

@app.get("/")
def root():
    return {"status": "FastAPI Server Running"}

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in connected_clients:
                await client.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

app.mount("/static", StaticFiles(directory="static"), name="static")
