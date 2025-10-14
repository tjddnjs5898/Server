from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 모든 출처 허용
    allow_methods=["*"], # GET, POST, PUT, DELETE 등 허용
    allow_headers=["*"]  # 헤더 허용
)

connected_clients = []  # 접속된 클라이언트 저장

# 토픽별 최신 데이터 저장
latest_data = {
    "map": None,
    "odom": None,
    "scan": None,
    "tf": None
}

@app.get("/")
def root():
    return {"status": "FastAPI Server Running"}

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data_str = await websocket.receive_text() # 라즈베리파이에서 JSON 문자열 수신
            data_json = json.loads(data_str) # JSON 파싱

            topic = data_json.get("topic") # map, odom, scan, tf
            topic_data = data_json.get("data")

            if topic in latest_data:
                latest_data[topic] = topic_data # 메모리에 최신값 저장

            # 모든 접속 클라이언트에 브로드캐스트    
            for client in connected_clients:
                try:
                    await client.send_text(json.dumps({
                        "topic": topic,
                        "data": topic_data
                    }))
                except:
                    pass # 연결 끊긴 클라이언트는 무시

    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# 정적 파일 서비스
app.mount("/static", StaticFiles(directory="static"), name="static")
