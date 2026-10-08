#!/usr/bin/env python3
"""Generate Word from canonical Markdown. Requires python-docx only.
Run from repository root: python3 tools/build_word.py /absolute/output.docx
Supports this project's headings, paragraphs, lists, tables, links, and fences.
Code fences remain monospaced and shaded; no server commands are executed.
"""
from pathlib import Path
import re, sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/self-hosted-netbird-travel-vpn.md'

def inline(p,text):
    pattern=r'(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))'
    for part in re.split(pattern,text):
        if not part: continue
        if part.startswith('`'):
            r=p.add_run(part[1:-1]);r.font.name='DejaVu Sans Mono';r.font.size=Pt(9.5)
            r._element.get_or_add_rPr().append(OxmlElement('w:noProof'))
        elif part.startswith('**'):
            p.add_run(part[2:-2]).bold=True
        elif part.startswith('['):
            m=re.match(r'\[([^\]]+)\]\(([^)]+)\)',part)
            label,url=m.groups()
            if url.startswith('http'):
                rel=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
                h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rel)
                r=OxmlElement('w:r');rp=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'245A81');rp.append(color);r.append(rp)
                t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)
            else: p.add_run(label)
        else: p.add_run(part)

def shade(p,color='F1F3F5'):
    el=OxmlElement('w:shd');el.set(qn('w:fill'),color);p._p.get_or_add_pPr().append(el)

def table(doc,lines):
    rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    rows=[r for r in rows if not all(re.fullmatch(r'[: -]+',x) for x in r)]
    t=doc.add_table(rows=1,cols=len(rows[0]));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths=[2.0,4.8] if len(rows[0])==2 else [1.15,0.8,4.85]
    for c,w in zip(t.columns,widths):c.width=Inches(w)
    for n,row in enumerate(rows):
        cells=t.rows[0].cells if n==0 else t.add_row().cells
        for i,(cell,value) in enumerate(zip(cells,row)):
            cell.width=Inches(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=cell._tc.get_or_add_tcPr()
            borders=OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
            tcpr.append(borders)
            margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'90');e.set(qn('w:type'),'dxa');margins.append(e)
            tcpr.append(margins)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E5E9ED' if n==0 else 'F7F8FA' if n%2==0 else 'FFFFFF');tcpr.append(sh)
            p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3)
            inline(p,value)
            for r in p.runs:r.font.size=Pt(9.5);r.bold=n==0 or r.bold
        trpr=t.rows[n]._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        if n==0:
            rep=OxmlElement('w:tblHeader');trpr.append(rep)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)

def build(output):
    doc=Document();sec=doc.sections[0]
    # Remove template title rules and theme font overrides.
    for style in doc.styles:
        for border in style.element.xpath('.//w:pBdr'):border.getparent().remove(border)

    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Inches(.65);sec.left_margin=sec.right_margin=Inches(.85)
    normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(10.5)
    normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.08
    for name,size in [('Title',24),('Heading 1',16),('Heading 2',12)]:
        s=doc.styles[name];s.font.name='Calibri';s.font.size=Pt(size);s.font.color.rgb=RGBColor(0,0,0)
        s.paragraph_format.keep_with_next=True
        s.paragraph_format.space_before=Pt(13 if name!='Title' else 0);s.paragraph_format.space_after=Pt(7)
    code=doc.styles.add_style('Code Block',WD_STYLE_TYPE.PARAGRAPH)
    code.font.name='DejaVu Sans Mono';code.font.size=Pt(8.5)
    code.paragraph_format.line_spacing=1.05;code.paragraph_format.space_before=Pt(5);code.paragraph_format.space_after=Pt(8)
    code.paragraph_format.left_indent=Inches(.10);code.paragraph_format.right_indent=Inches(.10)
    code.paragraph_format.keep_together=True;code.paragraph_format.widow_control=False
    footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=footer.add_run('NetBird travel VPN  |  ');r.font.size=Pt(8)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    doc.core_properties.title='Self Hosted NetBird Travel VPN Walkthrough'
    doc.core_properties.author='';doc.core_properties.last_modified_by='';doc.core_properties.comments=''
    lines=SOURCE.read_text().splitlines();i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
            p=doc.add_paragraph(style='Code Block');r=p.add_run('\n'.join(block));r.font.name='DejaVu Sans Mono';r.font.size=Pt(8.5);p.paragraph_format.keep_together=len(block)<=18;shade(p);i+=1;continue
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].startswith('|'):block.append(lines[i]);i+=1
            table(doc,block);continue
        if line.startswith('!['):
            p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(ROOT/'assets/architecture/architecture.png'),width=Inches(6.65))
            # Native alt text for accessibility.
            drawing=p._p.xpath('.//wp:docPr')[0];drawing.set('descr','Remote peers connect to the host control plane and encrypted routing peer. Routing peer forwards to home LAN or home ISP. Cloudflare maintains DNS.')
            i+=1;continue
        if line.startswith('# '):p=doc.add_paragraph(line[2:],style='Title');i+=1;continue
        if line.startswith('## '):p=doc.add_paragraph(line[3:],style='Heading 1');i+=1;continue
        if line.startswith('### '):p=doc.add_paragraph(line[4:],style='Heading 2');i+=1;continue
        if line.startswith('- '):p=doc.add_paragraph(style='List Bullet');inline(p,line[2:]);i+=1;continue
        if re.match(r'^\d+\. ',line):
            p=doc.add_paragraph();inline(p,line);i+=1;continue
        block=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|```|\||!\[|- |\d+\. )',lines[i]):block.append(lines[i]);i+=1
        p=doc.add_paragraph();inline(p,' '.join(block))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);doc.save(output)
    print(output)

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: build_word.py /path/output.docx')
    build(sys.argv[1])
