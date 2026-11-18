import streamlit as st
from google import genai

# পেজ কনফিগারেশন এবং কাস্টম থিম (Sharp Blue, Black, White Mix)
st.set_page_config(
    page_title="Judge Yourself - EFAZ", page_icon="💡", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b132b, #1c2541, #3a506b);
        color: #ffffff;
    }
    .brand-container {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px 0;
        border-bottom: 2px solid #5bc0be;
        margin-bottom: 20px;
    }
    .main-logo-text {
        font-size: 28px;
        font-weight: bold;
        color: #6fffe9;
        letter-spacing: 1px;
    }
    .sub-logo-badge {
        background-color: #5bc0be;
        color: #0b132b;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    </style>
    
    <div class="brand-container">
        <div class="main-logo-text">🎯 Judge Yourself</div>
        <div class="sub-logo-badge">EFAZ</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "bookmarked_questions" not in st.session_state:
  st.session_state.bookmarked_questions = []
if "exam_submitted" not in st.session_state:
  st.session_state.exam_submitted = False

st.subheader("🚀 স্মার্ট অনলাইন এক্সাম এবং এআই ক্যুইজ প্ল্যাটফর্ম")

st.sidebar.header("⚙️ সেটিংস ও মেনু")
api_key = st.sidebar.text_input(
    "আপনার Gemini API Key এখানে দিন:", type="password"
)
menu = st.sidebar.selectbox(
    "মেনু নির্বাচন করুন:",
    ["নতুন পরীক্ষা তৈরি (Create Exam)", "সংরক্ষিত কঠিন ও ভুল প্রশ্ন (Bookmarks)"],
)

if menu == "নতুন পরীক্ষা তৈরি (Create Exam)":
  st.subheader("📖 পিডিএফ বা বইয়ের ছবি থেকে এক্সাম কনফিগার করুন")
  subject_name = st.text_input("সাবজেক্টের নাম:", value="জীববিজ্ঞান")
  chapter_name = st.text_input(
      "অধ্যায়ের নাম বা নম্বর (যেমন: অধ্যায় ৫ - খাদ্য ও পুষ্টি):"
  )
  uploaded_files = st.file_uploader(
      "বই/নোটের ছবি বা পেজগুলো আপলোড করুন:",
      type=["jpg", "jpeg", "png", "pdf"],
      accept_multiple_files=True,
  )

  col1, col2 = st.columns(2)
  with col1:
    num_questions = st.slider("প্রশ্নের সংখ্যা:", 5, 40, 15, 5)
  with col2:
    exam_time = st.slider("পরীক্ষার সময় (মিনিট):", 1, 60, 10)

  if st.button("🔥 পরীক্ষা শুরু করুন (Generate Exam)") and api_key:
    if not uploaded_files:
      st.warning("দয়া করে অন্তত একটি ফাইল বা ছবি আপলোড করুন।")
    else:
      with st.spinner(
          "এআই ডেটা বিশ্লেষণ করে কঠিন ও মিক্সড প্রশ্ন তৈরি করছে..."
      ):
        try:
          client = genai.Client(api_key=api_key)
          prompt = f"""
                    নিচে দেওয়া ফাইল/ছবিগুলো হলো {subject_name}-এর {chapter_name} এর অংশ। 
                    এই তথ্যগুলো ব্যবহার করে মোট {num_questions} টি অত্যন্ত **কঠিন ও স্ট্যান্ডার্ড (Standard/Hard level)** বহুনির্বাচনী প্রশ্ন (MCQ) তৈরি করো।
                    নির্দেশনা:
                    ১. প্রশ্নগুলো ধারাবাহিক বা ছবির সিরিয়াল অনুযায়ী না দিয়ে সম্পূর্ণ এলোমেলো বা মিক্সড (Random/Mixed) আকারে সাজাবে।
                    ২. প্রতিটি প্রশ্নের ৪টি অপশন (ক, খ, গ, ঘ) থাকবে।
                    ৩. সঠিক উত্তর এবং শিক্ষণীয় ব্যাখ্যা নিচে যুক্ত করবে।
                    """
          contents_list = list(uploaded_files) + [prompt]
          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=contents_list
          )
          st.session_state.raw_quiz_text = response.text
          st.session_state.exam_submitted = False
          st.success("পরীক্ষা সফলভাবে তৈরি হয়েছে!")
        except Exception as e:
          st.error(f"ত্রুটি ঘটেছে: {e}")

  if "raw_quiz_text" in st.session_state and not st.session_state.exam_submitted:
    st.markdown("---")
    st.header(f"📝 {subject_name} - লাইভ পরীক্ষা")
    st.info(f"নির্ধারিত সময়: {exam_time} মিনিট।")
    with st.form("exam_form"):
      st.markdown(st.session_state.raw_quiz_text)
      st.markdown("---")
      mark_difficult = st.checkbox(
          "এই পরীক্ষার প্রশ্নগুলো কঠিন মনে হলে বুকমার্ক বা সেভ করে রাখুন"
      )
      submitted = st.form_submit_button("পরীক্ষা জমা দিন (Submit Exam)")
      if submitted:
        if mark_difficult:
          st.session_state.bookmarked_questions.append(
              f"{subject_name} - {chapter_name} (কঠিন প্রশ্ন)"
          )
        st.session_state.exam_submitted = True
        st.rerun()

  elif (
      "raw_quiz_text" in st.session_state and st.session_state.exam_submitted
  ):
    st.success("🎉 আপনার পরীক্ষা সফলভাবে জমা হয়েছে!")
    st.subheader("💡 ফলাফল ও শিক্ষকসুলভ উপদেশ:")
    st.markdown("""
        > **শিক্ষকের মূল্যবান উপদেশ (EFAZ Platform):** 
        > *"সাফল্য একদিনে আসে না। যে প্রশ্নগুলোতে ভুল করেছ বা যেগুলো তোমার কাছে কঠিন মনে হয়েছে, সেগুলোর ব্যাখ্যা বারবার রিভিশন দাও। তোমার লক্ষ্য স্থির রাখো এবং নিয়মিত অনুশীলন করো, সফলতা অবশ্যই আসবে!"*
        """)
    if st.button("পুনরায় নতুন পরীক্ষা দিন"):
      del st.session_state.raw_quiz_text
      st.session_state.exam_submitted = False
      st.rerun()

elif menu == "সংরক্ষিত কঠিন ও ভুল প্রশ্ন (Bookmarks)":
  st.subheader("📌 আপনার সংরক্ষিত কঠিন ও ভুল প্রশ্নসমূহ")
  if not st.session_state.bookmarked_questions:
    st.info("এখনো কোনো প্রশ্ন বুকমার্ক বা সেভ করা হয়নি।")
  else:
    for i, q in enumerate(st.session_state.bookmarked_questions):
      st.markdown(f"**সংরক্ষিত আইটেম {i+1}:** {q}")
