from pdf2image import convert_from_path

pages = convert_from_path("data/raw/HSC26-Bangla1st-Paper.pdf", dpi=300, fmt="png")
for i, p in enumerate(pages, 1):
    p.save(f"data/processed/HSC26-Bangla1st-Paper_{i:03}.png")
