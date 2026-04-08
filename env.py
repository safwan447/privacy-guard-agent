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
        """Mandatory for OpenEnv Spec Compliance."""
        doc = self.documents[self.doc_idx]
        segments = doc.get("segments", [])
        return {
            "current_segment_index": self.seg_idx,
            "current_document_index": self.doc_idx,
            "is_done": self.seg_idx >= len(segments)
        }

    def reset(self):
        """Restarts the environment for a fresh evaluation."""
        self.seg_idx = 0
        return self._get_obs()

    def _get_obs(self):
        """Constructs the observation for the agent."""
        doc = self.documents[self.doc_idx]
        segments = doc["segments"]
        
        current_idx = min(self.seg_idx, len(segments) - 1)
        segment = segments[current_idx]
        
        return PrivacyObservation(
            text_segment=segment["text"],
            context_before="No context available" if current_idx == 0 else segments[current_idx-1]["text"][:50],
            context_after="No context available" if current_idx >= len(segments)-1 else segments[current_idx+1]["text"][:50],
            segment_id=current_idx
        )

    def step(self, action: PrivacyAction):
        """
        Processes the action and returns (obs, reward, done, info).
        META RULE: Rewards must be STRICTLY between 0.0 and 1.0 (e.g., 0.1 or 0.9).
        """
        segments = self.documents[self.doc_idx]["segments"]
        segment = segments[self.seg_idx]
        is_pii = segment["is_pii"]
        
        # We use 0.9 for success and 0.1 for failure to stay within (0, 1) range
        reward = 0.1
        
        if is_pii and action.action == PrivacyActionType.REDACT:
            reward = 0.9  # Correct Redaction
        elif not is_pii and action.action == PrivacyActionType.KEEP:
            reward = 0.9  # Correct Keep
        elif is_pii and action.action == PrivacyActionType.KEEP:
            reward = 0.1  # Leak
        elif not is_pii and action.action == PrivacyActionType.REDACT:
            reward = 0.1  # Over-redaction
        
        # Progress the segment index
        self.seg_idx += 1
        done = self.seg_idx >= len(segments)
        
        # Return results
        obs = self._get_obs() if not done else None
        return obs, float(reward), done, {}