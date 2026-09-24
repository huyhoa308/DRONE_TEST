"""Sinh cac hinh SVG cho tai lieu giai thich chip PID (ic/doc/figs/).

Chay: python ic/doc/gen_figs.py
"""
import os
from xml.sax.saxutils import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, 'figs')
TEXT, MUTED = '#1f2328', '#57606a'
FONT = 'Segoe UI, Arial, Helvetica, sans-serif'


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.o = w, h, []

    def text(self, x, y, s, size=14, anchor='start', weight=400, fill=TEXT, italic=False):
        st = ' font-style="italic"' if italic else ''
        self.o.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
                      f'fill="{fill}"{st}>{esc(s)}</text>')

    def box(self, x, y, w, h, fill='#f6f8fa', stroke='#57606a', sw=2, rx=8, dash=False):
        d = ' stroke-dasharray="7 5"' if dash else ''
        self.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                      f'stroke-width="{sw}"{d}/>')

    def lines(self, x, y, rows, size=13, anchor='start', gap=18, fill=TEXT, weight=400):
        for i, r in enumerate(rows):
            self.text(x, y + i * gap, r, size, anchor, weight, fill)

    def arrow(self, pts, color='#1f2328', sw=2, dash=False, head=True):
        d = ' '.join(f'{x},{y}' for x, y in pts)
        da = ' stroke-dasharray="6 5"' if dash else ''
        mk = f' marker-end="url(#ah{color[1:]})"' if head else ''
        self.o.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{mk}/>')
        self._markers.add(color)

    _markers = set()

    def trapezoid(self, x, y, w, h, label, fill='#fff4e6', stroke='#e67700'):
        k = 12
        self.o.append(f'<polygon points="{x},{y} {x + w},{y + k} {x + w},{y + h - k} {x},{y + h}" fill="{fill}" '
                      f'stroke="{stroke}" stroke-width="2"/>')
        self.o.append(f'<text x="{x + w / 2}" y="{y + h / 2}" font-size="12" font-weight="700" fill="{TEXT}" '
                      f'text-anchor="middle" transform="rotate(-90 {x + w / 2} {y + h / 2})">{esc(label)}</text>')

    def save(self, name):
        defs = ''.join(f'<marker id="ah{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                       f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
                       for c in sorted(self._markers))
        body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" font-family="{FONT}">', f'<defs>{defs}</defs>',
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>', *self.o, '</svg>']
        os.makedirs(FIGS, exist_ok=True)
        with open(os.path.join(FIGS, name), 'w', encoding='utf-8') as f:
            f.write('\n'.join(body))
        Svg._markers = set()


