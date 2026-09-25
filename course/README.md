# Khoá học thiết kế vi mạch — từ transistor tới chip PID

Khoá học riêng cho nhóm FPOLY UAV. Mỗi bài có 3 phần:

1. **Bài giảng** trong chat (15–20 phút), cuối bài có câu hỏi để trả lời.
2. **Ghi chú** trong [`lessons/`](lessons/) để đọc lại.
3. **Thực hành** trong [`labs/`](labs/): viết mạch Verilog nhỏ và chạy mô phỏng bằng Icarus trên máy.

Mọi bài đều gắn với con chip thật của nhóm: [`ic/rtl/pid_ctrl.v`](../ic/rtl/pid_ctrl.v).

## Lộ trình

| # | Chủ đề | Gắn với chip PID | Thực hành |
|---|---|---|---|
| 1 | **Từ MOSFET tới cổng CMOS**: inverter, NAND/NOR, trễ, công suất | Chip PID tốn bao nhiêu điện, vì sao tắt clock tiết kiệm | Dựng cổng từ transistor |
| 2 | **Số nhị phân có dấu**: bù 2, tràn số, mở rộng dấu | Vì sao `e` cần 23 bit, `>>>` khác `>>` | Bộ cộng/trừ, phát hiện tràn |
| 3 | **Mạch tổ hợp số học**: bộ cộng, bộ nhân, MUX, dịch | Bộ nhân 14 × 29 là linh kiện to nhất | Bộ nhân, đo số cổng |
| 4 | **Mạch tuần tự**: flip-flop, clock, thanh ghi, setup/hold | Thanh ghi trạng thái A, e_prev, Df | Thanh ghi, bộ đếm |
| 5 | **Máy trạng thái (FSM)** | Lịch 20 chu kỳ IDLE → LOAD → … → MIX | Tự viết một FSM nhỏ |
| 6 | **Verilog để mô tả phần cứng + testbench** | Đọc hiểu từng dòng `pid_ctrl.v` | Viết testbench tự chấm |
| 7 | **Số fixed-point trên chip**: Q-format, làm tròn, bão hoà | Mô hình Python, cấu hình A/B | Tự làm bộ lọc số |
| 8 | **Timing**: đường tới hạn, tần số tối đa, STA | Chip có chạy nổi 10 MHz không | Đo đường tới hạn |
| 9 | **Tổng hợp (synthesis)**: thư viện cell, PDK, diện tích | Chuẩn bị cho Cadence Genus | Tổng hợp thử bằng Yosys |
| 10 | **Physical design**: floorplan, place, CTS, route, DRC/LVS, GDS | Chuẩn bị cho Cadence Innovus | Xem layout mẫu |
| 11 | **Công suất và kiểm chứng nâng cao** | Clock gating, coverage | — |
| 12 | **Ôn thi**: trình bày, câu hỏi giám khảo | Bảo vệ thiết kế của nhóm | Thuyết trình thử |

## Cách chạy lab

Icarus Verilog đã cài ở `C:\iverilog`. Mỗi lab có `run.sh`:

```bash
sh course/labs/01_cmos/run.sh
```

Bài làm đúng sẽ in `PASS`.
