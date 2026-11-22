import streamlit as st
import requests
import re
from resume_parser import extract_text_from_pdf, extract_claimed_skills
from github_fetcher import get_user_public_repos, get_repo_deep_context

st.set_page_config(page_title="Dev Proof-of-Work Verifier", page_icon="🌲", layout="wide")

# --- CUSTOM CSS: ANIMATED LIVING FOREST BACKGROUND ---
st.markdown("""
    <style>
        /* Base app background */
        .stApp {
            background: linear-gradient(180deg, #050d09 0%, #091a12 50%, #040a07 100%);
            color: #d8f3dc;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            overflow-x: hidden;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: rgba(7, 18, 13, 0.9) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid #1b4332;
        }
        [data-testid="stSidebar"] * {
            color: #d8f3dc !important;
        }

        /* SILUET POHON PINUS LATAR BELAKANG */
        .forest-layer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100vw;
            height: 280px;
            pointer-events: none;
            z-index: 0;
            opacity: 0.35;
            background-repeat: repeat-x;
            background-position: bottom center;
        }
        
        /* Lapisan pohon belakang (lebih gelap & berkabut) */
        .trees-back {
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" preserveAspectRatio="none"><path fill="%230b1e16" d="M0,300 L0,220 L30,170 L40,190 L70,130 L80,150 L110,90 L120,110 L150,70 L180,120 L210,180 L230,140 L260,80 L290,150 L320,210 L350,160 L380,100 L410,170 L440,220 L480,150 L510,80 L540,160 L570,220 L610,140 L640,90 L670,160 L700,230 L740,170 L770,110 L800,180 L830,240 L880,160 L910,90 L940,170 L980,230 L1020,150 L1050,70 L1080,160 L1120,220 L1160,160 L1200,110 L1200,300 Z"/></svg>');
            height: 320px;
            animation: treeSway 12s ease-in-out infinite alternate;
        }

        /* Lapisan pohon depan */
        .trees-front {
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" preserveAspectRatio="none"><path fill="%2306120c" d="M0,300 L0,250 L20,200 L50,150 L80,210 L110,130 L140,220 L170,180 L200,120 L230,190 L270,140 L310,240 L350,170 L390,110 L430,200 L470,260 L510,180 L550,120 L590,210 L630,260 L670,190 L710,130 L750,220 L790,260 L830,180 L870,110 L910,190 L950,250 L990,170 L1030,100 L1070,210 L1110,260 L1150,190 L1200,140 L1200,300 Z"/></svg>');
            opacity: 0.55;
            animation: treeSway 8s ease-in-out infinite alternate-reverse;
        }

        @keyframes treeSway {
            0% { transform: scaleY(1) translateY(0); }
            50% { transform: scaleY(1.02) translateY(-4px); }
            100% { transform: scaleY(1) translateY(0); }
        }

        /* ANIMASI KUNANG-KUNANG / CAHAYA SPORA HUTAN */
        .firefly {
            position: fixed;
            width: 4px;
            height: 4px;
            background: #9ef01a;
            border-radius: 50%;
            box-shadow: 0 0 10px #70e000, 0 0 20px #38b000;
            pointer-events: none;
            z-index: 1;
            animation: rise 10s infinite linear;
            opacity: 0;
        }
        .f1 { left: 15%; animation-duration: 8s; animation-delay: 0s; }
        .f2 { left: 35%; animation-duration: 11s; animation-delay: 2s; width: 5px; height: 5px; background: #ccff33; }
        .f3 { left: 55%; animation-duration: 9s; animation-delay: 4s; }
        .f4 { left: 75%; animation-duration: 12s; animation-delay: 1s; width: 6px; height: 6px; }
        .f5 { left: 90%; animation-duration: 10s; animation-delay: 3s; }
        .f6 { left: 25%; animation-duration: 13s; animation-delay: 5s; }

        @keyframes rise {
            0% { transform: translateY(105vh) translateX(0); opacity: 0; }
            20% { opacity: 0.9; }
            80% { opacity: 0.8; }
            100% { transform: translateY(-10vh) translateX(50px); opacity: 0; }
        }

        /* CARD GLASSMORPHISM UNTUK KONTEN */
        [data-testid="stMetric"] {
            background: rgba(14, 34, 25, 0.7) !important;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(82, 183, 136, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
            position: relative;
            z-index: 2;
        }
        [data-testid="stMetricValue"] {
            color: #95d5b2 !important;
            font-weight: 700 !important;
            font-size: 2.3rem !important;
            text-shadow: 0 0 12px rgba(82, 183, 136, 0.4);
        }
        [data-testid="stMetricLabel"] {
            color: #b7e4c7 !important;
            font-size: 0.95rem !important;
        }

        /* TOMBOL HIJAU HUTAN BERCORAK EMERALD */
        .stButton > button {
            background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important;
            color: #ffffff !important;
            border: 1px solid #52b788 !important;
            border-radius: 10px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            box-shadow: 0 6px 20px rgba(45, 106, 79, 0.5) !important;
            transition: all 0.25s ease-in-out !important;
            position: relative;
            z-index: 2;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%) !important;
            border-color: #95d5b2 !important;
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(82, 183, 136, 0.6) !important;
        }

        table {
            background-color: rgba(11, 26, 19, 0.75) !important;
            backdrop-filter: blur(8px);
            border: 1px solid #1b4332 !important;
            border-radius: 10px;
            color: #e8f5e9 !important;
            position: relative;
            z-index: 2;
        }
        th {
            background-color: #1b4332 !important;
            color: #d8f3dc !important;
        }
        td {
            border-bottom: 1px solid #163628 !important;
        }
        a {
            color: #74c69d !important;
            font-weight: 500;
        }
    </style>

    <!-- ELEMEN ANIMASI DI LATAR BELAKANG -->
    <div class="forest-layer trees-back"></div>
    <div class="forest-layer trees-front"></div>
    <div class="firefly f1"></div>
    <div class="firefly f2"></div>
    <div class="firefly f3"></div>
    <div class="firefly f4"></div>
    <div class="firefly f5"></div>
    <div class="firefly f6"></div>
""", unsafe_allow_html=True)

