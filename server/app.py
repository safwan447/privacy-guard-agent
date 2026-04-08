import sys
import os
from fastapi import FastAPI, HTTPException

# --- PATH FIX: Ensures server can see env.py and models.py in the root ---
# This looks one level up from the /server folder to find your core logic.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import PrivacyAction, PrivacyObservation
from env import PrivacyEnv

app = FastAPI()
env = PrivacyEnv()

@app.post("/reset")
async def reset():
    try:
        obs = env.reset()
        # model_dump() is the modern Pydantic v2 way; dict() is the fallback.
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
    """
    FIX: Returns the full documents list from docs.json.
    This ensures the 'grader' and 'id' fields are present for the validator.
    """
    try:
        return env.documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_state():
    # Returns the internal state of the environment.
    return env.state()

def main():
    """
    Mandatory Entry Point for Multi-mode Deployment.
    The validator looks for this callable function.
    """
    import uvicorn
    # We pass the 'app' object directly here.
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()