"""Chon do rong bit cho PID fixed-point bang cach so voi ban float tren cac kich ban bay.

Chay:  python ic/model/analyze.py
Xuat ra ic/model/out/:
  report.md          bang quet do rong bit, cau hinh chon, do rong datapath, he so luong tu hoa
  golden_vectors.csv dau vao Q + dau ra mong doi tung chu ky -> testbench RTL so sanh bit-exact
  coeffs.txt         mantissa/shift cua he so, alpha, gioi han -> tham so cho RTL
  step_roll.svg      dap ung buoc roll vong kin: float vs fixed
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pid_model
from pid_model import (AXES, DT, GAINS, INTEGRAL_LIMIT, DERIV_ALPHA, MIX_LIMITS, OUTPUT_SCALE,
                       FloatController, FixedController, FxConfig, quant_coeff, worst_case_widths,
                       clamp, signed_bits)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

# Tieu chi chap nhan: sai lech lenh motor so voi float
MAX_MOTOR_ERR_US = 1        # toi da 1 us (1 LSB lenh motor; lech 1 la do cat ve 0 o ranh gioi)
MAX_MISMATCH_PCT = 1.0      # toi da 1% so chu ky co bat ky motor nao lech


# ------------------------------------------------------------------ mo hinh drone don gian ----
class Plant:
    """Moi truc la vat quay: goc'' = B*lenh - C*goc'. Chi can du thuc te de tao tin hieu giong bay that."""
    B = {'roll': 20.0, 'pitch': 20.0, 'yaw': 10.0}   # (do/s^2) tren 1 us chenh lech motor
    C = {'roll': 2.0, 'pitch': 2.0, 'yaw': 3.0}

    def __init__(self):
        self.ang = {a: 0.0 for a in AXES}
        self.rate = {a: 0.0 for a in AXES}

    def step(self, motors, dist, dt=DT):
        m1, m2, m3, m4 = motors
        torque = {'roll': (m1 - m2 - m3 + m4) / 4, 'pitch': (m1 + m2 - m3 - m4) / 4,
                  'yaw': (-m1 + m2 - m3 + m4) / 4}
        for a in AXES:
            acc = self.B[a] * torque[a] - self.C[a] * self.rate[a] + dist.get(a, 0.0)
            self.rate[a] += acc * dt
            self.ang[a] += self.rate[a] * dt


def run_closed_loop(ctrl, setpoint_fn, seconds, seed, noise=(0.3, 3.0), dist_fn=None, throttle=1500):
    """Chay vong kin, tra ve danh sach dau vao chip tung chu ky va quy dao."""
    rng = random.Random(seed)
    plant = Plant()
    inputs, traj = [], []
    for k in range(int(seconds / DT)):
        t = k * DT
        sp = setpoint_fn(t)
        inp = {'armed': 1, 'throttle': sp.get('throttle', throttle),
               'sp_roll': sp.get('roll', 0.0), 'sp_pitch': sp.get('pitch', 0.0), 'sp_yaw': sp.get('yaw', 0.0),
               'roll': plant.ang['roll'] + rng.gauss(0, noise[0]),
               'pitch': plant.ang['pitch'] + rng.gauss(0, noise[0]),
               'gz': plant.rate['yaw'] + rng.gauss(0, noise[1])}
        inputs.append(inp)
        motors, _ = ctrl.step(inp)
        plant.step(motors, dist_fn(t, rng) if dist_fn else {})
        traj.append((t, inp['sp_roll'], plant.ang['roll'], motors[0]))
    return inputs, traj


def square(t, period, amp):
    return amp if (t % period) < period / 2 else -amp


