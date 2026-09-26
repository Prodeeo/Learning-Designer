import os
import json
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="AI Learning Experience Designer",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI Learning Experience Designer")
st.markdown(
    "Design a technology-enhanced learning experience using **TPACK, SAMR, RAT, and PICRAT**."
)

# -----------------------------
# API configuration
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.warning(
        "Groq API key not found. Add `GROQ_API_KEY` to your environment variables "
        "or Streamlit secrets."
    )

# -----------------------------
# Input form
# -----------------------------
with st.form("learning_design_form"):
    st.subheader("Learning Experience Inputs")

    topic = st.text_input(
        "Topic",
        placeholder="e.g., Generative AI for Teachers",
    )

    audience = st.text_input(
        "Audience",
        placeholder="e.g., Higher education faculty",
    )

    duration = st.text_input(
        "Duration",
        placeholder="e.g., 2 hours",
    )

    delivery_mode = st.selectbox(
        "Delivery Mode",
        [
            "Face-to-face",
            "Online synchronous",
            "Online asynchronous",
            "Blended / Hybrid",
            "Flipped classroom",
        ],
    )

    learning_objective = st.text_area(
        "Learning Objective",
        placeholder=(
            "By the end of the session, learners will be able to..."
        ),
        height=100,
    )

    submitted = st.form_submit_button(
        "✨ Generate Learning Experience",
        type="primary",
        use_container_width=True,
    )

# -----------------------------
# Prompt
# -----------------------------
def build_prompt(topic, audience, duration, delivery_mode, objective):
    return f"""
You are an expert Learning Experience Designer, instructional designer,
teacher educator, and educational technology specialist.

Design a practical technology-enhanced learning experience using the
information below.

TOPIC:
{topic}

AUDIENCE:
{audience}

DURATION:
{duration}

DELIVERY MODE:
{delivery_mode}

LEARNING OBJECTIVE:
{objective}

Use the following frameworks accurately:

1. TPACK
Explain the relevant:
- Content Knowledge (CK)
- Pedagogical Knowledge (PK)
- Technological Knowledge (TK)
- Pedagogical Content Knowledge (PCK)
- Technological Content Knowledge (TCK)
- Technological Pedagogical Knowledge (TPK)
- TPACK integration

2. SAMR
Place the learning experience across:
- Substitution
- Augmentation
- Modification
- Redefinition
Explain why the proposed technology use fits each level and identify
the most appropriate target level.

3. RAT
Analyze technology use as:
- Replacement
- Amplification
- Transformation
Explain the pedagogical value of the selected level.

4. PICRAT
Use both dimensions:
Student relationship with technology:
- Passive
- Interactive
- Creative

Teacher use of technology:
- Replacement
- Amplification
- Transformation

Identify the most appropriate PICRAT position and explain it.

5. ACTIVITIES
Create a practical sequence of activities suitable for the duration.
For each activity provide:
- Time
- Activity
- Teacher/facilitator role
- Learner role
- Technology/tool
- Expected output

6. ASSESSMENT
Create:
- Formative assessment
- Summative assessment
- Assessment criteria / rubric
Make sure assessment aligns with the learning objective.

7. REFLECTION
Provide 4-6 reflective questions for learners and 3-4 questions for
the teacher/facilitator after the session.

IMPORTANT:
- Keep the design realistic and usable by a teacher/facilitator.
- Do not use technology merely because it is available.
- Prioritize pedagogy and learning outcomes.
- Clearly explain how technology improves the learning experience.
- Avoid inventing specific product capabilities.
- Use concise tables where useful.
- Make the final response practical enough to use directly in a lesson plan.

Return the answer as valid JSON with exactly these top-level keys:
tpack, samr, rat, picrat, activities, assessment, reflection

Do not include markdown fences around the JSON.
"""

# -----------------------------
# Generate
# -----------------------------
if submitted:
    if not all(
        [
            topic.strip(),
            audience.strip(),
            duration.strip(),
            learning_objective.strip(),
        ]
    ):
        st.error("Please complete Topic, Audience, Duration, and Learning Objective.")
        st.stop()

    if not api_key:
        st.error(
            "Please configure your Groq API key before generating the learning experience."
        )
        st.stop()

    try:
        client = Groq(api_key=api_key)

        with st.spinner("Designing your learning experience..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert instructional designer. "
                            "Return accurate, practical, structured learning designs."
                        ),
                    },
                    {
                        "role": "user",
                        "content": build_prompt(
                            topic,
                            audience,
                            duration,
                            delivery_mode,
                            learning_objective,
                        ),
                    },
                ],
                temperature=0.4,
                response_format={"type": "json_object"},
            )

        raw_output = response.choices[0].message.content
        result = json.loads(raw_output)

        st.success("Learning experience generated successfully!")

        # -----------------------------
        # Output sections
        # -----------------------------
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            [
                "TPACK",
                "SAMR",
                "RAT",
                "PICRAT",
                "Activities",
                "Assessment",
                "Reflection",
            ]
        )

        with tab1:
            st.header("TPACK")
            st.write(result.get("tpack", ""))

        with tab2:
            st.header("SAMR")
            st.write(result.get("samr", ""))

        with tab3:
            st.header("RAT")
            st.write(result.get("rat", ""))

        with tab4:
            st.header("PICRAT")
            st.write(result.get("picrat", ""))

        with tab5:
            st.header("Activities")
            st.write(result.get("activities", ""))

        with tab6:
            st.header("Assessment")
            st.write(result.get("assessment", ""))

        with tab7:
            st.header("Reflection")
            st.write(result.get("reflection", ""))

        # Download complete design as JSON
        download_data = json.dumps(result, indent=2, ensure_ascii=False)

        st.download_button(
            label="⬇️ Download Learning Design (JSON)",
            data=download_data,
            file_name="ai_learning_experience_design.json",
            mime="application/json",
        )

        # Also show the complete generated response
        with st.expander("View complete generated design"):
            st.json(result)

    except Exception as e:
        st.error(f"Something went wrong while generating the design: {e}")

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "AI Learning Experience Designer • Powered by Streamlit and Groq"
)
