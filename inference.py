import os
import time
from openai import OpenAI
from env import PrivacyEnv
from models import PrivacyAction, PrivacyActionType

# Mandatory Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("Warning: HF_TOKEN not set. Local testing might fail if calling cloud LLMs.")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def run_task(task_id):
    env = PrivacyEnv()
    obs = env.reset()
    
    # [START] Line: Mandatory Format
    print(f"[START] task={task_id} env=privacy-guard model={MODEL_NAME}", flush=True)

    rewards = []
    step_num = 1
    done = False
    
    while not done:
        # Prompting the LLM to decide
        prompt = f"Decide if this text is PII (Private) or not: '{obs.text_segment}'. Reply with 'REDACT' or 'KEEP' only."
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            ).choices[0].message.content.strip().upper()
        except Exception as e:
            response = "KEEP" # Fallback

        action_type = PrivacyActionType.REDACT if "REDACT" in response else PrivacyActionType.KEEP
        action = PrivacyAction(action=action_type)
        
        obs, reward, done, info = env.step(action)
        rewards.append(reward)

        # [STEP] Line: Mandatory Format
        print(f"[STEP] step={step_num} action={action_type.value} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)
        
        step_num += 1
        if done: break

    # [END] Line: Mandatory Format
    success = sum(rewards) > 0
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={step_num-1} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    # In a real run, you'd loop through all tasks in docs.json
    run_task("task_1_simple")