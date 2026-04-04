import json
from models import PrivacyObservation, PrivacyAction, PrivacyActionType

class PrivacyEnv:
    def __init__(self, data_path="docs.json"):
        with open(data_path, "r") as f:
            self.documents = json.load(f)
        self.doc_idx = 0
        self.seg_idx = 0

    def state(self):
        # Mandatory for OpenEnv Spec Compliance
        return {
            "current_segment_index": self.seg_idx,
            "current_document_index": self.doc_idx,
            "is_done": self.seg_idx >= len(self.documents[self.doc_idx]["segments"])
        }

    def reset(self):
        self.seg_idx = 0
        return self._get_obs()

    def _get_obs(self):
        doc = self.documents[self.doc_idx]
        segment = doc["segments"][self.seg_idx]
        return PrivacyObservation(
            text_segment=segment["text"],
            context_before="...", # Logic to grab surrounding text
            context_after="...",
            segment_id=self.seg_idx
        )

    def step(self, action: PrivacyAction):
        segment = self.documents[self.doc_idx]["segments"][self.seg_idx]
        reward = 0.0
        
        # Grader Logic: Correct Redaction vs. Missed PII
        is_pii = segment["is_pii"]
        if is_pii and action.action == PrivacyActionType.REDACT:
            reward = 1.0  # Perfect catch
        elif not is_pii and action.action == PrivacyActionType.KEEP:
            reward = 0.2  # Correctly ignored non-PII
        elif is_pii and action.action == PrivacyActionType.KEEP:
            reward = -1.5 # CRITICAL FAILURE: Data Leak!
        
        self.seg_idx += 1
        done = self.seg_idx >= len(self.documents[self.doc_idx]["segments"])
        return self._get_obs() if not done else None, reward, done, {}