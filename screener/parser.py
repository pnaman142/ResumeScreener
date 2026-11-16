"""
Resume Parser module supporting PDF, DOCX, and TXT files.
Extracts raw text and segments content into logical sections
(Skills, Experience, Education, Projects, Certifications).
"""

import io
import os
import re
from typing import Dict, Optional, Union

import pdfplumber
import pypdf
import docx


def normalize_extracted_text(text: str) -> str:
    """Normalize extracted text, clean bullet glyphs and collapse multi-space gaps."""
    if not text:
        return ""
    # Remove CID artifacts from PDF fonts (e.g., (cid:127))
    text = re.sub(r"\(cid:\d+\)", " ", text)
    # Normalize bullet characters
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u00B7\u25AA\u25CF]", " ", text)
    # Collapse consecutive horizontal spaces while keeping line breaks
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    # Remove excessive blank lines
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_text_from_pdf(source: Union[str, bytes, io.BytesIO]) -> str:
    """
    Extract text from a PDF file path or file-like binary stream.
    Tries pdfplumber first for high fidelity layout; falls back to pypdf.
    """
    text_content = []

    # Prepare stream
    stream = None
    if isinstance(source, (str, os.PathLike)):
        with open(source, "rb") as f:
            stream = io.BytesIO(f.read())
    elif isinstance(source, bytes):
        stream = io.BytesIO(source)
    else:
        stream = source

    # Try pdfplumber
    try:
        stream.seek(0)
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                # Default extract_text usually gives better continuous word spacing than layout=True
                page_text = page.extract_text()
                if not page_text:
                    page_text = page.extract_text(layout=True)
                if page_text:
                    text_content.append(page_text)
        if text_content:
            return normalize_extracted_text("\n\n".join(text_content))
    except Exception:
        pass

    # Fallback to pypdf
    try:
        stream.seek(0)
        reader = pypdf.PdfReader(stream)
        text_content = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_content.append(t)
        return normalize_extracted_text("\n\n".join(text_content))
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")


def extract_text_from_docx(source: Union[str, bytes, io.BytesIO]) -> str:
    """Extract text from a DOCX file path or binary stream."""
    stream = None
    if isinstance(source, (str, os.PathLike)):
        doc = docx.Document(source)
    elif isinstance(source, bytes):
        doc = docx.Document(io.BytesIO(source))
    else:
        source.seek(0)
        doc = docx.Document(source)

    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return normalize_extracted_text("\n".join(paragraphs))


def extract_text_from_txt(source: Union[str, bytes, io.BytesIO]) -> str:
    """Extract text from a TXT or Markdown file path or stream."""
    if isinstance(source, (str, os.PathLike)):
        with open(source, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    elif isinstance(source, bytes):
        raw = source.decode("utf-8", errors="replace")
    else:
        source.seek(0)
        data = source.read()
        raw = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)

    return normalize_extracted_text(raw)


def parse_resume(source: Union[str, bytes, io.BytesIO], filename: Optional[str] = None) -> str:
    """
    Parse a resume from a file path or file-like buffer based on extension/filename.
    """
    name = ""
    if isinstance(source, str):
        name = source.lower()
    elif filename:
        name = filename.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(source)
    elif name.endswith(".docx"):
        return extract_text_from_docx(source)
    elif name.endswith(".txt") or name.endswith(".md"):
        return extract_text_from_txt(source)
    else:
        # Default probe: try text, then pdf
        try:
            return extract_text_from_txt(source)
        except Exception:
            try:
                return extract_text_from_pdf(source)
            except Exception:
                raise ValueError(f"Unsupported resume format or corrupted file for: {filename or 'source'}")


SECTION_HEADERS = {
    "experience": [
        "work experience", "professional experience", "experience",
        "employment history", "work history", "career history", "internships"
    ],
    "education": [
        "education", "academic background", "qualifications", "academics",
        "educational background", "degrees"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "technologies",
        "expertise", "key skills", "skill set", "technical expertise",
        "tools & technologies", "proficiencies"
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "key projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses & certifications", "accreditations"
    ],
    "summary": [
        "summary", "professional summary", "about me", "profile", "objective",
        "career objective", "executive summary"
    ]
}


def segment_sections(text: str) -> Dict[str, str]:
    """
    Segment resume raw text into distinct sections based on common headings.
    Returns a dictionary of section names to text content.
    """
    sections = {k: "" for k in SECTION_HEADERS}
    sections["full_text"] = text

    lines = text.split("\n")
    current_section = "summary"
    section_buffers = {k: [] for k in SECTION_HEADERS}
    section_buffers["other"] = []

    # Build regex patterns for section headers
    header_patterns = {}
    for sec, aliases in SECTION_HEADERS.items():
        alias_regex = "|".join([re.escape(a) for a in aliases])
        pattern = re.compile(rf"^\s*(?:[\#\*\-]+\s*)?(?:{alias_regex})(?:\s*[:\-])?\s*$", re.IGNORECASE)
        header_patterns[sec] = pattern

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_sec = None
        # Check if line matches any section header
        if len(stripped) < 45:
            for sec, pattern in header_patterns.items():
                if pattern.match(stripped):
                    matched_sec = sec
                    break

        if matched_sec:
            current_section = matched_sec
        else:
            if current_section in section_buffers:
                section_buffers[current_section].append(line)
            else:
                section_buffers["other"].append(line)

    for sec in SECTION_HEADERS:
        sections[sec] = "\n".join(section_buffers[sec]).strip()

    return sections
