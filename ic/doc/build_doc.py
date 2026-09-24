"""Dung tai lieu .docx va .pdf tu chip_pid_giai_thich.html (khong can Word/LibreOffice).

  .docx: dung truc tiep WordprocessingML (goi ZIP chua XML) tu HTML - chi ho tro dung tap the
         dang dung trong file HTML: h1, h2, p, div.note/.ok, ul/li, table, img, b, i, code, sup.
  .pdf : Microsoft Word xuat tu chinh file .docx (giong het); Word loi thi Edge in HTML (du phong).
  Khoi co class "wide" (hinh, tieu de, doan, bang) nam tren trang kho ngang.

Chay: python ic/doc/build_doc.py      (chay ic/doc/gen_figs.py + svg2png.ps1 truoc neu doi hinh)
"""
import os
import re
import struct
import subprocess
import zipfile
from html.parser import HTMLParser
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'chip_pid_giai_thich.html')
DOCX = os.path.join(HERE, 'FPOLY_UAV_chip_PID_giai_thich.docx')
PDF = os.path.join(HERE, 'FPOLY_UAV_chip_PID_giai_thich.pdf')
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

TEXT_W_DXA = 9638          # A4 21 cm - 2 x 2 cm le = 17 cm
TEXT_W_EMU = 6120000       # 17 cm


