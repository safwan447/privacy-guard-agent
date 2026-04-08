import json
import os
from models import PrivacyObservation, PrivacyAction, PrivacyActionType

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
        return {
            "current_segment_index": self.seg_idx,
            "current_document_index": self.doc_idx,
            "is_done": self.seg_idx >= len(segments)
        }

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
            context_before="No context" if current_idx == 0 else segments[current_idx-1]["text"][:50],
            context_after="No context" if current_idx >= len(segments)-1 else segments[current_idx+1]["text"][:50],
            segment_id=current_idx
        )

    def step(self, action: PrivacyAction):
        """
        META RULE: Rewards MUST be strictly between 0 and 1.
        Success: 0.85 | Failure: 0.15
        """
        segments = self.documents[self.doc_idx]["segments"]
        segment = segments[self.seg_idx]
        is_pii = segment["is_pii"]
        
        # Determine reward strictly inside (0, 1)
        if (is_pii and action.action == PrivacyActionType.REDACT) or \
           (not is_pii and action.action == PrivacyActionType.KEEP):
            reward = 0.85
        else:
            reward = 0.15
        
        self.seg_idx += 1
        done = self.seg_idx >= len(segments)
        obs = self._get_obs() if not done else None
        
        return obs, float(reward), done, {}