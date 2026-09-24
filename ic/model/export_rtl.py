"""Xuat tham so + vector kiem thu cho RTL tu mo hinh fixed-point.

Chay:  python ic/model/export_rtl.py [A|B]      (mac dinh A = khop MCU, xem out/report.md)
Sinh ra:
  ic/rtl/pid_params.vh   localparam do rong bit, he so, gioi han  -> `include trong pid_ctrl.v
  ic/tb/vectors.txt      moi dong 1 mau IMU: dau vao Q + dau ra mong doi -> tb_pid_ctrl.v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pid_model import (AXES, DT, GAINS, INTEGRAL_LIMIT, DERIV_ALPHA, MIX_LIMITS, OUTPUT_SCALE, ANGLE_MAX,
                       GYRO_MAX, SP_YAW_MAX, ERR_MAX, FixedController, FxConfig, quant_coeff, signed_bits, to_q)
from analyze import build_scenarios

CONFIGS = {
    'A': FxConfig(fe=10, wk=13, fa=13, fd=4, fu=9, rnd=True),   # khop MCU
    'B': FxConfig(fe=6, wk=10, fa=8, fd=2, fu=6, rnd=True),     # tiet kiem
}
IC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def widths(cfg):
    """Do rong bit tung thanh ghi/day trong pid_ctrl.v (truong hop xau nhat, khong bao gio tran)."""
    in_max = to_q(max(ANGLE_MAX, GYRO_MAX, SP_YAW_MAX), cfg.fe)
    e_max = to_q(ERR_MAX, cfg.fe)
    acc_lim = round(INTEGRAL_LIMIT / cfg.dt * (1 << cfg.fe))
    de_max = (2 * e_max) << cfg.fd
    df_max = de_max + 1
    w = {'W_IN': signed_bits(in_max), 'W_E': signed_bits(e_max), 'W_ACC': signed_bits(acc_lim + e_max),
         'W_DE': signed_bits(de_max), 'W_DF': signed_bits(df_max), 'W_DIFF': signed_bits(de_max + df_max)}
    w['W_E'] = max(w['W_E'], w['W_IN'] + 1)          # e = sp - meas, cung dinh dang dau vao
    w['W_MA'] = max(cfg.wk, cfg.fa) + 1               # he so/alpha la so duong, them 1 bit dau
    w['W_MB'] = max(w['W_E'], w['W_ACC'], w['W_DF'], w['W_DIFF'])
    w['W_P'] = w['W_MA'] + w['W_MB']
    terms = []
    for a in AXES:
        for k, x, xf in ((OUTPUT_SCALE * GAINS[a][0], e_max, cfg.fe),
                         (OUTPUT_SCALE * GAINS[a][1] * cfg.dt, acc_lim + e_max, cfg.fe),
                         (OUTPUT_SCALE * GAINS[a][2] / cfg.dt, df_max, cfg.fe + cfg.fd)):
            m, s = quant_coeff(k, cfg.wk)
            terms.append(((m * x) >> max(0, xf + s - cfg.fu)) + 1)
    u_max = max(sum(terms[i:i + 3]) for i in range(0, 9, 3))
    w['W_U'] = signed_bits(max(u_max, MIX_LIMITS['roll'] << cfg.fu))
    return w, acc_lim


def write_params(cfg, name):
    w, acc_lim = widths(cfg)
    alpha = round(DERIV_ALPHA * (1 << cfg.fa))
    lines = ['// Tu dong sinh boi ic/model/export_rtl.py - KHONG sua tay, sua mo hinh roi chay lai.',
             f'// Cau hinh {name}: {cfg.label()}, dt = {cfg.dt * 1000:.1f} ms',
             '// Dau vao sp_*/roll/pitch/gz: so nguyen co dau Q.FE (do, do/s). Dau ra motor: us.', '',
             f'localparam integer FE     = {cfg.fe};',
             f'localparam integer FD     = {cfg.fd};',
             f'localparam integer FA     = {cfg.fa};',
             f'localparam integer FU     = {cfg.fu};',
             f'localparam integer ROUND  = {int(cfg.rnd)};', '']
    for k, v in w.items():
        lines.append(f'localparam integer {k:<6} = {v};')
    lines += ['', f'localparam integer ALPHA   = {alpha};       // {DERIV_ALPHA} * 2^FA',
              f'localparam integer ACC_LIM = {acc_lim};  // {INTEGRAL_LIMIT}/dt * 2^FE',
              f'localparam integer U_LIM   = {250 << cfg.fu};     // 250 * 2^FU', '']
    for i, a in enumerate(AXES):
        kp, ki, kd = GAINS[a]
        for tag, val, xf in (('P', OUTPUT_SCALE * kp, cfg.fe), ('I', OUTPUT_SCALE * ki * cfg.dt, cfg.fe),
                             ('D', OUTPUT_SCALE * kd / cfg.dt, cfg.fe + cfg.fd)):
            m, s = quant_coeff(val, cfg.wk)
            sh = xf + s - cfg.fu
            assert sh >= 0, f'{a} K{tag}: shift am ({sh}), tang FE hoac giam FU'
            lines.append(f'localparam integer K{tag}_M{i}  = {m};  localparam integer SH_{tag}{i} = {sh};'
                         f'  // {a} K{tag}\' = {val:.6g}')
        lines.append(f'localparam integer MIX_LIM{i} = {MIX_LIMITS[a]};')
    for v in (acc_lim, 250 << cfg.fu, alpha):
        assert v < 2 ** 31, 'hang so vuot 32 bit'
    path = os.path.join(IC, 'rtl', 'pid_params.vh')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    return path, w


def write_vectors(cfg):
    path = os.path.join(IC, 'tb', 'vectors.txt')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = 0
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        for inputs in build_scenarios().values():
            ctrl = FixedController(cfg)
            for k, inp in enumerate(inputs):
                q = ctrl.quantize_inputs(inp)
                m, mix = ctrl.step_q(q)
                f.write(' '.join(map(str, [int(k == 0), q['armed'], q['throttle'], q['sp_roll'], q['sp_pitch'],
                                           q['sp_yaw'], q['roll'], q['pitch'], q['gz'],
                                           mix['roll'], mix['pitch'], mix['yaw'], *m])) + '\n')
                n += 1
    return path, n


if __name__ == '__main__':
    name = sys.argv[1].upper() if len(sys.argv) > 1 else 'A'
    cfg = CONFIGS[name]
    p, w = write_params(cfg, name)
    v, n = write_vectors(cfg)
    print(f'cau hinh {name}: {cfg.label()}')
    print('do rong:', w)
    print(f'-> {p}\n-> {v} ({n} mau)')