# ------------------------------------------------------------- so do khoi ----
def block_diagram():
    s = Svg(1480, 880)
    s.text(740, 30, 'Sơ đồ khối mạch pid_ctrl — PID 3 trục dùng chung một bộ nhân', 20, 'middle', 700)

    # FSM
    s.box(540, 48, 500, 64, '#e7f5ff', '#1c7ed6')
    s.text(790, 72, 'Bộ điều khiển FSM (máy trạng thái)', 15, 'middle', 700, '#1864ab')
    s.text(790, 96, 'IDLE → LOAD → FILT → P → I → D → SAT  (lặp 3 trục)  → MIX', 13, 'middle')
    s.arrow([(600, 112), (600, 124), (418, 124), (418, 226)], '#1c7ed6', 1.5, True)
    s.text(430, 140, 'chọn trục', 11, fill='#1864ab')
    s.arrow([(780, 112), (780, 440), (818, 440), (818, 466)], '#1c7ed6', 1.5, True)
    s.text(786, 430, 'chọn toán hạng', 11, fill='#1864ab')

    # dau vao
    ins = [('sample_valid', 200), ('armed', 232), ('throttle [10:0]', 264), ('sp_roll / sp_pitch / sp_yaw', 318),
           ('roll / pitch / gz', 372)]
    for label, y in ins:
        s.text(214, y + 5, label, 13, 'end')
        s.arrow([(218, y), (230, y)], '#1f2328', 1.5)
    s.text(120, 160, 'Đầu vào', 15, 'middle', 700)
    s.text(120, 410, '(Q.FE, số nguyên có dấu)', 11, 'middle', fill=MUTED)
    s.box(232, 170, 140, 250, '#f6f8fa', '#495057')
    s.lines(302, 270, ['Thanh ghi', 'đầu vào', '(chốt khi', 'sample_valid)'], 13, 'middle', 18, weight=600)

    # mux truc + tru
    s.arrow([(372, 318), (400, 318)], '#1f2328', 1.5)
    s.arrow([(372, 372), (400, 372)], '#1f2328', 1.5)
    s.trapezoid(400, 230, 36, 170, 'MUX trục')
    s.o.append('<circle cx="486" cy="315" r="18" fill="#ffffff" stroke="#1f2328" stroke-width="2"/>')
    s.text(486, 322, '−', 22, 'middle', 700)
    s.arrow([(436, 300), (468, 308)], '#1f2328', 1.5)
    s.arrow([(436, 340), (468, 324)], '#1f2328', 1.5)
    s.text(452, 294, 'sp', 11, 'middle', fill=MUTED)
    s.text(452, 356, 'đo', 11, 'middle', fill=MUTED)
    s.arrow([(504, 315), (540, 315)], '#1f2328', 2)
    s.text(520, 306, 'e', 14, 'middle', 700)

    # tien xu ly
    s.box(540, 190, 220, 170, '#fff9db', '#f08c00')
    s.text(650, 214, 'Tiền xử lý (bước LOAD)', 14, 'middle', 700, '#e67700')
    s.lines(556, 244, ['A_raw = A + e', 'ΔE = (e − e_prev) · 2^FD', 'diff = ΔE − Df'], 13, gap=26)
    s.text(650, 344, '3 bộ cộng/trừ, không nhân', 11, 'middle', fill=MUTED, italic=True)

    # trang thai 3 truc
    s.box(232, 470, 250, 150, '#f3f0ff', '#7048e8')
    s.text(357, 494, 'Trạng thái 3 trục (thanh ghi)', 14, 'middle', 700, '#5f3dc4')
    s.lines(248, 524, ['A[roll, pitch, yaw]   tích phân', 'e_prev[3]   sai số lần trước', 'Df[3]   đạo hàm đã lọc',
                       'mix[3]   đầu ra PID'], 13, gap=22)
    s.arrow([(482, 520), (512, 520), (512, 345), (540, 345)], '#7048e8', 2)
    s.text(518, 440, 'A, e_prev, Df', 11, fill='#5f3dc4')

    # ROM he so
    s.box(540, 470, 220, 150, '#ebfbee', '#2b8a3e')
    s.text(650, 494, 'Hằng số (nối cứng)', 14, 'middle', 700, '#2b8a3e')
    s.lines(556, 524, ["KP', KI', KD' mỗi trục", 'ALPHA bộ lọc D', 'số bit dịch mỗi hệ số', 'giới hạn ±250, ±80'],
            13, gap=22)

    # mux du lieu / he so
    s.arrow([(760, 250), (800, 250)], '#f08c00', 2)
    s.trapezoid(800, 200, 36, 140, 'MUX dữ liệu')
    s.arrow([(760, 545), (800, 545)], '#2b8a3e', 2)
    s.trapezoid(800, 470, 36, 150, 'MUX hệ số')

    # bo nhan
    s.o.append('<circle cx="905" cy="405" r="32" fill="#fff0f6" stroke="#c2255c" stroke-width="3"/>')
    s.text(905, 416, '×', 32, 'middle', 700, '#c2255c')
    s.arrow([(836, 270), (880, 270), (880, 382)], '#1f2328', 2)
    s.arrow([(836, 545), (880, 545), (880, 428)], '#1f2328', 2)
    s.lines(945, 462, ['Bộ nhân dùng chung', '14 × 29 bit'], 13, 'start', 17, '#a61e4d', 700)

    # dich + lam tron
    s.box(950, 380, 104, 50, '#fff0f6', '#c2255c')
    s.lines(1002, 400, ['Dịch phải', '+ làm tròn'], 12, 'middle', 16, weight=600)
    s.arrow([(937, 405), (950, 405)], '#1f2328', 2)

    # cot phai
    col = [('Thanh ghi Df\', P, I', 150, 70, '#fff0f6', '#c2255c'),
           ("Σ   u' = P + I + D", 258, 50, '#fff0f6', '#c2255c'),
           ("Bão hoà |u'| ≤ 250", 348, 70, '#fff5f5', '#c92a2a'),
           ('Cắt về 0, giới hạn ±250 / ±80', 458, 50, '#fff5f5', '#c92a2a'),
           ('Thanh ghi mix × 3 trục', 548, 50, '#f3f0ff', '#7048e8'),
           ('Mixer X-frame', 638, 70, '#e6fcf5', '#0c8599')]
    for label, y, h, f, st in col:
        s.box(1100, y, 200, h, f, st)
        s.text(1200, y + h / 2 + 5, label, 13, 'middle', 700)
    s.text(1200, 406, '+ chống tràn tích phân', 12, 'middle', fill='#c92a2a')
    s.text(1200, 700, 'kẹp 1000–2000 µs', 12, 'middle', fill='#0c8599')
    for (_, y, h, *_), (_, y2, *_2) in zip(col, col[1:]):
        s.arrow([(1200, y + h), (1200, y2)], '#1f2328', 2)
    s.arrow([(1054, 405), (1076, 405), (1076, 185), (1100, 185)], '#1f2328', 2)
    s.arrow([(1076, 283), (1100, 283)], '#1f2328', 2)
    s.text(1080, 250, 'D', 12, 'start', 700, '#a61e4d')
    # Df' quay lai MUX du lieu
    s.arrow([(1200, 150), (1200, 136), (818, 136), (818, 206)], '#c2255c', 1.8)
    s.text(1010, 130, "Df' quay lại bộ nhân để tính D", 11, 'middle', fill='#a61e4d')
    # ghi lai trang thai
    s.arrow([(1100, 400), (1088, 400), (1088, 790), (357, 790), (357, 620)], '#c92a2a', 2, True)
    s.text(720, 782, 'ghi lại A (khi không bão hoà), e_prev, Df  —  bước SAT', 12, 'middle', 600, '#c92a2a')

    # dau ra
    for label, y in (('mix_roll / pitch / yaw', 573), ('m1 m2 m3 m4 [10:0]', 663), ('out_valid, busy', 690)):
        s.arrow([(1300, y), (1318, y)], '#1f2328', 1.5)
        s.text(1322, y + 4, label, 12)
    s.text(1350, 540, 'Đầu ra', 15, 'middle', 700)

    # chu thich
    s.arrow([(40, 840), (80, 840)], '#1f2328', 2, head=False)
    s.text(88, 845, 'dữ liệu', 12)
    s.arrow([(170, 840), (210, 840)], '#1c7ed6', 1.5, True, head=False)
    s.text(218, 845, 'điều khiển từ FSM', 12)
    s.arrow([(360, 840), (400, 840)], '#c92a2a', 2, True, head=False)
    s.text(408, 845, 'ghi lại trạng thái', 12)
    s.text(1440, 845, 'Mỗi mẫu IMU: 20 chu kỳ clock (2 µs @ 10 MHz) trong 2500 µs', 12, 'end', fill=MUTED)
    s.save('block_diagram.svg')


