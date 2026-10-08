import zipfile
import re
import os

pptx_path = r"D:\Projects\Data_Quest_3.0\DATAQUEST_3_0_PRISM_Engine.pptx"
out_path = r"D:\Projects\Data_Quest_3.0\ppt_content.md"

if not os.path.exists(pptx_path):
    print("File not found.")
else:
    try:
        with open(out_path, "w", encoding="utf-8") as out:
            with zipfile.ZipFile(pptx_path, 'r') as z:
                slide_files = [f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
                slide_files.sort(key=lambda x: int(re.search(r'slide(\d+)\.xml', x).group(1)))
                
                for i, slide_file in enumerate(slide_files, 1):
                    xml_content = z.read(slide_file).decode('utf-8')
                    texts = re.findall(r'<a:t>(.*?)</a:t>', xml_content)
                    out.write(f"### SLIDE {i}\n")
                    for t in texts:
                        if t.strip():
                            out.write(f"- {t}\n")
                    out.write("\n")
        print("Successfully extracted to ppt_content.md")
    except Exception as e:
        print(f"Error reading pptx: {e}")