# --- HEADER UTAMA ---
st.title("🌲 Dev Proof-of-Work Verifier")
st.caption("🍃 Verifikasi klaim teknis CV berbasis repositori GitHub dengan Deep Ecosystem Inspection.")

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("🌿 Panel Parameter")
    github_user = st.text_input("GitHub Username", value="sulthanrunvarg-wq")
    deep_scan_enabled = st.toggle("🔍 Aktifkan Deep Scan (README & Dependencies)", value=True)
    
    st.divider()
    use_sample = st.checkbox("Gunakan Contoh Teks CV", value=True)
    uploaded_pdf = None
    sample_text = ""
    
    if not use_sample:
        uploaded_pdf = st.file_uploader("Upload CV (PDF)", type=["pdf"])
    else:
        sample_text = st.text_area(
            "Isi Contoh CV:",
            value="Sulthan - AI & Software Developer\n"
                  "Skills: Python, Streamlit, PyTorch, Git, Docker, PostgreSQL, React, Linux.\n"
                  "Projects: Built a Sketch-Guided Doodle-to-Art Diffusion Studio using Python and Streamlit.",
            height=130
        )
    
    run_btn = st.button("🚀 Audit & Verifikasi CV", type="primary")

# --- LOGIKA VERIFIKASI ---
def verify_skills(claimed_skills, repos, repo_contexts):
    results = []
    verified_count = 0
    
    for skill in claimed_skills:
        matched_evidences = []
        pattern = rf"\b{re.escape(skill)}\b"
        
        for repo in repos:
            repo_name = repo["name"]
            lang = repo.get("language") or ""
            desc = repo.get("description") or ""
            context = repo_contexts.get(repo_name, "")
            
            full_repo_corpus = f"{lang} {repo_name} {desc} {context}"
            
            if re.search(pattern, full_repo_corpus, re.IGNORECASE):
                sources = []
                if re.search(pattern, lang, re.IGNORECASE):
                    sources.append("Language")
                if re.search(pattern, f"{repo_name} {desc}", re.IGNORECASE):
                    sources.append("Metadata/Repo")
                if "[README]" in context and re.search(pattern, context.split("[REQUIREMENTS]")[0] if "[REQUIREMENTS]" in context else context, re.IGNORECASE):
                    sources.append("README")
                if "[REQUIREMENTS]" in context and re.search(pattern, context.split("[REQUIREMENTS]")[-1], re.IGNORECASE):
                    sources.append("Dependencies")
                    
                source_tag = f" ({', '.join(sources)})" if sources else ""
                matched_evidences.append(f"[{repo_name}]({repo['html_url']}){source_tag}")
        
        if matched_evidences:
            verified_count += 1
            results.append({
                "Skill": skill,
                "Status": "✅ Terverifikasi",
                "Bukti Repository": ", ".join(matched_evidences)
            })
        else:
            results.append({
                "Skill": skill,
                "Status": "⚠️ Belum Ada Bukti Publik",
                "Bukti Repository": "Tidak ditemukan di repo publik"
            })
            
    score = int((verified_count / len(claimed_skills)) * 100) if claimed_skills else 0
    return results, score, verified_count

