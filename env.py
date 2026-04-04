import json
import os
from models import PrivacyObservation, PrivacyAction, PrivacyActionType

class PrivacyEnv:
    def __init__(self, data_path="docs.json"):
        # Use absolute path to ensure Docker finds the file correctly
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
        
        # Safety check: if we exceed segments, return the last one
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
        Rewards are strictly in the [0.0, 1.0] range per Meta Hackathon rules.
        """
        segments = self.documents[self.doc_idx]["segments"]
        segment = segments[self.seg_idx]
        is_pii = segment["is_pii"]
        
        # --- REWARD LOGIC: 0.0 to 1.0 Range Only ---
        reward = 0.0
        
        if is_pii and action.action == PrivacyActionType.REDACT:
            reward = 1.0  # Perfect catch of sensitive data
        elif not is_pii and action.action == PrivacyActionType.KEEP:
            reward = 1.0  # Correctly identified safe data
        elif is_pii and action.action == PrivacyActionType.KEEP:
            reward = 0.0  # FAILED: Data Leak (Penalty = lowest possible score)
        elif not is_pii and action.action == PrivacyActionType.REDACT:
            reward = 0.0  # FAILED: Over-redaction (Penalty = lowest possible score)
        
        # Progress the segment index
        self.seg_idx += 1
        done = self.seg_idx >= len(segments)
        
        # Return results
        obs = self._get_obs() if not done else None
        return obs, float(reward), done, {}