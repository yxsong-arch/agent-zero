from python.helpers.extension import Extension
from python.helpers.prompt_injection import detect_output_text, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD

class DetectPromptInjectionInOutput(Extension):
    async def execute(self, **kwargs):
        agent = kwargs.get("agent")
        if not agent:
            return
        try:
            key = "_full_response_buffer"
            text = agent.get_data(key) or ""
            if not isinstance(text, str) or not text:
                return

            result = detect_output_text(text[:50000])  # limit for perf
            risk = result.get("risk_score", 0.0)
            signals = result.get("signals", {})
            triggers = result.get("triggers", [])

            if risk >= MEDIUM_RISK_THRESHOLD:
                heading = f"icon://shield Security: Potential prompt injection in output (risk={risk:.2f})"
                kvps = {"signals": signals, "triggers": ", ".join(triggers)}
                t = "warning" if risk >= HIGH_RISK_THRESHOLD else "info"
                self.agent.context.log.log(type=t, heading=heading, kvps=kvps)

            # Clear buffer
            agent.set_data(key, "")
        except Exception:
            return
