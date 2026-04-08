import sys
import os
from fastapi import FastAPI, HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import PrivacyAction
from env import PrivacyEnv

app = FastAPI()
env = PrivacyEnv()

@app.post("/reset")
async def reset():
    obs = env.reset()
    return obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()

@app.post("/step")
async def step(action: PrivacyAction):
    obs, reward, done, info = env.step(action)
    return {
        "observation": (obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()) if obs else None,
        "reward": float(reward),
        "done": done,
        "info": info
    }

@app.get("/tasks")
async def get_tasks():
    return env.documents

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()