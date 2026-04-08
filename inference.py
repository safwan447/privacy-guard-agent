import os
import asyncio
from openai import OpenAI
from env import PrivacyEnv
from models import PrivacyAction, PrivacyActionType

# Credentials
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"

SYSTEM_PROMPT = """
You are a Privacy Guard. You will receive a text segment. 
If it contains Personal Information (Names, Phone Numbers, Emails), reply with REDACT.
If the text is safe and contains no PII, reply with KEEP.
Reply with ONLY the word REDACT or KEEP.
"""

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = PrivacyEnv()
    
    # Run for all 3 tasks in docs.json
    for doc_idx in range(len(env.documents)):
        env.doc_idx = doc_idx
        obs = env.reset()
        task_id = env.documents[doc_idx]["id"]
        
        print(f"[START] task={task_id} env=privacy_guard model={MODEL_NAME}", flush=True)
        
        rewards = []
        step_count = 1
        done = False
        
        while not done:
            # LLM Inference
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Segment: {obs.text_segment}"}
                ],
                max_tokens=10
            )
            action_text = response.choices[0].message.content.strip().upper()
            action_enum = PrivacyActionType.REDACT if "REDACT" in action_text else PrivacyActionType.KEEP
            
            # Step environment
            obs, reward, done, _ = env.step(PrivacyAction(action=action_enum))
            rewards.append(reward)
            
            print(f"[STEP] step={step_count} action={action_text} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)
            step_count += 1

        # CLAMP SCORE: Ensures it stays strictly between 0 and 1 (e.g., 0.15 to 0.85)
        raw_score = sum(rewards) / len(rewards) if rewards else 0.5
        final_score = min(max(raw_score, 0.15), 0.85)
        success = final_score > 0.5
        
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(f"[END] success={str(success).lower()} steps={len(rewards)} score={final_score:.2f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())