import os
from pngtomarkdown import ocr_to_md

def main():
    image_folder = os.path.join("data", "processed")
    output_md = os.path.join(image_folder, "HSC26-Bangla1st-Paper-parsed-random.md")
    
    
    # Get all image files
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith('.png')]
    image_files.sort()
    all_md = []
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        print(f"Processing {img_file}...")
        md_text = ocr_to_md(img_path)
        all_md.append(f"## {img_file}\n\n{md_text}\n")
    combined_md = "\n".join(all_md)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(combined_md)
    print(f"Combined markdown written to {output_md}")
    

if __name__ == "__main__":
    main() 