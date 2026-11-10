from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ROOT,
    run_model_tool_loop,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDER_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --text-color: #172033;
        --background-color: #f4f7fb;
        --secondary-background-color: #ffffff;
        --primary-color: #2563eb;
    }
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #f4f7fb;
        color: #172033;
    }
    [data-testid="stHeader"] {
        background: rgba(244, 247, 251, 0.92);
    }
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e1e7f0;
    }
    [data-testid="stSidebar"] * { color: #263449; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 6rem; }
    .hero {
        padding: 1.5rem 1.7rem; border: 1px solid #dce6f3; border-radius: 18px;
        background: linear-gradient(125deg, #eaf1ff 0%, #f7f9ff 58%, #e9f8f4 100%);
        box-shadow: 0 12px 30px rgba(34, 57, 91, 0.07);
        margin-bottom: 1.4rem;
    }
    .hero h1 { margin: 0; color: #15243b; font-size: 2rem; }
    .hero p { color: #53647b; margin: .55rem 0 0; font-size: 1rem; }
    div[data-testid="stChatMessage"] {
        border: 1px solid #e1e7f0; border-radius: 15px; background: #ffffff;
        padding: .8rem 1rem;
        box-shadow: 0 4px 14px rgba(34, 57, 91, 0.04);
    }
    div[data-testid="stChatInput"] textarea {
        background: #ffffff;
        color: #172033;
        border-color: #d7dfeb;
    }
    div[data-testid="stChatInput"] textarea::placeholder { color: #718096; }
    [data-testid="stBottom"] {
        background: rgba(244, 247, 251, 0.96);
    }
    [data-testid="stMetricLabel"] { color: #64748b; }
    [data-testid="stMetricValue"] { color: #172033; }
    [data-testid="stAlert"] { color: #263449; }
    [data-testid="stAlert"] p { color: inherit; }
    input, textarea, [data-baseweb="select"] > div {
        color: #172033 !important;
        background-color: #ffffff !important;
    }
    label, [data-testid="stWidgetLabel"] p { color: #475569 !important; }
    .stButton > button {
        border-radius: 10px;
        border-color: #d7dfeb;
        color: #263449;
    }
    .stButton > button[kind="primary"] {
        background: #2563eb;
        border-color: #2563eb;
        color: #ffffff;
    }
    .small-label {
        color: #526a8a; text-transform: uppercase; letter-spacing: .08em;
        font-size: .72rem; font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def start_transcript(
    provider_name: str,
    model: str,
    version: str,
    artifact_version: dict[str, str],
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{version}_{provider_name}_{timestamp}"
    return {
        "transcript_id": transcript_id,
        **artifact_version,
        "provider": provider_name,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def save_current_transcript() -> None:
    transcript = st.session_state.get("transcript")
    if transcript:
        write_transcript(
            TRANSCRIPTS_DIR / f"{transcript['transcript_id']}.transcript.json",
            transcript,
        )


def render_tool_events(events: list[dict[str, Any]]) -> None:
    if not events:
        return
    with st.expander(f"🔧 Hoạt động công cụ ({len(events)})"):
        for index, event in enumerate(events, start=1):
            st.markdown(f"**{index}. `{event.get('tool', 'unknown')}`**")
            st.markdown("Tham số")
            st.json(event.get("args", {}))
            st.markdown("Kết quả")
            st.json(event.get("result", {}))


def render_conversation() -> None:
    transcript = st.session_state.get("transcript")
    if not transcript or not transcript["turns"]:
        return
    for turn in transcript["turns"]:
        with st.chat_message("user"):
            st.markdown(turn.get("user", ""))
        with st.chat_message("assistant"):
            if turn.get("status") == "provider_error":
                st.error(turn.get("error", "Đã xảy ra lỗi khi gọi provider."))
            else:
                st.markdown(turn.get("assistant_text") or "Agent chưa trả về nội dung.")
            render_tool_events(turn.get("tool_events", []))


def update_pending_event(turn: dict[str, Any], new_event: dict[str, Any]) -> None:
    args = new_event.get("args", {})
    for event_list in (
        turn.get("tool_events", []),
        *[round_record.get("tool_results", []) for round_record in turn.get("rounds", [])],
    ):
        for index, event in enumerate(event_list):
            if (
                event.get("tool") == "send"
                and event.get("args", {}) == args
                and event.get("result", {}).get("status") == "awaiting_confirmation"
            ):
                event_list[index] = new_event


st.sidebar.markdown("## ⚙️ Cấu hình")
provider_name = st.sidebar.selectbox(
    "Provider",
    ["openrouter", "openai", "anthropic", "gemini", "ollama"],
    format_func=lambda value: {
        "openrouter": "OpenRouter",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "gemini": "Google Gemini",
        "ollama": "Ollama (local)",
    }[value],
)
provider = make_provider(provider_name)
default_model = getattr(provider, "default_model", "") or ""
model = st.sidebar.text_input(
    "Model",
    value=default_model,
    key=f"model_{provider_name}",
    help="Để trống để dùng model mặc định của provider.",
).strip() or None
version = st.sidebar.text_input("Nhãn version", value="v3")
history_window = st.sidebar.slider("Số lượt hội thoại đưa vào context", 1, 10, 5)
max_tool_rounds = st.sidebar.slider("Số vòng gọi tool tối đa", 1, 8, 4)

api_key_name = PROVIDER_KEYS.get(provider_name)
if api_key_name:
    if os.getenv(api_key_name):
        st.sidebar.success(f"Đã tìm thấy `{api_key_name}`")
    else:
        st.sidebar.warning(f"Chưa cấu hình `{api_key_name}` trong `.env`")
else:
    st.sidebar.info(
        f"Ollama endpoint: `{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')}`"
    )

try:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
except (OSError, KeyError, TypeError, ValueError) as exc:
    st.error(f"Không thể đọc cấu hình agent: {type(exc).__name__}: {exc}")
    st.stop()

config_signature = (
    provider_name,
    model,
    version,
    artifact_version.prompt_hash,
    artifact_version.tools_hash,
    history_window,
    max_tool_rounds,
)
if st.session_state.get("config_signature") != config_signature:
    st.session_state["config_signature"] = config_signature
    st.session_state["history"] = []
    st.session_state["transcript"] = None
    st.session_state["pending_send"] = None

st.sidebar.markdown("---")
st.sidebar.markdown("#### Công cụ")
st.sidebar.caption("Agent có thể tự chọn công cụ phù hợp với yêu cầu.")
tool_columns = st.sidebar.columns(2)
for index, declaration in enumerate(tool_declarations):
    tool_columns[index % 2].code(declaration["name"], language=None)
st.sidebar.caption(
    f"Prompt `{artifact_version.prompt_hash[:8]}` · Tools `{artifact_version.tools_hash[:8]}`"
)

if st.sidebar.button("🗑️ Cuộc trò chuyện mới", disabled=bool(st.session_state.get("pending_send"))):
    st.session_state["history"] = []
    st.session_state["transcript"] = None
    st.rerun()

st.markdown(
    """
    <div class="hero">
      <div class="small-label">Research Agent · Tool Evaluation Lab</div>
      <h1>Trợ lý nghiên cứu</h1>
      <p>Tìm kiếm web, bài báo khoa học, nội dung mạng xã hội và chính sách nội bộ — có hiển thị công cụ đã dùng.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

info_columns = st.columns(3)
info_columns[0].metric("Provider", provider_name.title())
info_columns[1].metric("Version", version or "chưa đặt")
info_columns[2].metric("Tools sẵn sàng", len(tool_declarations))

if not st.session_state.get("transcript") or not st.session_state["transcript"]["turns"]:
    st.info(
        "Hãy thử: “Tìm các nghiên cứu gần đây về AI agent và tóm tắt các nguồn đáng tin cậy.”"
    )
else:
    render_conversation()

pending_send = st.session_state.get("pending_send")
if pending_send:
    text_to_send = str(pending_send["event"].get("args", {}).get("text", ""))
    st.warning(
        "Agent đang yêu cầu gửi nội dung qua Telegram. Hãy kiểm tra kỹ nội dung bên dưới; "
        "không có tin nhắn nào được gửi cho đến khi bạn bấm xác nhận."
    )
    with st.container(border=True):
        st.markdown("**Nội dung chính xác sẽ gửi**")
        st.text(text_to_send or "(trống)")
    confirm_col, cancel_col = st.columns(2)
    if confirm_col.button(
        "Xác nhận gửi nội dung này",
        type="primary",
        disabled=not text_to_send.strip(),
        use_container_width=True,
    ):
        send_result = TOOL_FUNCTIONS["send"](
            **{**pending_send["event"].get("args", {}), "confirmed": True}
        )
        send_event = {
            "tool": "send",
            "args": {**pending_send["event"].get("args", {}), "confirmed": True},
            "result": send_result,
        }
        turn = st.session_state["transcript"]["turns"][pending_send["turn_index"]]
        update_pending_event(turn, send_event)
        turn["status"] = "answered" if send_result.get("status") == "sent" else "tool_error"
        turn["assistant_text"] = (
            "Đã gửi nội dung đến Telegram."
            if send_result.get("status") == "sent"
            else f"Không gửi được nội dung: {send_result.get('message', send_result)}"
        )
        st.session_state["history"].append(
            {"role": "assistant", "content": turn["assistant_text"]}
        )
        st.session_state["pending_send"] = None
        save_current_transcript()
        st.rerun()
    if cancel_col.button("Hủy gửi", use_container_width=True):
        turn = st.session_state["transcript"]["turns"][pending_send["turn_index"]]
        cancelled_event = {
            "tool": "send",
            "args": pending_send["event"].get("args", {}),
            "result": {"status": "cancelled", "message": "User cancelled the send action."},
        }
        update_pending_event(turn, cancelled_event)
        turn["status"] = "action_cancelled"
        turn["assistant_text"] = "Đã hủy thao tác gửi."
        st.session_state["history"].append(
            {"role": "assistant", "content": turn["assistant_text"]}
        )
        st.session_state["pending_send"] = None
        save_current_transcript()
        st.rerun()

user_text = st.chat_input(
    "Bạn muốn nghiên cứu điều gì?",
    disabled=bool(st.session_state.get("pending_send")),
)
if user_text:
    if st.session_state.get("transcript") is None:
        st.session_state["transcript"] = start_transcript(
            provider_name,
            model or default_model,
            version,
            artifact_version_dict(artifact_version),
            history_window,
            max_tool_rounds,
        )

    transcript = st.session_state["transcript"]
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state["history"], history_window),
        {"role": "user", "content": user_text},
    ]

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=max_tool_rounds,
            tool_call_guard=lambda call: call.name != "send",
        )
        turn_record.update(result)
        st.session_state["history"].append({"role": "user", "content": user_text})
        if result.get("status") == "waiting_for_confirmation":
            st.session_state["pending_send"] = {
                "turn_index": len(transcript["turns"]),
                "event": result["pending_tool_event"],
            }
        else:
            st.session_state["history"].append(
                {"role": "assistant", "content": result.get("assistant_text", "")}
            )
    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {exc}",
        })

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    save_current_transcript()
    st.rerun()

if st.session_state.get("transcript") and st.session_state["transcript"]["turns"]:
    st.sidebar.download_button(
        "Tải transcript JSON",
        data=json.dumps(st.session_state["transcript"], ensure_ascii=False, indent=2),
        file_name=f"{st.session_state['transcript']['transcript_id']}.transcript.json",
        mime="application/json",
        use_container_width=True,
    )
