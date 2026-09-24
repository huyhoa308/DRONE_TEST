# Chip điều khiển PID cho drone — FPOLY UAV

Thư mục cho phần thiết kế vi mạch (Cuộc thi Thiết kế vi mạch cho Đô thị thông minh lần 3). Mục tiêu: đưa bộ điều khiển PID + mixer đang bay trên STM32 ([`src/Flight/Flight.cpp`](../src/Flight/Flight.cpp)) thành vi mạch số.

| Bước | Trạng thái | Thư mục |
|---|---|---|
| 1. Mô hình fixed-point, chọn độ rộng bit | ✅ | [`model/`](model/) |
| 2. RTL Verilog (PID + mixer) | ✅ biên dịch sạch (`vlog -lint`) | [`rtl/`](rtl/) |
| 3. Testbench so bit-exact với golden vectors | ✅ viết xong, ⏳ chưa chạy (cần simulator) | [`tb/`](tb/), [`sim/`](sim/) |
| 4. Tổng hợp / P&R (Genus, Innovus) | ⏳ | — |

## RTL

[`rtl/pid_ctrl.v`](rtl/pid_ctrl.v): PID 3 trục + mixer X-frame, **một bộ nhân dùng chung** chạy tuần tự roll → pitch → yaw. Mỗi mẫu IMU mất 20 chu kỳ clock (6 cho mỗi trục + 2); ở 10 MHz là 2 µs, trong khi chu kỳ điều khiển là 2500 µs.

| Cổng | Hướng | Mô tả |
|---|---|---|
| `clk`, `rst_n` | vào | clock, reset bất đồng bộ mức thấp |
| `sample_valid` | vào | xung 1 chu kỳ khi có mẫu IMU mới, chốt toàn bộ đầu vào |
| `clear` | vào | xoá trạng thái PID (chỉ khi `busy = 0`) |
| `armed`, `throttle[10:0]` | vào | trạng thái arm, ga (µs) |
| `sp_roll/sp_pitch/sp_yaw`, `roll/pitch/gz` | vào | setpoint và đo đạc, số nguyên có dấu Q.FE |
| `m1..m4[10:0]` | ra | lệnh 4 motor (µs, 1000..2000) |
| `mix_roll/pitch/yaw[9:0]` | ra | đầu ra PID từng trục (µs) |
| `out_valid`, `busy` | ra | xung báo kết quả mới / đang tính |

Độ rộng bit, hệ số và giới hạn nằm trong `rtl/pid_params.vh`, file này **sinh tự động**. Đổi cấu hình rồi sinh lại tham số và vector:

```bash
python ic/model/export_rtl.py A
```

Thay `A` bằng `B` để dùng cấu hình tiết kiệm.

## Mô phỏng

Testbench [`tb/tb_pid_ctrl.v`](tb/tb_pid_ctrl.v) đọc `tb/vectors.txt` (16.000 mẫu, 7 kịch bản) và so **bit-exact** từng mẫu với mô hình Python, in `PASS`/`FAIL`.

| Công cụ | Lệnh (từ thư mục gốc repo) |
|---|---|
| Icarus Verilog (miễn phí) | `sh ic/sim/run_iverilog.sh` |
| Cadence Xcelium | `sh ic/sim/run_xcelium.sh` |
| ModelSim/Questa | `cd ic/sim && vsim -c -do run_modelsim.do` |

## Mô hình fixed-point

```bash
python ic/model/analyze.py
```

Chạy khoảng 1 phút, chỉ cần Python 3 (không cần numpy). Kết quả ghi vào `ic/model/out/`:

- [`report.md`](model/out/report.md): toàn bộ phân tích, đọc file này trước.
- `golden_vectors.csv`: đầu vào và đầu ra mong đợi từng chu kỳ, dùng cho testbench RTL.
- `coeffs.txt`: hệ số đã lượng tử hoá, dùng làm tham số RTL.
- `step_roll.svg`: đáp ứng bước vòng kín, float so với fixed.

[`model/pid_model.py`](model/pid_model.py) chứa hai bản:
- `FloatController`: chép đúng từng phép tính của `UpdatePid()` và mixer X-frame trong `Flight.cpp`. Đây là tham chiếu.
- `FixedController`: chỉ dùng phép toán số nguyên (cộng, nhân hằng, dịch, so sánh, bão hoà), đúng những gì RTL sẽ làm. Vì vậy đầu ra của nó là đáp án bit-exact cho RTL.

### Biến đổi để phần cứng không cần phép chia

| Float (STM32) | Fixed (chip) |
|---|---|
| dt đo từ timestamp, thay đổi từng chu kỳ | dt cố định 2.5 ms (400 Hz), chip tự đếm chu kỳ |
| `I += e·dt`, giới hạn \|I\| ≤ 100 | `A += e`, giới hạn \|A\| ≤ 100/dt |
| `D = (e − e_prev)/dt` | `ΔE = e − e_prev`, không chia |
| `u = kp·e + ki·I + kd·Df`, rồi nhân 3 | `u' = KP'·e + KI'·A + KD'·ΔEf` với KP' = 3kp, KI' = 3ki·dt, KD' = 3kd/dt |
| bão hoà \|u\| ≤ 250/3 | bão hoà \|u'\| ≤ 250 |

Mỗi hệ số lưu dạng `mantissa / 2^shift` với shift riêng, vì KI' ≈ 0.0003 còn KD' = 36 (chênh nhau 5 bậc độ lớn).

### Kết quả chính (chi tiết trong `report.md`)

- **Cấu hình A, khớp MCU** (`fe=10 wk=13 fa=13 fd=4 fu=9`): lệnh motor lệch float tối đa 1 µs, ở 0.7% số chu kỳ. Datapath: sai số 23 bit, tích lớn nhất 40 bit.
- **Cấu hình B, tiết kiệm** (`fe=6 wk=10 fa=8 fd=2 fu=6`): góc bay lệch tối đa 0.11°, nhỏ hơn nhiễu IMU (khoảng 0.3°). Tích nhỏ hơn 8 bit so với A.
- **Thành phần D quyết định độ chính xác đầu vào**: KD' = 36 khuếch đại sai số lượng tử của góc.
- **alpha = 0.2 tốn 13 bit.** Đổi alpha thành 13/64 trên cả MCU lẫn chip thì chỉ cần 6 bit.
- **Làm tròn khi dịch phải là bắt buộc:** cắt (floor) thì lệch 2 µs và không đạt tiêu chí.

### Giả định cần nhóm xác nhận

1. **Tần số 400 Hz.** PID trên STM32 chỉ tính lại khi có mẫu IMU mới, mà BNO08x game rotation vector đang ở 2500 µs. Nếu đổi tần số IMU thì chạy lại mô hình với `DT` mới.
2. **Phạm vi chip:** PID 3 trục + mixer + chặn khi chưa arm/ga ≤ 1000. Phần điều hướng GPS và yaw-inhibit nằm ngoài chip (ở MCU).
3. **Đầu vào đã ở dạng Q.fe có dấu.** MCU chuyển góc (độ), gyro (độ/s) và setpoint sang số nguyên trước khi gửi xuống chip.
4. **Trạng thái PID không reset khi disarm**, giống hệt code STM32 hiện tại: tích phân từ lần bay trước được giữ nguyên tới lần arm sau. Nên cân nhắc thêm reset khi arm, trên cả MCU lẫn chip.
5. Bản float dùng số thực double của Python; STM32 dùng float32. Chênh lệch này rất nhỏ so với sai số lượng tử đang xét.
