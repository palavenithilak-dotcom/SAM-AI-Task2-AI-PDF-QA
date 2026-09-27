import re
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="AI PDF Question Answering", page_icon="📄", layout="centered")

st.title("📄 AI PDF Question Answering")
st.write("Upload a PDF and ask questions related to its content.")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

def extract_pages(file):
    reader = PdfReader(file)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((i, text))
    return pages

def answer_question(pages, question):
    question_words = set(
        w for w in re.findall(r"\b[a-zA-Z]{3,}\b", question.lower())
        if w not in {"what", "when", "where", "which", "who", "does", "this", "that", "from", "about"}
    )

    candidates = []
    for page_no, text in pages:
        sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            words = set(re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower()))
            score = len(question_words & words)
            if score:
                candidates.append((score, page_no, sentence))

    candidates.sort(key=lambda x: x[0], reverse=True)

    if not candidates:
        return None

    selected = []
    seen = set()
    for score, page_no, sentence in candidates:
        key = sentence.lower()
        if key not in seen:
            selected.append((page_no, sentence))
            seen.add(key)
        if len(selected) == 3:
            break

    return selected

if uploaded_file:
    pages = extract_pages(uploaded_file)
    total_chars = sum(len(text) for _, text in pages)

    st.success(f"PDF uploaded successfully — {len(pages)} page(s) read.")

    question = st.text_input(
        "Ask a question about the PDF",
        placeholder="Example: What is this document about?"
    )

    if st.button("🔎 Get Answer", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        elif total_chars == 0:
            st.error("No selectable text could be extracted from this PDF.")
        else:
            result = answer_question(pages, question)

            if result:
                st.subheader("Answer")
                answer_text = " ".join(sentence for _, sentence in result)
                st.success(answer_text)

                st.subheader("Context")
                for page_no, sentence in result:
                    st.write(f"**Page {page_no}:** {sentence}")
            else:
                st.info("No relevant answer was found in the uploaded PDF. Try using keywords from the document.")
else:
    st.info("Upload a PDF to begin.")
