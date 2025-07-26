import os
import base64
import google.generativeai as genai


def ocr_to_md(img_path):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Google API key not found. Set GOOGLE_API_KEY env variable or provide google_api_key.txt.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    prompt = """
    Extract ALL text from this page.
    • Use Markdown.
    • Headings -> ## .
    • Preserve tables with Markdown table syntax.
    • If sentences are highlighted in blue and red both in main part not headings, give them a special markdown tag.
    """
    resp = model.generate_content([prompt, {"mime_type": "image/png", "data": b64}])
    return resp.text

