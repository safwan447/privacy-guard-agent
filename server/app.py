import sys
import os
from fastapi import FastAPI, HTTPException

# Path fix to see env and models in the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import PrivacyAction, PrivacyObservation
from env import PrivacyEnv

app = FastAPI()
env = PrivacyEnv()

@app.post("/reset")
async def reset():
    try:
        obs = env.reset()
        return obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(action: PrivacyAction):
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": (obs.model_dump() if hasattr(obs, 'model_dump') else obs.dict()) if obs else None,
            "reward": float(reward),
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks():
    # FIX: Returning env.documents ensures 'grader' is included for all tasks
    return env.documents

@app.get("/state")
async def get_state():
    return env.state()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()