# ------------------------------------------------------------- lich FSM ----
def fsm_timeline():
    cw, x0 = 58, 70
    s = Svg(x0 + 20 * cw + 40, 320)
    s.text(s.w / 2, 30, 'Lịch 20 chu kỳ clock cho một mẫu IMU (bộ nhân dùng chung)', 18, 'middle', 700)
    cells = [('IDLE', 'chốt đầu vào', '#e9ecef')]
    colors = {'roll': '#fff4e6', 'pitch': '#e7f5ff', 'yaw': '#ebfbee'}
    work = [('LOAD', 'nạp α·diff'), ('FILT', "Df', nạp KP·e"), ('P', 'P, nạp KI·A'), ('I', "I, nạp KD·Df'"),
            ('D', "u'=P+I+D"), ('SAT', 'bão hoà, ghi')]
    for ax in ('roll', 'pitch', 'yaw'):
        for st, what in work:
            cells.append((st, what, colors[ax]))
    cells.append(('MIX', '4 motor', '#e6fcf5'))
    y = 100
    s.text(x0 - 8, 90, 'chu kỳ', 12, 'end', fill=MUTED)
    for i, (st, what, fill) in enumerate(cells):
        x = x0 + i * cw
        s.text(x + cw / 2, 90, str(i), 12, 'middle', fill=MUTED)
        s.box(x, y, cw - 4, 56, fill, '#868e96', 1.5, 6)
        s.text(x + cw / 2 - 2, y + 24, st, 13, 'middle', 700)
        s.o.append(f'<text x="{x + cw / 2 - 2}" y="{y + 72}" font-size="10.5" text-anchor="end" fill="{TEXT}" '
                   f'transform="rotate(-40 {x + cw / 2 - 2} {y + 72})">{esc(what)}</text>')
        busy = st in ('FILT', 'P', 'I', 'D')
        s.box(x + 6, y + 36, cw - 16, 12, '#c2255c' if busy else '#dee2e6', 'none', 0, 3)
    for ax, i0 in (('trục roll', 1), ('trục pitch', 7), ('trục yaw', 13)):
        xa, xb = x0 + i0 * cw, x0 + (i0 + 6) * cw - 4
        s.o.append(f'<path d="M{xa},{y - 28} L{xa},{y - 34} L{xb},{y - 34} L{xb},{y - 28}" fill="none" stroke="{MUTED}"/>')
        s.text((xa + xb) / 2, y - 40, ax, 13, 'middle', 700, MUTED)
    s.box(x0, 272, 14, 12, '#c2255c', 'none', 0, 3)
    s.text(x0 + 20, 283, 'bộ nhân đang cho kết quả dùng được (4 phép nhân mỗi trục: α·diff, KP·e, KI·A, KD·Df\')', 12)
    s.text(x0, 306, 'Kết quả của phép nhân nạp ở chu kỳ n được dùng ở chu kỳ n+1, nên một bộ nhân phục vụ đủ cả 12 phép '
           'nhân của 3 trục.', 12, fill=MUTED)
    s.save('fsm_timeline.svg')


