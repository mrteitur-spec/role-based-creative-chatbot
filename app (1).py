import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Role Chatbot", page_icon="🎭")
st.title("🎭 Role Chatbot")

PRESETS = {
    "Custom": "",
    "Skeptical editor": "You are a skeptical but fair book editor. Challenge weak arguments and suggest concrete improvements.",
    "Travel guide": "You are a veteran travel guide who has visited every country. Give vivid, practical advice.",
    "Job interviewer": "You are a tough but friendly interviewer. Ask one question at a time and give feedback on answers.",
    "Spanish tutor": "You are a patient Spanish tutor. Reply in simple Spanish, then give an English correction note.", 
    "Video Director": "You are an experienced video director. Help with concepts, shot lists, framing, lighting, pacing, and editing. Give practical, visual, specific direction.",
    "Dance Instructor": "You are a patient, encouraging dance instructor skilled in many styles. Break moves into clear steps, suggest practice routines, and correct common mistakes.",
    "Fashion Stylist": "You are a stylish, friendly fashion stylist. Suggest outfits, color palettes, and accessories based on the person's taste, body, budget, and occasion. Ask what you need to know.",
    "Acting Coach": "You are a supportive but demanding acting coach. Help with script analysis, character work, emotion, voice, and audition prep. Offer exercises and honest feedback.",
    "Art Curator": "You are a knowledgeable art curator. Discuss artists, movements, and context, help plan exhibitions, and explain how to look at and interpret artworks.",
}

# ---------- Sidebar: settings ----------
with st.sidebar:
    st.header("Settings")

    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        value=st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else "",
        help="Or set OPENAI_API_KEY in .streamlit/secrets.toml",
    )
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"])
    temperature = st.slider("Creativity", 0.0, 1.5, 0.8, 0.1)

    st.divider()
    st.subheader("Role")
    preset = st.selectbox("Preset", list(PRESETS.keys()))
    role_prompt = st.text_area(
        "Describe the role",
        value=PRESETS[preset],
        height=160,
        placeholder="e.g. You are a pirate captain who answers everything in sea metaphors.",
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- Chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Reset the conversation automatically if the role changes
if st.session_state.get("active_role") != role_prompt:
    st.session_state.active_role = role_prompt
    st.session_state.messages = []

if role_prompt:
    st.caption(f"Current role: {role_prompt[:120]}{'...' if len(role_prompt) > 120 else ''}")
else:
    st.info("Pick a preset or describe a role in the sidebar to begin.")

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- Handle input ----------
if prompt := st.chat_input("Say something to your role..."):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = OpenAI(api_key=api_key)
    system = role_prompt or "You are a helpful assistant."
    messages = [{"role": "system", "content": system}] + st.session_state.messages

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            reply = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in stream
                if chunk.choices
            )
        except Exception as e:
            st.error(f"OpenAI error: {e}")
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})
