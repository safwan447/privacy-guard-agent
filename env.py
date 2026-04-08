import json
import os
from models import PrivacyObservation, PrivacyAction, PrivacyActionType
from grader import calculate_pii_score

class PrivacyEnv:
    def __init__(self, data_path="docs.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, data_path)
        with open(full_path, "r") as f:
            self.documents = json.load(f)
        self.doc_idx = 0
        self.seg_idx = 0

    def state(self):
        doc = self.documents[self.doc_idx]
        segments = doc.get("segments", [])
        return {"current_segment_index": self.seg_idx, "is_done": self.seg_idx >= len(segments)}

    def reset(self):
        self.seg_idx = 0
        return self._get_obs()

    def _get_obs(self):
        doc = self.documents[self.doc_idx]
        segments = doc["segments"]
        current_idx = min(self.seg_idx, len(segments) - 1)
        segment = segments[current_idx]
        return PrivacyObservation(
            text_segment=segment["text"],
            context_before="None" if current_idx == 0 else segments[current_idx-1]["text"][:30],
            context_after="None" if current_idx >= len(segments)-1 else segments[current_idx+1]["text"][:30],
            segment_id=current_idx
        )

    def step(self, action: PrivacyAction):
        segments = self.documents[self.doc_idx]["segments"]
        segment = segments[self.seg_idx]
        
        # Call the grader logic
        reward = calculate_pii_score(action.action.value, segment["is_pii"])
        
        self.seg_idx += 1
        done = self.seg_idx >= len(segments)
        obs = self._get_obs() if not done else None
        return obs, float(reward), done, {}