# -------------------------------------------------------- quy trinh thiet ke ----
def design_flow():
    steps = [('1. Thuật toán', 'STM32 · Flight.cpp', 'Xong', '#2b8a3e'),
             ('2. Fixed-point', 'Python', 'Xong', '#2b8a3e'),
             ('3. RTL Verilog', 'pid_ctrl.v', 'Xong', '#2b8a3e'),
             ('4. Mô phỏng', 'Icarus Verilog', 'PASS', '#2b8a3e'),
             ('5. Tổng hợp', 'Cadence Genus', 'Chưa làm', '#868e96'),
             ('6. Layout', 'Cadence Innovus', 'Chưa làm', '#868e96'),
             ('7. Kiểm tra cuối', 'Tempus · Pegasus', 'Chưa làm', '#868e96')]
    bw, gap, x0 = 160, 26, 30
    s = Svg(x0 * 2 + len(steps) * bw + (len(steps) - 1) * gap, 250)
    s.text(s.w / 2, 32, 'Quy trình thiết kế chip và tiến độ của nhóm', 19, 'middle', 700)
    for i, (name, tool, status, color) in enumerate(steps):
        x = x0 + i * (bw + gap)
        s.box(x, 60, bw, 120, '#ffffff', color, 3, 12)
        s.text(x + bw / 2, 96, name, 15, 'middle', 700)
        s.text(x + bw / 2, 124, tool, 12, 'middle', fill=MUTED)
        s.box(x + 30, 140, bw - 60, 26, color, 'none', 0, 13)
        s.text(x + bw / 2, 158, status, 12, 'middle', 700, '#ffffff')
        if i:
            s.arrow([(x - gap + 2, 120), (x - 3, 120)], '#495057', 2.5)
    s.box(x0, 196, 4 * bw + 3 * gap, 34, '#ebfbee', '#2b8a3e', 1.5, 8)
    s.text(x0 + (4 * bw + 3 * gap) / 2, 218, 'Làm trên máy của nhóm (miễn phí)', 13, 'middle', 700, '#2b8a3e')
    xb = x0 + 4 * (bw + gap)
    s.box(xb, 196, 3 * bw + 2 * gap, 34, '#e7f5ff', '#1c7ed6', 1.5, 8)
    s.text(xb + (3 * bw + 2 * gap) / 2, 218, 'Cần license Cadence — buổi đào tạo', 13, 'middle', 700, '#1864ab')
    s.save('design_flow.svg')


if __name__ == '__main__':
    block_diagram()
    fsm_timeline()
    design_flow()
    print('ok ->', FIGS)
