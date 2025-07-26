import re
import os

# convert Bangla digits to int
def bangla_to_int(bangla_num_str):
    mapping = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    return int(bangla_num_str.translate(mapping))

bangla_digit_pattern = r'([০-৯]+)\।'


def preprocess_markdown(input_file, cleaned_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the failed <red>/<blue> tag extraction from gemini
    content = re.sub(r'</?red>', '', content)
    content = re.sub(r'</?blue>', '', content)

    # Remove specific headers
    headers_to_remove = [
        'অনলাইন ব্যাচ',
        'কল করো',
        '## HSC 26'
    ]
    #Remove redundant pattern bangla_eng_ict
    pattern_bangla_eng_ict = re.compile(r'বাংলা\W+ইংরেজি\W+আইসিটি')
    
    #Remove the page header pattern developed by gemini ## HSC26-Bangla1st-Paper_1.png  
    pattern_page_header = re.compile(r'^##\s*HSC26-Bangla1st-Paper_\d+\.png\s*$', re.MULTILINE)

    lines = content.split('\n')
    filtered_lines = []
    for line in lines:
        stripped = line.strip()

        # Skip headers
        should_remove = any(header.strip() in stripped for header in headers_to_remove)
        if pattern_bangla_eng_ict.search(stripped):
            should_remove = True
        if pattern_page_header.match(stripped):
            should_remove = True

        # Remove English page numbers like "12"
        if re.fullmatch(r'[\d০-৯]{1,3}', stripped):
            should_remove = True
        # Remove page numbers like "(12)" or "(১২)" at the start of a line
        if re.match(r'^\([\d০-৯]{1,3}\)\s*$', stripped):
            should_remove = True

        if not should_remove:
            filtered_lines.append(line)

    processed_content = '\n'.join(filtered_lines)


    with open(cleaned_file, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"Preprocessing complete!")
    print(f"Input file: {input_file}")
    print(f"Output file: {cleaned_file}")
    return processed_content


def format_inline_mcqs_with_answers(md_text, output_file):
    
    #Handle inline answer tables (| SL | Ans | format)

    # Pattern to match tables that start with | SL | Ans |
    table_pattern = r'(\|\s*SL\s*\|.*?\n(?:\|\s*---.*?\n)?(?:\|.*?\n)*)'
    table_match = re.search(table_pattern, md_text, re.MULTILINE | re.DOTALL)
    answers = {}

    if table_match:
        table_text = table_match.group(1)


        rows = [row.strip() for row in table_text.splitlines() if '|' in row][2:]  # Skip header and separator
        for row in rows:
            cols = [c.strip() for c in row.split('|') if c.strip()]
            for i in range(0, len(cols), 2):
                if i + 1 < len(cols):
                    q_str = cols[i].replace('SL', '').strip()
                    if q_str: 
                        # Finding question number (English or Bangla digits)
                        try:
                            num = int(q_str)
                        except ValueError:
                            try:
                                num = bangla_to_int(q_str)
                            except Exception:
                                continue
                        answers[num] = cols[i + 1]

        # Remove the table completely
        md_text = re.sub(table_pattern, "", md_text, count=1)

    # Add answers to individual questions
    # Only process questions if we have answers
    if answers:
        question_blocks = re.split(r'(?m)(?<=\n)' + bangla_digit_pattern, md_text)
        result = question_blocks[0]  # Text before first question
        
        processed_count = 0
        max_questions = len(answers)
        
        for i in range(1, len(question_blocks), 2):
            # Stop processing once we've handled all questions in our dictionary
            if processed_count >= max_questions:
                for j in range(i, len(question_blocks), 2):
                    if j + 1 < len(question_blocks):
                        result += f"{question_blocks[j]}।{question_blocks[j + 1]}"
                break
                
            qnum_bangla = question_blocks[i]
            content = question_blocks[i + 1] if i + 1 < len(question_blocks) else ""
            
            try:
                qnum = bangla_to_int(qnum_bangla)
                if qnum in answers:
                    answer = answers[qnum]
                    block_lines = content.strip().splitlines()
                    block_with_answer = "\n".join(block_lines) + \
                        f"\n\n**সঠিক উত্তর:** {answer}\n"
                    result += f"{qnum_bangla}।{block_with_answer}\n"
                    processed_count += 1
                else:
                    # Question not in answers, keep original
                    result += f"{qnum_bangla}।{content}"
            except Exception:
                result += f"{qnum_bangla}।{content}"
        
        final_text = result
    else:
        final_text = md_text

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_text)

    print(f"Inline MCQ formatting complete!")
    print(f"Output file: {output_file}")


def format_mcqs_with_answers(md_text, output_file):
    #handles table starting with ## উত্তরমালা

    table_pattern = r'## উত্তরমালা\s*((?:\|.*\n)+)'
    table_match = re.search(table_pattern, md_text)
    answers = {}

    if table_match:
        table_text = table_match.group(1)

        # Parse the table
        rows = [row.strip() for row in table_text.splitlines() if '|' in row][2:]
        for row in rows:
            cols = [c.strip() for c in row.split('|') if c.strip()]
            for i in range(0, len(cols), 2):
                if i + 1 < len(cols):
                    q = cols[i].replace('SL', '').strip()
                    try:
                        num = int(q)
                    except ValueError:
                        try:
                            num = bangla_to_int(q)
                        except Exception:
                            continue
                    answers[num] = cols[i + 1]

        md_text = re.sub(table_pattern,"", md_text, count=1)

    def add_answers_to_section(section_text):
        question_blocks = re.split(r'(?m)(?<=\n)' + bangla_digit_pattern, section_text)
        result = question_blocks[0]
        for i in range(1, len(question_blocks), 2):
            qnum_bangla = question_blocks[i]
            qnum = bangla_to_int(qnum_bangla)
            content = question_blocks[i + 1]
            block_lines = content.strip().splitlines()
            block_with_answer = "\n".join(block_lines) + \
                f"\n\n**সঠিক উত্তর:** {answers.get(qnum, 'উত্তর পাওয়া যায়নি')}\n"
            result += f"{qnum_bangla}।{block_with_answer}\n"
        return result
    section_pattern = r"(## (?:বহুনির্বাচনী-প্র্যাক্টিস)[\s\S]*?)(?=\n## |\Z)"

    final_text = re.sub(
        section_pattern,
        lambda m: add_answers_to_section(m.group(1)),
        md_text
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_text)

    print(f"MCQ formatting complete!")
    print(f"Output file: {output_file}")


def main():
    input_file = os.path.join("data", "processed", "HSC26-Bangla1st-Paper-parsed.md")
    cleaned_file = os.path.join("data", "processed", "HSC26-Bangla1st-Paper-parsed-cleaned.md")
    inline_mcq_file = os.path.join("data", "processed", "HSC26-Bangla1st-Paper-inline-answers.md")
    final_file = os.path.join("data", "processed", "HSC26-Bangla1st-Paper-with-answers.md")

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    cleaned_md = preprocess_markdown(input_file, cleaned_file)

    print("Processing inline MCQ tables")
    format_inline_mcqs_with_answers(cleaned_md, inline_mcq_file)
    
    with open(inline_mcq_file, 'r', encoding='utf-8') as f:
        inline_processed_md = f.read()

    print("Processing উত্তরমালা sections")
    format_mcqs_with_answers(inline_processed_md, final_file)
    print(f"Final processed file written to: {final_file}")


if __name__ == "__main__":
    main()
