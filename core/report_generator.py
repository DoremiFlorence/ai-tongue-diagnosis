"""PDF 报告生成模块。"""

import io
import os
from datetime import datetime
from typing import Optional

from fpdf import FPDF


def get_chinese_font_path() -> Optional[str]:
    """获取系统中文字体路径。"""
    font_paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None


def safe_text_for_pdf(text: str, use_chinese_font: bool) -> str:
    """处理文本以确保 PDF 兼容性。"""
    if use_chinese_font:
        return text
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_diagnosis_report(
    initial_analysis: str,
    final_diagnosis: str,
    conversation_summary: Optional[str] = None,
) -> bytes:
    """生成诊断报告 PDF。

    Args:
        initial_analysis: 初始舌诊分析
        final_diagnosis: 最终诊断结果
        conversation_summary: 问诊摘要

    Returns:
        PDF 文件字节
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    chinese_font_path = get_chinese_font_path()
    use_chinese = False

    if chinese_font_path:
        try:
            pdf.add_font("Chinese", "", chinese_font_path, uni=True)
            use_chinese = True
            font_name = "Chinese"
        except Exception:
            font_name = "Helvetica"
    else:
        font_name = "Helvetica"

    if use_chinese:
        pdf.set_font(font_name, size=18)
        pdf.cell(0, 15, "中医舌诊诊断报告", ln=True, align="C")
    else:
        pdf.set_font(font_name, "B", 18)
        pdf.cell(0, 15, "TCM Tongue Diagnosis Report", ln=True, align="C")

    pdf.set_font(font_name, size=10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(8)

    def write_section(title: str, content: str):
        """写入一个章节。"""
        if use_chinese:
            pdf.set_font(font_name, size=14)
        else:
            pdf.set_font(font_name, "B", 14)
        pdf.cell(0, 10, safe_text_for_pdf(title, use_chinese), ln=True)

        if use_chinese:
            pdf.set_font(font_name, size=11)
        else:
            pdf.set_font(font_name, size=11)

        for line in content.split("\n"):
            line = line.strip()
            if line:
                safe_line = safe_text_for_pdf(line, use_chinese)
                if len(safe_line) > 80:
                    words = safe_line.split()
                    if len(words) > 1:
                        pdf.multi_cell(0, 6, safe_line)
                    else:
                        for i in range(0, len(safe_line), 70):
                            pdf.cell(0, 6, safe_line[i:i+70], ln=True)
                else:
                    pdf.multi_cell(0, 6, safe_line)
        pdf.ln(4)

    write_section("1. Tongue Analysis / 舌象分析" if use_chinese else "1. Tongue Analysis",
                  initial_analysis)

    if conversation_summary:
        write_section("2. Consultation / 问诊记录" if use_chinese else "2. Consultation Summary",
                      conversation_summary)

    write_section("3. Diagnosis & Recommendations / 诊断与建议" if use_chinese else "3. Diagnosis & Recommendations",
                  final_diagnosis)

    pdf.ln(10)
    pdf.set_font(font_name, size=9)
    disclaimer = ("Disclaimer: This report is for reference only and does not constitute medical advice. "
                  "Please consult a qualified healthcare professional for proper diagnosis and treatment.")
    pdf.multi_cell(0, 5, disclaimer)

    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue()
