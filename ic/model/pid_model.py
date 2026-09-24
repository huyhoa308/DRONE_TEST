"""Mo hinh bo dieu khien PID cho chip: ban float (tham chieu) va ban fixed-point (bit-accurate).

Ban float chep dung tung phep tinh cua UpdatePid() + mixer trong src/Flight/Flight.cpp (dang bay
tren STM32). Ban fixed-point chi dung phep toan so nguyen: cong, nhan voi hang so, dich, so sanh,
bao hoa - dung nhung gi RTL se lam - nen ket qua cua no chinh la "dap an" cho testbench RTL.

Bien doi chinh so voi ban float (de phan cung khong can phep chia):
  * dt co dinh (chip tu dem chu ky 400 Hz), gop vao he so:
        KP' = 3*kp          KI' = 3*ki*dt          KD' = 3*kd/dt
    (so 3 la kPidOutputScale, gop luon de dau ra PID chinh la don vi "us" cua mixer).
  * Tich phan luu dang tong sai so A = sum(e) (khong nhan dt moi chu ky):
        I_float = A*dt  ->  gioi han |I| <= 100 thanh |A| <= 100/dt.
  * Dao ham luu dang hieu sai so da loc Dd = D_float*dt, loc bang alpha luong tu hoa.
  * Nguong bao hoa: |3u| <= 250 (tuong duong |u| <= 250/3 trong ban float).
"""
from dataclasses import dataclass

DT = 0.0025                 # 400 Hz: BNO08x game rotation vector moi 2500 us (IMU.cpp)
MIX_LIMIT = 250             # kMixLimit
YAW_MIX_LIMIT = 80          # kYawMixLimit
OUTPUT_SCALE = 3.0          # kPidOutputScale
SAT_LIMIT = MIX_LIMIT / OUTPUT_SCALE   # kPidSaturationLimit
INTEGRAL_LIMIT = 100.0      # kPidIntegralLimit
DERIV_ALPHA = 0.2           # kDerivativeAlpha

AXES = ('roll', 'pitch', 'yaw')
GAINS = {                   # ResetPIDConfig() trong src/config.cpp
    'roll': (0.60, 0.040, 0.03),
    'pitch': (0.61, 0.041, 0.03),
    'yaw': (1.30, 0.0, 0.0),
}
MIX_LIMITS = {'roll': MIX_LIMIT, 'pitch': MIX_LIMIT, 'yaw': YAW_MIX_LIMIT}

# Pham vi dau vao that (dung de tinh do rong bit truong hop xau nhat)
ANGLE_MAX = 180.0           # roll/pitch tu IMU, do
SP_ANGLE_MAX = 35.0         # roll_sp/pitch_sp +/-350 phan muoi do
GYRO_MAX = 2000.0           # BNO08x gyro full-scale, do/s
SP_YAW_MAX = 350.0          # yaw_rate_sp +/-350 do/s
ERR_MAX = max(ANGLE_MAX + SP_ANGLE_MAX, GYRO_MAX + SP_YAW_MAX)   # 2350


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def trunc_to_zero(x):
    """static_cast<int32_t>(float): cat phan thap phan ve phia 0."""
    return int(x)


def mix_motors(throttle, r, p, y):
    """X-frame: M1 truoc-trai, M2 truoc-phai, M3 sau-phai, M4 sau-trai (Flight.cpp)."""
    return (clamp(throttle + p + r - y, 1000, 2000),
            clamp(throttle + p - r + y, 1000, 2000),
            clamp(throttle - p - r - y, 1000, 2000),
            clamp(throttle - p + r + y, 1000, 2000))


def gated(inp):
    """Flight.cpp: chua arm hoac ga <= 1000 -> 4 motor 1000, PID dung yen (khong cap nhat)."""
    return (not inp['armed']) or inp['throttle'] <= 1000


# --------------------------------------------------------------------------- float ----

class FloatPid:
    def __init__(self, kp, ki, kd, dt=DT):
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.integral = 0.0
        self.prev = 0.0
        self.dfilt = 0.0

    def update(self, error):
        dt = self.dt
        raw_i = self.integral + error * dt
        raw_d = (error - self.prev) / dt
        self.dfilt += (raw_d - self.dfilt) * DERIV_ALPHA
        u = self.kp * error + self.ki * raw_i + self.kd * self.dfilt
        sat = clamp(u, -SAT_LIMIT, SAT_LIMIT)
        if abs(u) <= SAT_LIMIT:
            self.integral = clamp(raw_i, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)
        self.prev = error
        return sat


