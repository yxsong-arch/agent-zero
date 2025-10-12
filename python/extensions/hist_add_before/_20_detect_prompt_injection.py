from python.helpers.extension import Extension
from python.helpers.prompt_injection import detect_input_text, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from python.helpers import log
import json

class DetectPromptInjectionInHistory(Extension):
    async def execute(self, **kwargs):
        # 'content_data' is provided before adding a user message to history
        content_data = kwargs.get("content_data")
        if not content_data:
            return

        try:
            raw = content_data.get("content", "")
            if not isinstance(raw, str):
                # Fallback to JSON if complex structure
                raw = json.dumps(raw, ensure_ascii=False)

            result = detect_input_text(raw[:20000])  # limit to 20k chars for perf
            risk = result.get("risk_score", 0.0)
            signals = result.get("signals", {})
            triggers = result.get("triggers", [])

            if risk >= MEDIUM_RISK_THRESHOLD:
                # Log a warning (medium/high risk). Do not mutate user content.
                heading = f"icon://shield Security: Potential prompt injection in input (risk={risk:.2f})"
                kvps = {"signals": signals, "triggers": ", ".join(triggers)}
                t = "warning" if risk >= HIGH_RISK_THRESHOLD else "info"
                self.agent.context.log.log(type=t, heading=heading, kvps=kvps)
        except Exception:
            # Detection should never break the flow
            return
