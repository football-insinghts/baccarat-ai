import hashlib
import hmac
import logging
import time
from pathlib import Path

import streamlit as st
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
from scanner import prepare_image, stream_analysis
from app_settings import load_settings

ROOT = Path(__file__).resolve().parent
st.set_page_config(
    page_title="Global BAR | AI Vision Scanner",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown("<style>" + (ROOT / "ui.css").read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)


def brand():
    if (ROOT / "logo.png").exists():
        st.image(str(ROOT / "logo.png"), width=64)
    st.markdown("""
    <div class="brand">
        <div class="brand-mark" aria-hidden="true">◈</div>
        <div><div class="brand-name">GLOBAL BAR</div>
        <div class="brand-sub">วิเคราะห์ด้วยระบบ AI</div></div>
        <div class="brand-badge">VIP MEMBER</div>
    </div>
    """, unsafe_allow_html=True)


def footer():
    st.markdown("""
    <div class="app-footer"><span>AI Vision · Powered by GLOBAL BAR</span>
    <span>วิเคราะห์จากภาพที่อัปโหลด · ผลลัพธ์อาจคลาดเคลื่อน</span></div>
    """, unsafe_allow_html=True)


def check_password():
    if st.session_state.get("password_correct", False):
        return True
    _, center, _ = st.columns([1, 1.25, 1])
    with center:
        brand()
        with st.container(border=True):
            st.markdown('<div class="eyebrow">MEMBER ACCESS</div><div class="login-heading">ยินดีต้อนรับกลับ</div><div class="section-copy">เข้าสู่พื้นที่วิเคราะห์ภาพของคุณ<br>กรอกรหัสผ่านสมาชิกเพื่อเริ่มใช้งาน</div>', unsafe_allow_html=True)
            with st.form("login"):
                password = st.text_input("รหัสผ่านสมาชิก", type="password", placeholder="กรอกรหัสผ่านของคุณ", key="password")
                submitted = st.form_submit_button("เข้าสู่ระบบ  →", type="primary", use_container_width=True)
            if submitted:
                if hmac.compare_digest(password.encode("utf-8"), SETTINGS["APP_PASSWORD"].encode("utf-8")):
                    st.session_state["password_correct"] = True
                    st.session_state.pop("password", None)
                    st.rerun()
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบและลองอีกครั้ง")
            st.caption("สำหรับสมาชิก VIP Global BAR · กรอกรหัสผ่านเพื่อเข้าสู่ระบบ")
        footer()
    return False


def main():
    brand()
    st.markdown('<div class="eyebrow">BACCARAT · IMAGE ANALYSIS</div>', unsafe_allow_html=True)
    st.title("วิเคราะห์สุดโหด ด้วย AI")
    st.markdown('<p class="intro">อัปโหลดภาพตารางเค้าไพ่ แล้วให้ AI ช่วยอ่านและสรุปข้อมูล<br>ทุกขั้นตอนอยู่ในพื้นที่เดียว ใช้งานง่าย พร้อมอ่านผลได้ทันที</p>', unsafe_allow_html=True)
    st.markdown('<div class="steps"><span><b class="step-num">01</b>อัปโหลดภาพ</span><span><b class="step-num">02</b>เริ่มวิเคราะห์</span><span><b class="step-num">03</b>อ่านผลสรุป</span></div>', unsafe_allow_html=True)

    upload_col, result_col = st.columns([1, 1.25], gap="large")
    image = None
    image_id = None
    with upload_col:
        with st.container(border=True):
            st.markdown('<div class="section-label">01 / UPLOAD</div><div class="section-title">เพิ่มภาพตารางเค้าไพ่</div><div class="section-copy">เลือกภาพแคปหน้าจอที่เห็นชื่อโต๊ะและตารางชัดเจน</div>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("อัปโหลดภาพ JPG หรือ PNG", type=["jpg", "jpeg", "png"], help="รองรับไฟล์ JPG, JPEG และ PNG ขนาดไม่เกิน 10 MB")
            if uploaded_file is not None:
                image_id = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
                try:
                    image = Image.open(uploaded_file)
                    image.load()
                    st.image(image, caption="ภาพที่เลือก · พร้อมวิเคราะห์", use_container_width=True)
                except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                    image = None
                    st.error("เปิดภาพนี้ไม่ได้ กรุณาเลือกไฟล์ JPG หรือ PNG ที่สมบูรณ์")
            if st.session_state.get("analysis_image_id") != image_id:
                st.session_state.pop("analysis", None)
                st.session_state.pop("analysis_error", None)
            scan = st.button("เริ่มวิเคราะห์ภาพ  →", type="primary", use_container_width=True, disabled=image is None)
            regenerate = False
            if image is not None and st.session_state.get("analysis"):
                regenerate = st.button("วิเคราะห์ภาพนี้ใหม่", use_container_width=True)
                st.caption("ปุ่มเริ่มวิเคราะห์ใช้ผลเดิมของภาพนี้ได้ทันที หากต้องการคำตอบใหม่ให้เลือกวิเคราะห์ภาพนี้ใหม่")
            st.markdown('<div class="tip"><strong>เพื่อให้ AI อ่านภาพได้ชัดเจน</strong><br>ใช้ภาพเต็มตาราง ตัวอักษรไม่เบลอ และหลีกเลี่ยงภาพที่มีข้อความบัง</div>', unsafe_allow_html=True)

    with result_col:
        with st.container(border=True):
            st.markdown('<div class="section-label">02 / ANALYSIS</div><div class="section-title">ผลการวิเคราะห์</div><div class="section-copy">สรุปข้อมูลจากภาพด้วย AI Vision</div>', unsafe_allow_html=True)
            model_name = SETTINGS["GEMINI_MODEL"]
            request_id = hashlib.sha256((str(image_id) + model_name + ANALYSIS_PROMPT).encode()).hexdigest()
            reuse_result = st.session_state.get("analysis_request_id") == request_id and bool(st.session_state.get("analysis"))
            if (scan or regenerate) and image is not None and (regenerate or not reuse_result):
                st.session_state.pop("analysis", None)
                st.session_state.pop("analysis_error", None)
                st.session_state.pop("analysis_metrics", None)
                st.session_state["analysis_image_id"] = image_id
                partial = st.empty()
                progress = st.empty()
                with st.spinner("กำลังอ่านภาพ คำตอบจะแสดงทันทีที่ AI เริ่มตอบ..."):
                    try:
                        started = time.perf_counter()
                        configure_ai()
                        payload = prepare_image(uploaded_file.getvalue(), image)
                        model = genai.GenerativeModel(model_name)
                        chunks = []
                        first_text_seconds = None
                        last_render = 0.0
                        for text in stream_analysis(model, payload, ANALYSIS_PROMPT):
                            now = time.perf_counter()
                            if first_text_seconds is None:
                                first_text_seconds = now - started
                                progress.caption(f"เริ่มแสดงคำตอบใน {first_text_seconds:.1f} วินาที · กำลังรับข้อมูลต่อ...")
                            chunks.append(text)
                            if now - last_render >= 0.15:
                                partial.markdown("".join(chunks) + " ▌")
                                last_render = now
                        result = "".join(chunks)
                        if not result.strip():
                            raise ValueError("Empty analysis")
                        st.session_state["analysis"] = result
                        st.session_state["analysis_request_id"] = request_id
                        st.session_state["analysis_metrics"] = {
                            "first_text": first_text_seconds,
                            "total": time.perf_counter() - started,
                            "original_bytes": len(uploaded_file.getvalue()),
                            "sent_bytes": len(payload["data"]),
                        }
                    except Exception:
                        st.session_state["analysis_error"] = True
                    finally:
                        partial.empty()
                        progress.empty()
            if st.session_state.get("analysis_error"):
                st.error("วิเคราะห์ไม่สำเร็จ กรุณาลองอีกครั้ง หากยังพบปัญหา ให้แจ้ง ADMIN")
            elif st.session_state.get("analysis"):
                st.success("วิเคราะห์ภาพเรียบร้อยแล้ว")
                metrics = st.session_state.get("analysis_metrics")
                if metrics:
                    st.caption(f"ข้อความแรก {metrics['first_text']:.1f} วินาที · เสร็จทั้งหมด {metrics['total']:.1f} วินาที")
                st.markdown(st.session_state["analysis"])
                st.download_button("ดาวน์โหลดผลสรุป", st.session_state["analysis"], file_name="global-bar-analysis.txt", mime="text/plain", use_container_width=True)
            else:
                title = "ภาพพร้อมแล้ว เริ่มวิเคราะห์ได้เลย" if image is not None else "ผลสรุปของคุณจะแสดงที่นี่"
                copy = "กดปุ่มเริ่มวิเคราะห์ภาพ แล้วรอผลสรุปสักครู่" if image is not None else "อัปโหลดภาพตารางเค้าไพ่ทางด้านซ้าย<br>แล้วกดเริ่มวิเคราะห์เพื่อดูผลสรุป"
                st.markdown(f'<div class="empty-result"><div class="empty-icon" aria-hidden="true">▧</div><div class="empty-title">{title}</div><div class="empty-copy">{copy}</div></div>', unsafe_allow_html=True)
    footer()


def configure_ai():
    genai.configure(api_key=SETTINGS["GOOGLE_API_KEY"])

ANALYSIS_PROMPT = """
                    คุณคือเซียนวิเคราะห์บาคาร่ามืออาชีพระดับ VIP ของกลุ่ม Global BAR
                    หน้าที่ของคุณคือวิเคราะห์ภาพตารางเค้าไพ่หลายโต๊ะ (เช่น โต๊ะ A, B, C, D...) ที่ผู้ใช้ส่งมา และจัดทำรายงานการวิเคราะห์ดังนี้:
                    🎯 1. โต๊ะที่น่าเล่นที่สุด: ระบุชื่อโต๊ะ พร้อมอธิบายลักษณะเค้าไพ่
                    📊 2. การประเมินคะแนน & Win Rate: ให้คะแนนความสวยงามและเปอร์เซ็นต์ความน่าจะเป็น (%)
                    🔮 3. การจำลองผลลัพธ์ 20 ไม้ถัดไป: จำลองผลลัพธ์ล่วงหน้า 20 ไม้ แยกเป็นข้อๆ โดยใช้คำว่า "🔴 แดง" หรือ "🔵 น้ำเงิน" เท่านั้น
                    💡 4. คำแนะนำการเดินเงิน: แนวทางการวางเงินเพื่อความปลอดภัย
                    โทนเสียง: เป็นกันเอง สไตล์เซียนบาคาร่าใจดีที่แนะนำสมาชิก VIP
                    """

try:
    SETTINGS = load_settings(st.secrets)
except (FileNotFoundError, KeyError, ValueError) as error:
    logging.getLogger(__name__).error("App configuration unavailable: %s", error)
    st.error("ระบบยังไม่พร้อมใช้งาน กรุณาแจ้งผู้ดูแลระบบเพื่อตรวจสอบการตั้งค่า")
    st.stop()

if check_password():
    main()
