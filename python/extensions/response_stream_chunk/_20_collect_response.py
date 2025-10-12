from python.helpers.extension import Extension
from python.helpers.prompt_injection import detect_output_text, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD

class CollectResponseFullBuffer(Extension):
    async def execute(self, **kwargs):
        # Accumulate the full response into agent data for end-of-stream checks
        stream_data = kwargs.get("stream_data")
        agent = kwargs.get("agent")
        if not agent or not stream_data:
            return
        try:
            key = "_full_response_buffer"
            full = stream_data.get("full")
            if isinstance(full, str) and full:
                agent.set_data(key, full)
            else:
                # Fallback to appending chunk
                chunk = stream_data.get("chunk") or ""
                prev = agent.get_data(key) or ""
                agent.set_data(key, prev + (chunk if isinstance(chunk, str) else ""))
        except Exception:
            return