# --- MAIN DASHBOARD ---
if run_btn:
    with st.spinner("🌲 Menjelajah ekosistem GitHub kandidat..."):
        cv_text = ""
        if use_sample:
            cv_text = sample_text
        elif uploaded_pdf is not None:
            cv_text = extract_text_from_pdf(uploaded_pdf)
        else:
            st.warning("Silakan upload file PDF atau aktifkan 'Gunakan Contoh Teks CV'.")
            st.stop()
            
        claimed_skills = extract_claimed_skills(cv_text)
        repos = get_user_public_repos(github_user)
        repo_contexts = {}
        if deep_scan_enabled and repos:
            for repo in repos:
                repo_contexts[repo["name"]] = get_repo_deep_context(github_user, repo["name"])
        
    if not claimed_skills:
        st.error("Tidak ada skill teknis umum yang terdeteksi di dokumen CV.")
    else:
        results, score, verified_count = verify_skills(claimed_skills, repos, repo_contexts)
        
        # --- METRIC CARDS ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Verification Score", f"{score}%")
        col2.metric("Skill Terverifikasi", f"{verified_count} / {len(claimed_skills)}")
        col3.metric("Repo Publik Dicek", len(repos))
        col4.metric("Status Integritas", "Tinggi 🌲⭐" if score >= 60 else "Menengah 🍃🔍" if score >= 30 else "Perlu Bukti ⚠️")
        
        st.divider()
        
        # --- TABEL BUKTI KERJA ---
        st.subheader("📋 Proof-of-Work Matrix")
        st.table(results)
        
        # --- CATATAN EVALUATOR ---
        st.subheader("🦉 Catatan Evaluasi untuk Recruiter")
        if score >= 50:
            st.success(
                f"Kandidat **{github_user}** memiliki skor integritas teknis **{score}%** dengan **{verified_count} skill** "
                f"terbukti aktif melalui kode, dokumentasi, dan dependensi proyek. Portofolio sangat kredibel dan siap lanjut ke tahap interview teknis."
            )
        else:
            st.info(
                f"Kandidat **{github_user}** mencantumkan **{len(claimed_skills)} skill**, dengan **{verified_count} skill** terverifikasi publik. "
                f"Beberapa skill belum memiliki artefak publik dan disarankan untuk dikonfirmasi melalui portofolio privat."
            )
else:
    st.info("👈 Klik **Audit & Verifikasi CV** di sidebar untuk menjalankan analisis bertema hutan!")
