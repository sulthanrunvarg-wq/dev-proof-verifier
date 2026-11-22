from pypdf import PdfReader
import re

COMMON_TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Docker",
    "Kubernetes", "PyTorch", "TensorFlow", "FastAPI", "Flask", "Django",
    "Streamlit", "PostgreSQL", "MongoDB", "MySQL", "Git", "GitHub",
    "C++", "C", "Go", "Rust", "Java", "Kotlin", "AWS", "GCP", "Azure",
    "Linux", "TailwindCSS", "HTML", "CSS", "Pandas", "NumPy"
]

def extract_text_from_pdf(pdf_file) -> str:
    """Mengekstrak teks lengkap dari objek atau file path PDF."""
    reader = PdfReader(pdf_file)
    extracted_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted_text += page_text + "\n"
    return extracted_text

def extract_claimed_skills(text: str) -> list[str]:
    """Mendeteksi skill teknis yang disebutkan dalam teks CV."""
    found_skills = set()
    for skill in COMMON_TECH_SKILLS:
        # Gunakan regex word boundary agar akurat (misal: 'C' tidak salah tangkap di 'Cat')
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill)
    return sorted(list(found_skills))

if __name__ == "__main__":
    # Tes simulasi teks CV sederhana
    sample_cv = """
    Sulthan - AI & Software Developer
    Skills: Python, Streamlit, PyTorch, Git, Docker, and PostgreSQL.
    Projects: Built a Sketch-Guided Doodle-to-Art Diffusion Studio using Python and Streamlit.
    """
    skills = extract_claimed_skills(sample_cv)
    print("Daftar skill yang terdeteksi dari simulasi CV:")
    print(skills)
