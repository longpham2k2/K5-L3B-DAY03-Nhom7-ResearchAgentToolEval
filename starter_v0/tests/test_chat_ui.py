from __future__ import annotations

from typing import Any

from chat import run_model_tool_loop
from providers.base import ModelResponse, ToolCall


class SendRequestProvider:
    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        return ModelResponse(
            tool_calls=[ToolCall(name="send", args={"text": "Test message", "confirmed": True})]
        )


def test_tool_call_guard_pauses_send_before_execution() -> None:
    result = run_model_tool_loop(
        provider=SendRequestProvider(),
        messages=[{"role": "user", "content": "Send this"}],
        tools=[],
        model=None,
        max_tool_rounds=1,
        tool_call_guard=lambda call: call.name != "send",
    )

    assert result["status"] == "waiting_for_confirmation"
    assert result["pending_tool_event"]["tool"] == "send"
    assert result["pending_tool_event"]["args"]["text"] == "Test message"
    assert result["pending_tool_event"]["result"]["status"] == "awaiting_confirmation"