def build_scenarios():
    """Dau vao ghi lai (open-loop) de float va fixed nhan CUNG mot chuoi dau vao."""
    sc = {}

    def dist_gusts(t, rng):
        return {'roll': 300.0 * math.sin(2 * math.pi * 0.7 * t), 'pitch': 250.0 * math.sin(2 * math.pi * 0.45 * t)}

    sc['hover_gio_nhieu'] = run_closed_loop(FloatController(), lambda t: {}, 6, 1, dist_fn=dist_gusts)[0]
    sc['buoc_roll_pitch'] = run_closed_loop(
        FloatController(), lambda t: {'roll': square(t, 2.0, 20.0), 'pitch': square(t + 0.5, 1.6, 35.0)}, 6, 2)[0]
    sc['yaw_quay'] = run_closed_loop(
        FloatController(), lambda t: {'yaw': 350.0 * math.sin(2 * math.pi * 0.5 * t) if t < 3 else square(t, 1.0, 350.0)},
        6, 3)[0]

    def sticks(t):
        return {'roll': 35 * math.sin(1.3 * t) * math.cos(0.37 * t), 'pitch': 35 * math.sin(0.9 * t + 1),
                'yaw': 350 * math.sin(0.6 * t), 'throttle': int(1500 + 450 * math.sin(0.8 * t))}
    sc['can_gat_ngau_nhien'] = run_closed_loop(FloatController(), sticks, 8, 4)[0]

    # Bao hoa + chong tran tich phan: drone bi ket (goc do khong doi) roi duoc tha ra
    stuck = []
    for k in range(int(4 / DT)):
        t = k * DT
        stuck.append({'armed': 1, 'throttle': 1400, 'sp_roll': 35.0, 'sp_pitch': -35.0, 'sp_yaw': 0.0,
                      'roll': 0.0 if t < 2.5 else 34.0, 'pitch': 120.0 if t < 2.5 else -30.0, 'gz': 0.0})
    sc['ket_bao_hoa'] = stuck

    # Dau vao ngau nhien toan dai (goc +/-180, gyro +/-2000): kiem tra goc cuc, bao hoa, kep motor
    rng = random.Random(7)
    sc['ngau_nhien_toan_dai'] = [{'armed': 1, 'throttle': rng.randint(1001, 2000),
                                  'sp_roll': rng.uniform(-35, 35), 'sp_pitch': rng.uniform(-35, 35),
                                  'sp_yaw': rng.uniform(-350, 350), 'roll': rng.uniform(-180, 180),
                                  'pitch': rng.uniform(-180, 180), 'gz': rng.uniform(-2000, 2000)}
                                 for _ in range(2000)]

    # Arm/disarm lien tuc va ga <= 1000: PID phai dung yen, motor ve 1000
    rng = random.Random(9)
    arm = []
    for k in range(2000):
        armed = (k // 150) % 2 == 0
        arm.append({'armed': int(armed), 'throttle': 1000 if k % 400 < 40 else 1300,
                    'sp_roll': 10.0, 'sp_pitch': -5.0, 'sp_yaw': 50.0,
                    'roll': rng.gauss(0, 2), 'pitch': rng.gauss(0, 2), 'gz': rng.gauss(0, 20)})
    sc['arm_disarm'] = arm
    return sc


def float_outputs(inputs):
    ctrl = FloatController()
    return [ctrl.step(i)[0] for i in inputs]


def compare(cfg, scenarios, ref, stats=None, rms=None):
    """Tra ve (sai lech motor lon nhat us, % chu ky lech, chi tiet tung kich ban).

    Neu truyen list `rms`, them vao do sai lech RMS (us) cua lenh motor tren toan bo chu ky.
    """
    worst, bad, total, per, sq = 0, 0, 0, {}, 0
    for name, inputs in scenarios.items():
        ctrl = FixedController(cfg, stats)
        s_worst = s_bad = 0
        for inp, r in zip(inputs, ref[name]):
            m, _ = ctrl.step(inp)
            diffs = [a - b for a, b in zip(m, r)]
            d = max(abs(x) for x in diffs)
            sq += sum(x * x for x in diffs) / 4
            s_worst = max(s_worst, d)
            s_bad += d > 0
        per[name] = (s_worst, 100.0 * s_bad / len(inputs))
        worst = max(worst, s_worst)
        bad += s_bad
        total += len(inputs)
    if rms is not None:
        rms.append(math.sqrt(sq / total))
    return worst, 100.0 * bad / total, per


def step_setpoint(t):
    return {'roll': 0.0 if t < 0.2 else 20.0 if t < 1.6 else -10.0}


def hover_gusts(t, rng):
    return {'roll': 300.0 * math.sin(2 * math.pi * 0.7 * t), 'pitch': 250.0 * math.sin(2 * math.pi * 0.45 * t)}


def closed_loop_dev(cfg):
    """Sai lech goc roll vong kin fixed vs float: (buoc khong nhieu: max, hover co nhieu + gio: RMS)."""
    _, tf = run_closed_loop(FloatController(), step_setpoint, 2.5, 11, noise=(0.0, 0.0))
    _, tx = run_closed_loop(FixedController(cfg), step_setpoint, 2.5, 11, noise=(0.0, 0.0))
    step_max = max(abs(a[2] - b[2]) for a, b in zip(tf, tx))
    _, hf = run_closed_loop(FloatController(), lambda t: {}, 6, 12, dist_fn=hover_gusts)
    _, hx = run_closed_loop(FixedController(cfg), lambda t: {}, 6, 12, dist_fn=hover_gusts)
    hover_rms = math.sqrt(sum((a[2] - b[2]) ** 2 for a, b in zip(hf, hx)) / len(hf))
    return step_max, hover_rms, (tf, tx)


def passes(worst, pct):
    return worst <= MAX_MOTOR_ERR_US and pct <= MAX_MISMATCH_PCT


# ------------------------------------------------------------------------------ SVG plot ----
def svg_plot(path, title, series, ylabel, width=900, height=380):
    """series: [(nhan, mau, [(x, y), ...], net_dut)]"""
    pad_l, pad_r, pad_t, pad_b = 60, 20, 40, 45
    xs = [p[0] for s in series for p in s[2]]
    ys = [p[1] for s in series for p in s[2]]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    span = (y1 - y0) or 1.0
    y0, y1 = y0 - 0.08 * span, y1 + 0.08 * span
    W, H = width - pad_l - pad_r, height - pad_t - pad_b

    def X(x):
        return pad_l + (x - x0) / (x1 - x0) * W

    def Y(y):
        return pad_t + (1 - (y - y0) / (y1 - y0)) * H

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
         'font-family="Segoe UI, Roboto, Helvetica, Arial, sans-serif">',
         f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
         f'<text x="{width / 2}" y="24" text-anchor="middle" font-size="16" font-weight="700" fill="#1f2328">{title}</text>']
    for i in range(6):
        yv = y0 + (y1 - y0) * i / 5
        o.append(f'<line x1="{pad_l}" y1="{Y(yv):.1f}" x2="{pad_l + W}" y2="{Y(yv):.1f}" stroke="#eaeef2"/>')
        o.append(f'<text x="{pad_l - 6}" y="{Y(yv) + 4:.1f}" text-anchor="end" font-size="11" fill="#57606a">{yv:.1f}</text>')
    for i in range(7):
        xv = x0 + (x1 - x0) * i / 6
        o.append(f'<text x="{X(xv):.1f}" y="{pad_t + H + 18}" text-anchor="middle" font-size="11" fill="#57606a">{xv:.2f}</text>')
    o.append(f'<text x="{pad_l + W / 2}" y="{height - 6}" text-anchor="middle" font-size="12" fill="#57606a">thời gian (s)</text>')
    o.append(f'<text x="14" y="{pad_t + H / 2}" text-anchor="middle" font-size="12" fill="#57606a" '
             f'transform="rotate(-90 14 {pad_t + H / 2})">{ylabel}</text>')
    o.append(f'<rect x="{pad_l}" y="{pad_t}" width="{W}" height="{H}" fill="none" stroke="#d0d7de"/>')
    for i, (label, color, pts, dash) in enumerate(series):
        d = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
        da = ' stroke-dasharray="6 4"' if dash else ''
        o.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2"{da}/>')
        lx = pad_l + 12 + i * 220
        o.append(f'<line x1="{lx}" y1="{pad_t + 14}" x2="{lx + 24}" y2="{pad_t + 14}" stroke="{color}" stroke-width="3"{da}/>')
        o.append(f'<text x="{lx + 30}" y="{pad_t + 18}" font-size="12" fill="#1f2328">{label}</text>')
    o.append('</svg>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(o))


# ---------------------------------------------------------------------------------- main ----
def main():
    os.makedirs(OUT, exist_ok=True)
    scenarios = build_scenarios()
    ref = {n: float_outputs(i) for n, i in scenarios.items()}
    n_steps = sum(len(v) for v in scenarios.values())
    lines = ['# Mô hình fixed-point bộ điều khiển PID — kết quả phân tích', '',
             f'Sinh bởi `ic/model/analyze.py`. dt = {DT * 1000:.1f} ms ({1 / DT:.0f} Hz), '
             f'{len(scenarios)} kịch bản, {n_steps} chu kỳ.', '',
             f'Tiêu chí đạt: lệnh motor lệch so với bản float **≤ {MAX_MOTOR_ERR_US} µs** và '
             f'**≤ {MAX_MISMATCH_PCT}%** số chu kỳ có lệch.', '']

    # 1. Quet tung tham so quanh cau hinh "rong rai" (cac tham so khac du bit)
    base = FxConfig(fe=10, wk=18, fa=12, fd=8, fu=10, rnd=True)
    bw, bp, _ = compare(base, scenarios, ref)
    lines += ['## 1. Quét từng tham số', '',
              f'Cấu hình gốc rộng rãi `{base.label()}`: lệch tối đa {bw} µs, {bp:.3f}% chu kỳ lệch.', '',
              'Giảm lần lượt **một** tham số, giữ các tham số khác như cấu hình gốc:', '']
    sweeps = {'fe': range(1, 11), 'wk': range(6, 19, 2), 'fa': range(3, 13), 'fd': range(0, 9), 'fu': range(0, 11)}
    desc = {'fe': 'bit thập phân của góc/sai số', 'wk': 'bit mantissa hệ số', 'fa': 'bit thập phân alpha',
            'fd': 'bit thập phân thêm của bộ lọc D', 'fu': 'bit thập phân tổng P+I+D'}
    minimum = {}
    for p, values in sweeps.items():
        lines += [f'### `{p}` — {desc[p]}', '', '| giá trị | lệch max (µs) | % chu kỳ lệch | đạt |', '|---|---|---|---|']
        for v in values:
            cfg = FxConfig(**{**base.__dict__, p: v})
            w, pct, _ = compare(cfg, scenarios, ref)
            ok = passes(w, pct)
            if ok and p not in minimum:
                minimum[p] = v
            lines.append(f'| {v} | {w} | {pct:.3f} | {"✅" if ok else "❌"} |')
        lines.append('')
        print(f'sweep {p}: min dat = {minimum.get(p)}')

    # 2. Cau hinh A "khop MCU": moi tham so lay muc toi thieu dat tieu chi, kiem tra lai khi ket hop
    chosen = FxConfig(**{**base.__dict__, **minimum})
    bumps = 0
    while True:
        rms_a = []
        w, pct, per = compare(chosen, scenarios, ref, rms=rms_a)
        if passes(w, pct):
            break
        chosen = FxConfig(**{**chosen.__dict__, **{p: getattr(chosen, p) + 1 for p in minimum}})
        bumps += 1
    floor_cfg = FxConfig(**{**chosen.__dict__, 'rnd': False})
    fw, fpct, _ = compare(floor_cfg, scenarios, ref)
    stats = {}
    compare(chosen, scenarios, ref, stats)
    lines += ['## 2. Cấu hình A — khớp thuật toán MCU', '',
              'Ghép các mức tối thiểu ở mục 1 lại' + (
                  f' thì chưa đạt (sai số cộng dồn), nên tăng mỗi tham số thêm {bumps} bit:' if bumps else ' là đạt:'), '',
              f'**`{chosen.label()}`** → lệch tối đa **{w} µs**, **{pct:.3f}%** chu kỳ lệch, '
              f'RMS {rms_a[0]:.3f} µs.', '',
              '| kịch bản | chu kỳ | lệch max (µs) | % chu kỳ lệch |', '|---|---|---|---|']
    for name, (sw, sp) in per.items():
        lines.append(f'| {name} | {len(scenarios[name])} | {sw} | {sp:.3f} |')
    lines += ['', f'Cùng cấu hình nhưng **cắt (floor) thay vì làm tròn** khi dịch phải: lệch tối đa {fw} µs, '
              f'{fpct:.3f}% chu kỳ lệch ({"đạt" if passes(fw, fpct) else "KHÔNG đạt"}). '
              'Làm tròn chỉ tốn thêm một bộ cộng hằng trước mỗi phép dịch.', '',
              f'Ngay cấu hình gốc dư bit cũng lệch {bp:.3f}% chu kỳ: đó là các lần giá trị PID nằm sát ranh giới '
              'số nguyên, phép cắt về 0 cho ra hai kết quả khác nhau 1 µs. Không thể khớp tuyệt đối với float, '
              'chỉ có thể khớp tới mức lệch 1 µs thỉnh thoảng.', '']

    # 3. Alpha nhi phan: doi alpha tren MCU thanh so dang k/2^n de chip khop tuyet doi voi it bit
    alt_alpha = 13 / 64
    saved_alpha = pid_model.DERIV_ALPHA
    pid_model.DERIV_ALPHA = alt_alpha
    ref_alt = {n: float_outputs(i) for n, i in scenarios.items()}
    lines += ['## 3. Đề xuất: đổi alpha bộ lọc D thành số nhị phân', '',
              f'alpha = {saved_alpha} không biểu diễn chính xác được ở hệ nhị phân nên cần fa ≥ {minimum["fa"]} bit '
              f'mới khớp MCU. Nếu đổi alpha trên **cả MCU lẫn chip** thành {alt_alpha} = 13/64 '
              '(bộ lọc gần như y hệt), số bit cần giảm hẳn:', '',
              '| fa | lệch max (µs) | % chu kỳ lệch | đạt |', '|---|---|---|---|']
    alpha_min = None
    for fa in range(4, 10):
        w2, p2, _ = compare(FxConfig(**{**chosen.__dict__, 'fa': fa}), scenarios, ref_alt)
        ok = passes(w2, p2)
        if ok and alpha_min is None:
            alpha_min = fa
        lines.append(f'| {fa} | {w2} | {p2:.3f} | {"✅" if ok else "❌"} |')
    pid_model.DERIV_ALPHA = saved_alpha
    lines += ['', f'→ với alpha = 13/64, chỉ cần **fa = {alpha_min}** (thay vì {chosen.fa}). Muốn áp dụng thì sửa '
              '`kDerivativeAlpha` trong `src/Flight/Flight.cpp` thành `13.0f / 64.0f` và bay thử lại.', '']

    # 4. Danh doi dien tich / chat luong dieu khien
    candidates = [('A — khớp MCU', chosen),
                  ('B — tiết kiệm', FxConfig(fe=6, wk=10, fa=8, fd=2, fu=6)),
                  ('C — tối giản', FxConfig(fe=4, wk=8, fa=6, fd=1, fu=4))]
    lines += ['## 4. Đánh đổi độ chính xác và diện tích', '',
              'Tiêu chí "khớp MCU" rất khắt khe. Về mặt điều khiển, cái cần so là quỹ đạo bay: nhiễu góc của IMU '
              'khoảng 0.3° nên sai lệch nhỏ hơn nhiều so với mức đó là không phân biệt được khi bay.', '',
              '| cấu hình | tham số | lệch max (µs) | % chu kỳ lệch | RMS (µs) | bước roll: lệch góc max | '
              'hover có gió: lệch góc RMS | bit e | bit tích lớn nhất | bit thanh ghi trạng thái (3 trục) |',
              '|---|---|---|---|---|---|---|---|---|---|']
    plot_runs, devs = {}, {}
    for label, cfg in candidates:
        rms = []
        cw, cp, _ = compare(cfg, scenarios, ref, rms=rms)
        step_max, hover_rms, runs = closed_loop_dev(cfg)
        plot_runs[label] = runs
        devs[label] = step_max
        wcc = worst_case_widths(cfg)
        state_bits = 3 * (wcc['acc (tich phan)'] + wcc['e (sai so)'] + wcc['dfilt (dao ham loc)'])
        lines.append(f'| {label} | `{cfg.label()}` | {cw} | {cp:.2f} | {rms[0]:.3f} | {step_max:.4f}° | '
                     f'{hover_rms:.4f}° | {wcc["e (sai so)"]} | {wcc["tich he so x du lieu"]} | {state_bits} |')
    lines += ['', 'Thanh ghi trạng thái mỗi trục = tích phân + sai số trước + đạo hàm lọc.', '',
              f'- **B** lệch MCU ở nhiều chu kỳ hơn nhưng góc bay chỉ lệch tối đa {devs["B — tiết kiệm"]:.2f}°, '
              'nhỏ hơn nhiễu IMU: về điều khiển là tương đương, đổi lại tích nhỏ hơn 8 bit.',
              f'- **C** lệch tới {devs["C — tối giản"]:.2f}° khi đổi setpoint: bắt đầu thấy khác biệt, không nên dùng.',
              '- Chọn A hay B là quyết định thiết kế của nhóm: A dễ chứng minh "chip = thuật toán đã bay thử", '
              'B tiết kiệm diện tích/công suất.', '']

    # 5. He so luong tu hoa (cau hinh A)
    lines += ['## 5. Hệ số sau lượng tử hoá (cấu hình A)', '',
              "Hệ số đã gộp dt và hệ số 3: KP' = 3·kp, KI' = 3·ki·dt, KD' = 3·kd/dt. "
              'Giá trị = mantissa / 2^shift.', '',
              '| trục | hệ số | giá trị thật | mantissa | shift | giá trị lượng tử | sai số |', '|---|---|---|---|---|---|---|']
    coeff_lines = [f'# He so PID cho RTL, cau hinh {chosen.label()}, dt={DT}',
                   '# truc he_so mantissa shift gia_tri_that']
    for a in AXES:
        kp, ki, kd = GAINS[a]
        for nm, val in (("KP'", OUTPUT_SCALE * kp), ("KI'", OUTPUT_SCALE * ki * DT), ("KD'", OUTPUT_SCALE * kd / DT)):
            m, s = quant_coeff(val, chosen.wk)
            q = m / 2 ** s if m else 0.0
            err = f'{(q - val) / val * 100:+.3f}%' if val else '—'
            lines.append(f'| {a} | {nm} | {val:.6g} | {m} | {s} | {q:.6g} | {err} |')
            coeff_lines.append(f'{a} {nm.rstrip(chr(39))} {m} {s} {val:.9g}')
    alpha_q = round(DERIV_ALPHA * (1 << chosen.fa))
    acc_lim = round(INTEGRAL_LIMIT / DT * (1 << chosen.fe))
    lines += ['', f'- alpha bộ lọc D: {DERIV_ALPHA} → {alpha_q}/2^{chosen.fa} = {alpha_q / 2 ** chosen.fa:.5f}',
              f'- Giới hạn tích phân: |A| ≤ {INTEGRAL_LIMIT}/dt = {INTEGRAL_LIMIT / DT:.0f} → {acc_lim} (Q.{chosen.fe})',
              f"- Ngưỡng bão hoà: |u'| ≤ 250 → {250 << chosen.fu} (Q.{chosen.fu})", '']
    coeff_lines += [f'ALPHA {alpha_q} {chosen.fa}', f'ACC_LIM {acc_lim}', f'U_LIM {250 << chosen.fu}',
                    f'FE {chosen.fe}', f'FD {chosen.fd}', f'FU {chosen.fu}', f'ROUND {int(chosen.rnd)}']
    with open(os.path.join(OUT, 'coeffs.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(coeff_lines) + '\n')

    # 6. Do rong datapath (cau hinh A)
    wc = worst_case_widths(chosen)
    observed = {'e (sai so)': 'e', 'acc (tich phan)': 'acc_raw', 'de (hieu sai so)': 'de',
                'dfilt (dao ham loc)': 'dfilt', 'tich he so x du lieu': 'prod', "u' = P+I+D": 'u'}
    lines += ['## 6. Độ rộng bit datapath (cấu hình A, có dấu)', '',
              'Trường hợp xấu nhất tính từ phạm vi đầu vào (góc ±180°, gyro ±2000°/s, setpoint tối đa); '
              'RTL phải dùng **ít nhất** cột này để không bao giờ tràn số.', '',
              '| tín hiệu | xấu nhất (bit) | quan sát trong mô phỏng (bit) |', '|---|---|---|']
    for k, v in wc.items():
        obs = signed_bits(stats[observed[k]]) if k in observed and observed[k] in stats else '—'
        lines.append(f'| {k} | {v} | {obs} |')
    lines += ['', f'Đầu vào chip: góc/tốc độ góc/setpoint dạng Q.{chosen.fe} có dấu, '
              f'{signed_bits(round(2350 * 2 ** chosen.fe))} bit đủ cho ±2350 (sai số yaw lớn nhất).', '']

    # 7. Vong kin: dap ung buoc roll
    tf, tx = plot_runs['A — khớp MCU']
    _, tb = plot_runs['B — tiết kiệm']
    max_dev = max(abs(a[2] - b[2]) for a, b in zip(tf, tx))
    svg_plot(os.path.join(OUT, 'step_roll.svg'), 'Đáp ứng bước roll vòng kín — float (MCU) vs fixed-point',
             [('setpoint', '#8c959f', [(t, s) for t, s, _, _ in tf], True),
              ('float (STM32)', '#1c7ed6', [(t, r) for t, _, r, _ in tf], False),
              ('fixed A', '#d9480f', [(t, r) for t, _, r, _ in tx], True),
              ('fixed B', '#2b8a3e', [(t, r) for t, _, r, _ in tb], True)], 'góc roll (độ)')
    lines += ['## 7. Vòng kín', '',
              'Đáp ứng bước roll (0 → 20° → −10°) trên mô hình drone đơn giản (mỗi trục là vật quay có cản). '
              'Ba đường gần như trùng nhau.', '', '![Đáp ứng bước roll](step_roll.svg)', '']

    # 8. Golden vectors
    cols = ['scenario', 'cycle', 'armed', 'throttle', 'sp_roll', 'sp_pitch', 'sp_yaw', 'roll', 'pitch', 'gz',
            'mix_roll', 'mix_pitch', 'mix_yaw', 'm1', 'm2', 'm3', 'm4']
    with open(os.path.join(OUT, 'golden_vectors.csv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(','.join(cols) + '\n')
        for name, inputs in scenarios.items():
            ctrl = FixedController(chosen)
            for k, inp in enumerate(inputs):
                q = ctrl.quantize_inputs(inp)
                m, mix = ctrl.step_q(q)
                f.write(','.join(map(str, [name, k, q['armed'], q['throttle'], q['sp_roll'], q['sp_pitch'],
                                           q['sp_yaw'], q['roll'], q['pitch'], q['gz'],
                                           mix['roll'], mix['pitch'], mix['yaw'], *m])) + '\n')
    lines += ['## 8. Golden vectors cho RTL (cấu hình A)', '',
              f'`golden_vectors.csv`: {n_steps} chu kỳ, đầu vào đã ở dạng số nguyên Q.{chosen.fe} và đầu ra mong đợi '
              '(mix 3 trục + 4 motor) tính bằng mô hình fixed-point. Testbench RTL đọc file này, đưa đầu vào '
              'vào chip từng chu kỳ và so sánh **bit-exact** với đầu ra. Trạng thái PID reset về 0 ở đầu mỗi kịch bản.',
              '', '`coeffs.txt`: mantissa/shift của hệ số và các hằng số, dùng làm tham số cho RTL.', '']

    with open(os.path.join(OUT, 'report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('chon:', chosen.label(), f'-> lech max {w} us, {pct:.3f}% chu ky; floor: {fw} us {fpct:.3f}%')
    print('vong kin lech toi da', round(max_dev, 4), 'do')
    print('do rong xau nhat:', wc)


if __name__ == '__main__':
    main()