# ------------------------------------------------------------------ doc HTML ----
class Doc(HTMLParser):
    """Chuyen HTML thanh danh sach khoi: (loai, thuoc tinh, runs | bang | hinh)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.block = None
        self.table = None
        self.cell = None
        self.fmt = {'b': 0, 'i': 0, 'code': 0, 'sup': 0}
        self.skip = 0

    def _runs(self):
        return self.cell['runs'] if self.cell is not None else self.block['runs'] if self.block else None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '')
        if tag in ('head', 'style', 'title', 'script'):
            self.skip += 1
        elif tag in ('p', 'h1', 'h2', 'li', 'div'):
            kind = {'p': 'p', 'h1': 'h1', 'h2': 'h2', 'li': 'li', 'div': 'note'}[tag]
            self.block = {'kind': kind, 'cls': cls, 'runs': [],
                          'pagebreak': 'page-break-before' in a.get('style', '')}
        elif tag == 'table':
            self.table = {'rows': [], 'cls': cls, 'pagebreak': 'page-break-before' in a.get('style', '')}
        elif tag == 'tr':
            self.table['rows'].append([])
        elif tag in ('th', 'td'):
            self.cell = {'header': tag == 'th', 'runs': []}
        elif tag in ('b', 'strong'):
            self.fmt['b'] += 1
        elif tag in ('i', 'em'):
            self.fmt['i'] += 1
        elif tag in ('code', 'sup'):
            self.fmt[tag] += 1
        elif tag == 'img':
            wide = self.block is not None and 'wide' in self.block['cls']
            self.blocks.append(('img', {'src': a['src'], 'width': int(a.get('width', 600)), 'wide': wide,
                                        'cls': 'wide' if wide else '',
                                        'maxh': float(a.get('data-maxh', 15.0))}))
            self.block = None

    def handle_endtag(self, tag):
        if tag in ('head', 'style', 'title', 'script'):
            self.skip -= 1
        elif tag in ('p', 'h1', 'h2', 'li', 'div') and self.block is not None:
            runs = self.block['runs']
            if runs:
                runs[0][0] = runs[0][0].lstrip()
                runs[-1][0] = runs[-1][0].rstrip()
            if any(r[0] for r in runs):
                self.blocks.append((self.block['kind'], self.block))
            self.block = None
        elif tag in ('th', 'td'):
            self.table['rows'][-1].append(self.cell)
            self.cell = None
        elif tag == 'table':
            self.blocks.append(('table', self.table))
            self.table = None
        elif tag in ('b', 'strong'):
            self.fmt['b'] -= 1
        elif tag in ('i', 'em'):
            self.fmt['i'] -= 1
        elif tag in ('code', 'sup'):
            self.fmt[tag] -= 1

    def handle_data(self, data):
        if self.skip:
            return
        runs = self._runs()
        if runs is None:
            return
        text = re.sub(r'\s+', ' ', data)
        if not text:
            return
        runs.append([text, dict(self.fmt)])


# --------------------------------------------------------------- viet DOCX ----
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


def run_xml(text, fmt, bold=False):
    rpr = ''
    if fmt['b'] or bold:
        rpr += '<w:b/>'
    if fmt['i']:
        rpr += '<w:i/>'
    if fmt['code']:
        rpr += ('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
                '<w:shd w:val="clear" w:color="auto" w:fill="F1F3F5"/>')
    if fmt['sup']:
        rpr += '<w:vertAlign w:val="superscript"/>'
    rpr = f'<w:rPr>{rpr}</w:rPr>' if rpr else ''
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def para(style, runs, extra_ppr='', bold=False):
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/>{extra_ppr}</w:pPr>'
    return f'<w:p>{ppr}{"".join(run_xml(t, f, bold) for t, f in runs)}</w:p>'


def png_size(path):
    with open(path, 'rb') as f:
        head = f.read(24)
    return struct.unpack('>II', head[16:24])


def table_xml(tbl, total_w=TEXT_W_DXA):
    rows = tbl['rows']
    ncol = max(len(r) for r in rows)
    weight = [8] * ncol
    for j, c in enumerate(rows[0]):
        head = ''.join(t for t, _ in c['runs']).strip()
        longest = max((len(w) for w in head.split()), default=0)
        weight[j] = max(weight[j], longest + 4)
    for r in rows:
        for j, c in enumerate(r):
            n = len(''.join(t for t, _ in c['runs']))
            weight[j] = max(weight[j], min(n, 42))
    total = sum(weight)
    widths = [int(total_w * w / total) for w in weight]
    widths[-1] += total_w - sum(widths)
    border = ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="ADB5BD"/>'
                     for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
    out = [f'<w:tbl><w:tblPr><w:tblW w:w="{total_w}" w:type="dxa"/><w:tblBorders>{border}</w:tblBorders>'
           '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
           '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>',
           ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths), '</w:tblGrid>']
    for r in rows:
        header = all(c['header'] for c in r)
        trpr = '<w:trPr><w:cantSplit/>' + ('<w:tblHeader/>' if header else '') + '</w:trPr>'
        out.append(f'<w:tr>{trpr}')
        for j, c in enumerate(r):
            shd = '<w:shd w:val="clear" w:color="auto" w:fill="E7F5FF"/>' if c['header'] else ''
            runs = c['runs']
            if runs:
                runs[0][0] = runs[0][0].lstrip()
                runs[-1][0] = runs[-1][0].rstrip()
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[j]}" w:type="dxa"/>{shd}</w:tcPr>'
                       f'{para("TableText", runs, bold=c["header"])}</w:tc>')
        out.append('</w:tr>')
    out.append('</w:tbl>')
    out.append(para('Normal', [], '<w:spacing w:after="60"/>'))
    return ''.join(out)


LAND_W_EMU = 9252000        # vung hinh trang ngang rong 25,7 cm
LAND_TEXT_W_DXA = 14570     # 29,7 cm - 2 x 2 cm


def sect_xml(landscape):
    size = ('<w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>' if landscape
            else '<w:pgSz w:w="11906" w:h="16838"/>')
    return ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/>' + size +
            '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" '
            'w:gutter="0"/></w:sectPr>')


def build_docx(blocks):
    body, media, rels = [], [], []
    orient = False            # False = doc, True = ngang
    prev_wide_img = False
    section_changed = False
    style_of = {'h1': 'Heading1', 'h2': 'Heading2', 'li': 'ListBullet'}
    p_style = {'title': 'Title', 'subtitle': 'Subtitle', 'caption': 'Caption'}
    for kind, b in blocks:
        want = 'wide' in b.get('cls', '')
        section_changed = want != orient
        if section_changed:
            body.append(f'<w:p><w:pPr>{sect_xml(orient)}</w:pPr></w:p>')   # ket thuc section hien tai
            orient = want
        prev_wide_img = kind == 'img' and b.get('wide', False)
        if kind == 'img':
            src = os.path.join(HERE, b['src'])
            w_px, h_px = png_size(src)
            if b.get('wide'):
                cx = LAND_W_EMU
                cy = int(cx * h_px / w_px)
                max_h = int(b['maxh'] * 360000)
                if cy > max_h:
                    cy = max_h
                    cx = int(cy * w_px / h_px)
            else:
                cx = min(TEXT_W_EMU, b['width'] * 9525)
                cy = int(cx * h_px / w_px)
            n = len(media) + 1
            rid = f'rIdImg{n}'
            media.append((f'media/image{n}.png', src))
            rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                        f'relationships/image" Target="media/image{n}.png"/>')
            body.append(
                '<w:p><w:pPr><w:pStyle w:val="Figure"/></w:pPr><w:r><w:drawing>'
                f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
                f'<wp:docPr id="{n}" name="Hinh {n}"/><wp:cNvGraphicFramePr>'
                '<a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
                '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{n}" name="image{n}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
                f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
                '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
        elif kind == 'table':
            if b.get('pagebreak') and not section_changed:
                body.append('<w:p><w:pPr><w:spacing w:after="0"/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>')
            body.append(table_xml(b, LAND_TEXT_W_DXA if orient else TEXT_W_DXA))
        elif kind == 'note':
            body.append(para('Ok' if 'ok' in b['cls'] else 'Note', b['runs']))
        elif kind in style_of:
            extra = '<w:pageBreakBefore/>' if b['pagebreak'] and not section_changed else ''
            body.append(para(style_of[kind], b['runs'], extra))
        else:
            body.append(para(p_style.get((b['cls'].split() or [''])[0], 'Normal'), b['runs']))

    sect = sect_xml(orient)
    document = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {NS}><w:body>'
                + ''.join(body) + sect + '</w:body></w:document>')

    def pstyle(sid, name, ppr='', rpr='', based='Normal', nxt='Normal', extra=''):
        return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/>'
                f'<w:basedOn w:val="{based}"/><w:next w:val="{nxt}"/><w:qFormat/>{extra}'
                f'<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')

    note_ppr = lambda fill, bar: (f'<w:pBdr><w:left w:val="single" w:sz="24" w:space="6" w:color="{bar}"/></w:pBdr>'
                                  f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
                                  '<w:spacing w:before="120" w:after="200"/><w:ind w:left="170" w:right="113"/>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial" '
              'w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="1F2328"/><w:lang w:val="vi-VN"/>'
              '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/>'
              '</w:pPr></w:pPrDefault></w:docDefaults>'
              '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
              + pstyle('Title', 'Title', '<w:spacing w:after="80"/>', '<w:b/><w:color w:val="1864AB"/><w:sz w:val="48"/>')
              + pstyle('Subtitle', 'Subtitle', '<w:spacing w:after="60"/>', '<w:color w:val="57606A"/><w:sz w:val="24"/>')
              + pstyle('Heading1', 'heading 1', '<w:keepNext/><w:spacing w:before="360" w:after="120"/><w:outlineLvl w:val="0"/>',
                       '<w:b/><w:color w:val="1864AB"/><w:sz w:val="32"/>')
              + pstyle('Heading2', 'heading 2', '<w:keepNext/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="1"/>',
                       '<w:b/><w:sz w:val="26"/>')
              + pstyle('Caption', 'caption', '<w:jc w:val="center"/><w:spacing w:after="240"/>',
                       '<w:i/><w:color w:val="57606A"/><w:sz w:val="19"/>')
              + pstyle('Figure', 'Figure', '<w:keepNext/><w:jc w:val="center"/><w:spacing w:before="160" w:after="60"/>')
              + pstyle('Note', 'Note', note_ppr('FFF9DB', 'F08C00'))
              + pstyle('Ok', 'Ok', note_ppr('EBFBEE', '2B8A3E'))
              + pstyle('TableText', 'Table Text', '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>',
                       '<w:sz w:val="20"/>')
              + pstyle('ListBullet', 'List Bullet', '<w:numPr><w:numId w:val="1"/></w:numPr><w:spacing w:after="80"/>')
              + '</w:styles>')
    numbering = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                 '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>'
                 '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/>'
                 '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="397" w:hanging="284"/></w:pPr>'
                 '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr></w:lvl></w:abstractNum>'
                 '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>')
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
              '<w:r><w:rPr><w:color w:val="57606A"/><w:sz w:val="18"/></w:rPr><w:t xml:space="preserve">FPOLY UAV · Chip PID · trang </w:t></w:r>'
              '<w:r><w:rPr><w:color w:val="57606A"/><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
              '<w:r><w:rPr><w:color w:val="57606A"/><w:sz w:val="18"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:rPr><w:color w:val="57606A"/><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
              '<w:r><w:rPr><w:color w:val="57606A"/><w:sz w:val="18"/></w:rPr><w:t>1</w:t></w:r>'
              '<w:r><w:rPr><w:color w:val="57606A"/><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
    doc_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '<Relationship Id="rIdNum" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
                '<Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
                + ''.join(rels) + '</Relationships>')
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Default Extension="png" ContentType="image/png"/>'
                     '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                     '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                     '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
                     '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
                     '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                     '</Types>')
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                 '</Relationships>')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:title>Chip điều khiển PID cho drone — Giải thích cho nhóm</dc:title><dc:creator>FPOLY UAV</dc:creator>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">2026-09-24T00:00:00Z</dcterms:created></cp:coreProperties>')

    with zipfile.ZipFile(DOCX, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', root_rels)
        z.writestr('docProps/core.xml', core)
        z.writestr('word/document.xml', document)
        z.writestr('word/styles.xml', styles)
        z.writestr('word/numbering.xml', numbering)
        z.writestr('word/footer1.xml', footer)
        z.writestr('word/_rels/document.xml.rels', doc_rels)
        for name, src in media:
            z.write(src, 'word/' + name)
    return len(media)


WORD_PDF_PS = r"""
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false; $word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open('%s', $false, $true, $false)
    $doc.ExportAsFixedFormat('%s', 17)
    $pages = $doc.ComputeStatistics(2)
    $doc.Close($false)
    "$pages"
} finally { $word.Quit() }
"""


def build_pdf():
    """Uu tien Word (PDF giong het .docx); Word loi/treo qua 3 phut thi dung Edge in HTML."""
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command', WORD_PDF_PS % (DOCX, PDF)],
                           capture_output=True, text=True, timeout=180)
        if r.returncode == 0 and os.path.exists(PDF):
            return f'Word, {r.stdout.strip()} trang'
    except subprocess.TimeoutExpired:
        subprocess.run(['powershell', '-NoProfile', '-Command',
                        'Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force'])
    build_pdf_edge()
    return 'Edge (du phong)'


def build_pdf_edge():
    tmp = os.path.join(os.environ.get('TEMP', HERE), 'edge-pdf-profile')
    uri = 'file:///' + SRC.replace('\\', '/')
    subprocess.run([EDGE, '--headless=new', '--disable-gpu', f'--user-data-dir={tmp}', '--no-pdf-header-footer',
                    f'--print-to-pdf={PDF}', uri], check=True, capture_output=True, timeout=120)


if __name__ == '__main__':
    parser = Doc()
    with open(SRC, encoding='utf-8') as f:
        parser.feed(f.read())
    n_img = build_docx(parser.blocks)
    kinds = [k for k, _ in parser.blocks]
    print(f'docx: {len(parser.blocks)} khoi, {kinds.count("table")} bang, {n_img} hinh -> {DOCX} '
          f'({os.path.getsize(DOCX) // 1024} KB)')
    how = build_pdf()
    print(f'pdf : {PDF} ({os.path.getsize(PDF) // 1024} KB, {how})')