class FloatController:
    """PID 3 truc + mixer, dung nhu Flight_Update() (bo phan nav/GPS, yaw-inhibit nam ngoai chip)."""

    def __init__(self, dt=DT):
        self.pid = {a: FloatPid(*GAINS[a], dt) for a in AXES}
        self.mix = {a: 0 for a in AXES}

    def step(self, inp):
        if gated(inp):
            return (1000, 1000, 1000, 1000), dict(self.mix)
        err = {'roll': inp['sp_roll'] - inp['roll'],
               'pitch': inp['sp_pitch'] - inp['pitch'],
               'yaw': inp['sp_yaw'] - inp['gz']}
        for a in AXES:
            u = self.pid[a].update(err[a])
            self.mix[a] = clamp(trunc_to_zero(u * OUTPUT_SCALE), -MIX_LIMITS[a], MIX_LIMITS[a])
        thr = clamp(inp['throttle'], 1000, 2000)
        return mix_motors(thr, self.mix['roll'], self.mix['pitch'], self.mix['yaw']), dict(self.mix)


# --------------------------------------------------------------------------- fixed ----

@dataclass(frozen=True)
class FxConfig:
    fe: int = 6       # so bit thap phan cua goc / toc do goc / sai so  (Q.fe)
    wk: int = 12      # so bit mantissa (khong dau) cua moi he so KP'/KI'/KD'
    fa: int = 8       # so bit thap phan cua alpha bo loc dao ham
    fd: int = 4       # so bit thap phan THEM cho trang thai bo loc dao ham
    fu: int = 6       # so bit thap phan cua tong dau ra u' = 3u
    rnd: bool = True  # lam tron (cong 1/2 LSB) khi dich phai; False = cat (floor)
    dt: float = DT

    def label(self):
        return f"fe={self.fe} wk={self.wk} fa={self.fa} fd={self.fd} fu={self.fu} rnd={int(self.rnd)}"


def quant_coeff(value, wk):
    """He so duong -> (mantissa, shift): value ~= m / 2^shift, m < 2^wk, shift lon nhat co the.

    Moi he so co shift rieng (co dinh luc thiet ke) vi KI' ~ 6e-4 con KD' ~ 36: mot dinh dang Q
    chung se phi bit hoac mat do chinh xac.
    """
    if value == 0:
        return 0, 0
    shift = 0
    while round(value * 2 ** (shift + 1)) < 2 ** wk and shift < 48:
        shift += 1
    m = round(value * 2 ** shift)
    assert 0 < m < 2 ** wk, (value, wk, m, shift)
    return m, shift


def shr(x, n, rnd):
    """Dich phai so hoc n bit (n >= 0), tuy chon lam tron 1/2 LSB nhu RTL: (x + 2^(n-1)) >>> n."""
    if n <= 0:
        return x << -n
    if rnd:
        x += 1 << (n - 1)
    return x >> n


def to_q(x, frac):
    """Luong tu hoa gia tri thuc dau vao chip (lam ben ngoai chip, vd ESP32/STM32 gui xuong)."""
    return int(round(x * (1 << frac)))


class FixedPid:
    def __init__(self, kp, ki, kd, mix_limit, cfg: FxConfig, stats=None):
        c = self.cfg = cfg
        self.kp = quant_coeff(OUTPUT_SCALE * kp, c.wk)
        self.ki = quant_coeff(OUTPUT_SCALE * ki * c.dt, c.wk)
        self.kd = quant_coeff(OUTPUT_SCALE * kd / c.dt, c.wk)
        self.alpha = round(DERIV_ALPHA * (1 << c.fa))
        self.acc_lim = round(INTEGRAL_LIMIT / c.dt * (1 << c.fe))
        self.u_lim = MIX_LIMIT << c.fu            # |3u| <= 250
        self.mix_limit = mix_limit
        self.acc = 0        # Q.fe   tong sai so (tich phan / dt)
        self.prev = 0       # Q.fe   sai so chu ky truoc
        self.dfilt = 0      # Q.(fe+fd)  hieu sai so da loc (dao ham * dt)
        self.stats = stats  # dict ten_tin_hieu -> |gia tri| lon nhat, de suy ra do rong bit

    def _term(self, coeff, x, x_frac):
        m, s = coeff
        prod = m * x                                   # Q.(x_frac + s)
        self._track('prod', prod)
        return shr(prod, x_frac + s - self.cfg.fu, self.cfg.rnd)   # -> Q.fu

    def _track(self, name, v):
        if self.stats is not None and abs(v) > self.stats.get(name, 0):
            self.stats[name] = abs(v)

    def update(self, e):
        c = self.cfg
        acc_raw = self.acc + e
        de = (e - self.prev) << c.fd                   # Q.(fe+fd)
        self.dfilt += shr((de - self.dfilt) * self.alpha, c.fa, c.rnd)
        p = self._term(self.kp, e, c.fe)
        i = self._term(self.ki, acc_raw, c.fe)
        d = self._term(self.kd, self.dfilt, c.fe + c.fd)
        u = p + i + d                                  # Q.fu, u' = 3u
        sat = clamp(u, -self.u_lim, self.u_lim)
        if -self.u_lim <= u <= self.u_lim:             # anti-windup: chi tich phan khi khong bao hoa
            self.acc = clamp(acc_raw, -self.acc_lim, self.acc_lim)
        self.prev = e
        for name, v in (('e', e), ('acc_raw', acc_raw), ('de', de), ('dfilt', self.dfilt), ('u', u)):
            self._track(name, v)
        mix = sat >> c.fu if sat >= 0 else -((-sat) >> c.fu)   # cat ve phia 0 nhu static_cast
        return clamp(mix, -self.mix_limit, self.mix_limit)


