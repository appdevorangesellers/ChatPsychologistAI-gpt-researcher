from backend.utils import write_to_txt_file
from typing import Dict
from slugify import slugify

async def generate_files(report: str, filename: str) -> Dict[str, str]:
    # pdf_path = await write_md_to_pdf(report, filename)
    # docx_path = await write_md_to_word(report, filename)
    print(slugify(filename))
    print("report", report)
    txt_path = await write_to_txt_file(report, slugify(filename))
    # return {"pdf": pdf_path, "docx": docx_path, "md": md_path}