class FixedController:
    def __init__(self, cfg: FxConfig, stats=None):
        self.cfg = cfg
        self.pid = {a: FixedPid(*GAINS[a], MIX_LIMITS[a], cfg, stats) for a in AXES}
        self.mix = {a: 0 for a in AXES}

    def quantize_inputs(self, inp):
        f = self.cfg.fe
        return {'armed': int(bool(inp['armed'])), 'throttle': int(inp['throttle']),
                **{k: to_q(inp[k], f) for k in ('sp_roll', 'sp_pitch', 'sp_yaw', 'roll', 'pitch', 'gz')}}

    def step_q(self, q):
        """Mot chu ky chip voi dau vao da o dang so nguyen Q.fe (dung khi xuat golden vector)."""
        if gated(q):
            return (1000, 1000, 1000, 1000), dict(self.mix)
        err = {'roll': q['sp_roll'] - q['roll'],
               'pitch': q['sp_pitch'] - q['pitch'],
               'yaw': q['sp_yaw'] - q['gz']}
        for a in AXES:
            self.mix[a] = self.pid[a].update(err[a])
        thr = clamp(q['throttle'], 1000, 2000)
        return mix_motors(thr, self.mix['roll'], self.mix['pitch'], self.mix['yaw']), dict(self.mix)

    def step(self, inp):
        return self.step_q(self.quantize_inputs(inp))


def signed_bits(max_abs):
    """So bit co dau toi thieu de chua duoc +/-max_abs."""
    return max(1, int(max_abs).bit_length() + 1)


def worst_case_widths(cfg: FxConfig):
    """Do rong bit tung tin hieu trong datapath, tinh tu pham vi dau vao (khong phu thuoc mo phong).

    RTL phai dung it nhat cac do rong nay de KHONG BAO GIO tran so.
    """
    e = to_q(ERR_MAX, cfg.fe)
    acc_lim = round(INTEGRAL_LIMIT / cfg.dt * (1 << cfg.fe))
    acc_raw = acc_lim + e
    de = (2 * e) << cfg.fd
    dfilt = de + 1                                   # to hop loi cua de, +1 do lam tron
    filt_prod = (de + dfilt) * round(DERIV_ALPHA * (1 << cfg.fa))
    coeffs = {a: [quant_coeff(OUTPUT_SCALE * k, cfg.wk) for k in
                  (GAINS[a][0], GAINS[a][1] * cfg.dt, GAINS[a][2] / cfg.dt)] for a in AXES}
    prods, terms = [], []
    for a in AXES:
        (pm, ps), (im, is_), (dm, ds) = coeffs[a]
        for m, s, x, xf in ((pm, ps, e, cfg.fe), (im, is_, acc_raw, cfg.fe), (dm, ds, dfilt, cfg.fe + cfg.fd)):
            prods.append(m * x)
            terms.append(shr(m * x, xf + s - cfg.fu, False) + 1)
    u = max(sum(terms[i:i + 3]) for i in range(0, len(terms), 3))
    return {
        'e (sai so)': signed_bits(e),
        'acc (tich phan)': signed_bits(acc_raw),
        'de (hieu sai so)': signed_bits(de),
        'dfilt (dao ham loc)': signed_bits(dfilt),
        'tich bo loc (de-dfilt)*alpha': signed_bits(filt_prod),
        'tich he so x du lieu': signed_bits(max(prods)),
        "u' = P+I+D": signed_bits(u),
    }
