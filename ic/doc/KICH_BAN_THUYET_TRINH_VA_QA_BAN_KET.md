# Kịch bản thuyết trình & Bộ Q&A — Vòng Bán kết

**Nhóm FPOLY UAV (ReShape Lab)** · Đề tài: Vi mạch điều khiển bay số `pid_ctrl` cho UAV quadcopter đô thị thông minh
Nguồn số liệu: `ic/doc/build_semifinal_slides.py` (12 slide), `ic/model/out/report.md`, RTL `ic/rtl/*.v`, `ic/syn/syn_genus.tcl`.

---

## 0. Phân vai & quy ước

| Ký hiệu | Thành viên | Phụ trách nói | Phụ trách Q&A |
|---|---|---|---|
| **TV1** | Nguyễn Trung (Cinq) | Slide 1, 2, 3, 5 | Hệ thống UAV, PCB, kiến trúc RTL, FSM, SPI |
| **TV2** | *(điền tên)* | Slide 4, 6, 8 | Mô hình fixed-point, lượng tử hoá, verification |
| **TV3** | *(điền tên)* | Slide 7, 9, 10 + **bấm Demo** | Cadence Genus, STA, corner, PPA, FoM, normalization |

- Tổng thời lượng phần nói: **10:00** (Slide 1 → Slide 10). Slide 11, 12 là slide dự phòng, chỉ mở khi Hội đồng hỏi.
- Tốc độ nói chuẩn: ~140 từ/phút. Mỗi đoạn thoại đã được cắt theo số giây ghi bên cạnh.
- `[▶ DEMO]` = thời điểm bấm chạy Demo 1 lệnh. `[⏱]` = mốc giờ phải đạt (người bấm giờ giơ tay nếu trễ > 10 s).
- Câu in nghiêng trong ngoặc vuông là **hành động**, không đọc ra.

### Lệnh Demo 1 lệnh (TV3 gõ sẵn trong cửa sổ PowerShell, chữ cỡ ≥ 20pt, chỉ việc nhấn Enter)

```powershell
powershell -ExecutionPolicy Bypass -File ic/sim/run_demo_ban_ket.ps1
```

Kết quả mong đợi (đã chạy thử, tổng khoảng 15 giây): cấu hình B rồi cấu hình A, mỗi cấu hình in `PASS: 16000/16000 mau khop bit-exact voi mo hinh Python` kèm `do tre toi da 20 chu ky clock / mau`; sau đó SPI in `PASS: 100/100 mau khop bit-exact qua SPI (MOSI va MISO)`; cuối cùng bảng tổng `KET QUA TONG: PASS - BIT-EXACT 100% (A, B va SPI)`. Script chỉ in PASS khi mô phỏng thật sự PASS; thiếu `iverilog` hoặc có FAIL thì in chữ đỏ và thoát mã 1.

---

## 1. Lời thoại theo slide (10 phút)

| Slide | Người nói | Bắt đầu | Kết thúc | Thời lượng |
|---|---|---|---|---|
| 1 · Bìa + One-line pitch | TV1 | 0:00 | 0:45 | 45 s |
| 2 · Vị trí trên flow + Spec | TV1 | 0:45 | 1:45 | 60 s |
| 3 · Bài toán đô thị, Edge LLM + ASIC | TV1 | 1:45 | 2:45 | 60 s |
| 4 · Toán học fixed-point không phép chia | TV2 | 2:45 | 3:55 | 70 s |
| 5 · Kiến trúc RTL, FSM 20 chu kỳ | TV1 | 3:55 | 5:05 | 70 s |
| 6 · DSE A vs B + verification | TV2 | 5:05 | 6:05 | 60 s |
| 7 · Bảng so sánh, Normalization, FoM | TV3 | 6:05 | 7:20 | 75 s |
| 8 · Khung quay màn hình + **DEMO LIVE** | TV2 + TV3 | 7:20 | 8:30 | 70 s |
| 9 · Phương án Demo A/B/C, phân vai | TV3 | 8:30 | 9:15 | 45 s |
| 10 · Checklist + lộ trình Chung kết | TV3 | 9:15 | 10:00 | 45 s |

---

### Slide 1 — Bìa & Câu giới thiệu một dòng · TV1 · 0:00 → 0:45

> Kính chào Hội đồng Giám khảo. Em là Nguyễn Trung, đại diện nhóm FPOLY UAV, FPT Polytechnic Đà Nẵng.
>
> Đề tài của nhóm em gói trong một câu: **chúng em lấy thuật toán PID 3 trục và mixer đang bay thật trên STM32, biến nó thành một lõi vi mạch số không phép chia, dùng chung đúng một bộ nhân, tính xong cả ba trục trong 20 chu kỳ clock, tức 2 micro-giây ở 10 MHz.**
>
> *[Chỉ vào 4 ô phía dưới]* Đây không phải một con chip đứng một mình. Nó là tầng thứ tư trong hệ sinh thái nhóm đã tự làm: tầng AI giọng nói và trạm mặt đất 3D, tầng PCB tay cầm tự thiết kế bằng Altium, tầng drone carbon với IMU BNO085, và cuối cùng là tầng vi mạch — trọng tâm hôm nay.

`[⏱ 0:45]`

---

### Slide 2 — Dự án đang ở đâu trên flow & Bảng Spec · TV1 · 0:45 → 1:45

> Trước khi đi vào kỹ thuật, nhóm em xin cho Hội đồng thấy ngay **dự án đang ở đâu**.
>
> *[Chỉ hàng Digital]* Ở nhánh Digital: Spec và kiến trúc, RTL, Verification đã xong — RTL lint sạch, mô phỏng **khớp bit-exact 16.000 trên 16.000 mẫu**. Ô màu cam là việc đang làm: tổng hợp và STA trên Cadence Genus cho cả cấu hình A và B. Ô nét đứt là kế hoạch đến Chung kết: P&R trên Innovus, DRC/LVS, xuất GDS hoặc nạp FPGA để bay HIL.
>
> *[Chỉ hàng System]* Nhánh hệ thống song song: drone và firmware STM32 làm baseline, PCB, simulator 3D đã xong; đang đo benchmark MCU so với chip.
>
> *[Chỉ bảng Spec]* Ba con số cam kết, mỗi số kèm điều kiện: clock 10 MHz, độ trễ 20 chu kỳ bằng 2 micro-giây trong chu kỳ IMU 2,5 mili-giây; sai lệch xung motor so với float tối đa 1 micro-giây, chỉ ở 0,7% số mẫu; và datapath không tràn với góc ±180 độ, gyro ±2000 độ/giây.

`[⏱ 1:45]`

---

### Slide 3 — Vì sao UAV đô thị cần "Edge LLM + chip PID chuyên dụng" · TV1 · 1:45 → 2:45

> Một drone đô thị phải làm cùng lúc hai loại việc trái ngược nhau.
>
> Loại thứ nhất là **nhận thức**: nghe lệnh tiếng Việt qua Gemini Live, GPS, geofence, telemetry. Việc này chạy trên ESP32, chấp nhận trễ vài mili-giây.
>
> Loại thứ hai là **điều khiển tư thế thời gian thực cứng**: cứ 2,5 mili-giây phải đọc IMU, tính PID ba trục, trộn ra bốn motor. Trễ một nhịp, drone lật.
>
> Hiện tại nhóm em phải gắn thêm một con STM32F103 chỉ để chạy đúng hàm `Flight_Update`. Cortex-M3 **không có FPU**, nên mỗi phép float là giả lập phần mềm — khoảng 1.300 chu kỳ lệnh cho một lần cập nhật.
>
> *[Chỉ ảnh phần cứng]* Giải pháp: thay khối STM32 này bằng lõi `pid_ctrl`. Không CPU, không phần mềm, không jitter của hệ điều hành — tính xong trong 20 nhịp clock, rồi nghỉ.

`[⏱ 2:45]` — *TV1 trao lời:* "Phần mô hình toán, xin mời bạn [TV2]."

---

### Slide 4 — Biến đổi đại số không phép chia & độ rộng bit · TV2 · 2:45 → 3:55

> Bước quan trọng nhất trước khi viết một dòng Verilog là **làm cho phần cứng không cần phép chia**.
>
> *[Chỉ bảng]* Vì IMU chạy đều 400 Hz, dt cố định 2,5 mili-giây, nên em gộp dt và hệ số 3 của đầu ra vào thẳng hằng số. Tích phân `I += e·dt` thành `A += e` — chỉ còn phép cộng. Đạo hàm chia dt thành hiệu `e − e_prev`. Ba hệ số kp, ki, kd thành KP' = 1,8, KI' = 0,0003 và KD' = 36.
>
> Từ mô hình Python `analyze.py` quét 7 kịch bản, 16.000 chu kỳ, nhóm em rút ra ba phát hiện:
>
> **Một**, KI' và KD' chênh nhau năm bậc độ lớn, nên mỗi hệ số có **shift riêng**; dùng chung một định dạng Q là mất sạch tích phân.
> **Hai**, khâu D quyết định số bit đầu vào: KD' = 36 khuếch đại sai số lượng tử góc lên 36 lần, nên cần Q.10.
> **Ba**, **làm tròn nửa LSB là bắt buộc**: nếu chỉ cắt bit, sai lệch vọt từ 1 lên 2 micro-giây và trượt tiêu chí.
>
> *[Chỉ đồ thị]* Kết quả vòng kín: đáp ứng bước roll của cấu hình A lệch tối đa 0,013 độ so với float — nhỏ hơn hai mươi lần nhiễu nền của IMU.

`[⏱ 3:55]` — *TV2 trao lời:* "Từ mô hình này, kiến trúc RTL xin mời bạn Trung."

---

### Slide 5 — Kiến trúc `pid_ctrl.v`: FSM 20 chu kỳ & 1 bộ nhân · TV1 · 3:55 → 5:05

> Câu hỏi thiết kế đầu tiên: cần bao nhiêu bộ nhân?
>
> Mỗi trục có bốn phép nhân: lọc D, P, I, D. Ba trục là mười hai. Nhưng hãy nhìn tỉ lệ thời gian: chu kỳ điều khiển là **2.500 micro-giây**, một nhịp clock chỉ **0,1 micro-giây**. Đặt mười hai bộ nhân song song để rồi 99,9% thời gian chúng đứng im là lãng phí diện tích.
>
> Nên nhóm em chọn **một bộ nhân có dấu 14 × 29 bit**, FSM điều phối chạy tuần tự roll → pitch → yaw. *[Chỉ timeline]* Mỗi trục 6 trạng thái: LOAD, FILT, P, I, D, SAT. Điểm then chốt là **chồng lệnh**: ở trạng thái này bộ nhân đang tính phép của bước trước, đồng thời mạch đã nạp toán hạng cho phép kế tiếp — nên bộ nhân bận gần như liên tục.
>
> Ba trục là 18 chu kỳ, cộng 1 chu kỳ chốt đầu vào và 1 chu kỳ mixer X-frame: **đúng 20 chu kỳ**. Trạng thái SAT làm luôn bão hoà và anti-windup: chỉ tích phân khi đầu ra không bão hoà.
>
> *[Chỉ sơ đồ khối]* Toàn bộ độ rộng bit, hệ số và giới hạn được sinh tự động vào `pid_params.vh` từ mô hình Python — không ai sửa tay hằng số.

`[⏱ 5:05]`

---

### Slide 6 — Đánh đổi A vs B & verification bit-exact · TV2 · 5:05 → 6:05

> Vì tham số được sinh tự động, nhóm em có thể **khám phá không gian thiết kế** chứ không chỉ chọn một điểm.
>
> *[Chỉ bảng]* Cấu hình A khớp MCU: bộ nhân 14 × 29, lệch motor tối đa 1 micro-giây. Cấu hình B tiết kiệm: bộ nhân 11 × 21, thanh ghi trạng thái giảm 18%, motor lệch tối đa 4 micro-giây nhưng **góc bay chỉ lệch 0,11 độ — vẫn dưới nhiễu IMU**. Chọn A hay B là quyết định thiết kế có số liệu, không phải cảm tính.
>
> Đề xuất thêm: đổi alpha bộ lọc D từ 0,2 sang 13/64 trên cả MCU lẫn chip, số bit alpha giảm từ 13 xuống 6.
>
> *[Chỉ cột phải]* Verification: testbench tự kiểm, so **bit-exact từng mẫu** với mô hình Python trên 7 kịch bản bay — hover có gió, bước roll/pitch, xoay yaw, gạt cần, kẹt bão hoà, ngẫu nhiên toàn dải, arm/disarm. Để chứng minh testbench thật sự bắt lỗi, nhóm em cố ý sửa sai 1 LSB trong file vector — testbench báo FAIL ngay.

`[⏱ 6:05]` — *TV2 trao lời:* "Về PPA và so sánh, xin mời bạn [TV3]."

---

### Slide 7 — Bảng so sánh, Normalization, FoM · TV3 · 6:05 → 7:20

> Mỗi con số trên bảng này đều có **nhãn bậc và corner** đi kèm.
>
> *[Chỉ hai hàng cam]* Hai hàng trên cùng là của nhóm. Các ô diện tích và công suất đang để trống có chủ ý: đó là **ước tính trước tổng hợp**, sẽ được thay bằng số post-synthesis từ Cadence Genus. Nhóm em không điền số chưa đo vào ô "Post-Synth".
>
> *[Chỉ hàng xanh]* Baseline là STM32F103 chạy chính firmware của drone: 72 MHz, khoảng 18,5 micro-giây cho một lần cập nhật.
>
> Về **FoM**: chip này không đo bằng Gbps. Với bộ điều khiển bay chạy pin, thước đo đúng là **năng lượng cho một lần cập nhật 3 trục** — công suất nhân thời gian tính, đơn vị nano-joule trên vòng lặp, càng nhỏ càng tốt.
>
> Hàng thiết kế đã công bố chỉ được đưa vào bảng sau khi nhóm đối chiếu được DOI và số liệu gốc — nhóm em không đưa số chưa kiểm chứng lên slide.
>
> Về **normalization**: khi so với thiết kế ở node khác — ASIC 180 nm, FPGA, hay MCU — nhóm em quy diện tích về **gate equivalent**, tức số cổng NAND2, độc lập tiến trình; còn công suất quy theo bình phương điện áp và kích thước node như công thức ở ô giữa.
>
> Kết luận ước tính: nhanh hơn MCU khoảng **9 lần** về thời gian tuyệt đối, và tiết kiệm năng lượng mỗi vòng **trên một nghìn lần**.

`[⏱ 7:20]` — *TV3 vừa nói câu cuối vừa chuyển sang Slide 8 và đặt tay lên phím Alt+Tab.*

---

### Slide 8 — Một khung quay màn hình thuyết phục + DEMO LIVE · TV2 (nói) + TV3 (bấm) · 7:20 → 8:30

> **TV2:** Thay vì để Hội đồng tin lời, nhóm em chạy trực tiếp ngay bây giờ.

**`[▶ DEMO — 7:25]`** *TV3: Alt+Tab sang cửa sổ PowerShell đã gõ sẵn lệnh → nhấn **Enter** → Alt+Tab quay lại Slide 8 trong lúc script chạy (≈ 15 s cho cấu hình B, A và SPI).*

> **TV2** *(nói trong lúc script chạy, chỉ vùng 1 trên slide)*: Vùng số 1 là waveform đã zoom vào một mẫu IMU. Xung `sample_valid` lên, `busy` lên, FSM đi qua LOAD, FILT, P, I, D, SAT ba lần, rồi MIX. Con trỏ đặt tại **cộng 2,0 micro-giây** — `out_valid` lên đúng chu kỳ thứ 20, bốn lệnh motor được cập nhật.
>
> Vùng số 3 là phần cứng thật: tay cầm PCB và drone của nhóm.

**`[⏱ ~7:50]`** *TV3: Alt+Tab sang PowerShell, zoom (Ctrl + lăn chuột) vào bảng tổng kết cuối.*

> **TV2** *(chỉ màn hình terminal)*: Đây là kết quả vừa chạy: cấu hình B và cấu hình A — mỗi cấu hình **PASS 16.000 trên 16.000**, độ trễ tối đa 20 chu kỳ. Bảy đầu ra mỗi mẫu, tức 112.000 phép so sánh bit-exact, không lệch một bit nào. Dòng cuối là giao tiếp **SPI 192 bit**: 100 mẫu đi qua đúng 4 dây SPI, khớp bit-exact cả hai chiều.

**Nếu script báo đỏ / treo quá 30 giây → chuyển ngay Phương án B:** *TV3 mở file MP4 quay sẵn (phím tắt đã gán), TV2 nói:* "Đây là bản ghi màn hình nhóm em quay hôm qua với cùng lệnh này." **Nếu video cũng lỗi → Phương án C:** quay lại Slide 8, đọc log PASS trên slide.

`[⏱ 8:30]` — *TV3 Alt+Tab về slide, chuyển Slide 9.*

---

### Slide 9 — Demo luôn có phương án A, B, C · TV3 · 8:30 → 9:15

> Hội đồng vừa xem **phương án A**: chạy trực tiếp một lệnh. Nhóm em luôn chuẩn bị thêm hai lớp dự phòng.
>
> **Phương án B**: video FullHD quay sẵn, mở được trong 10 giây, và nhóm em sẽ nói rõ đó là bản ghi. Ba cảnh: hệ thống thật, testbench và waveform, báo cáo Genus.
>
> **Phương án C**: không cần máy chạy — waveform, log PASS, báo cáo timing, power và coverage đã nhúng trong slide 8, 11, 12.
>
> *[Chỉ thanh dưới]* Phân vai hỏi đáp: bạn Trung trả lời về hệ thống và kiến trúc RTL; bạn [TV2] về lượng tử hoá và verification; em trả lời về Cadence, STA và PPA.

`[⏱ 9:15]`

---

### Slide 10 — Checklist & lộ trình Chung kết · TV3 · 9:15 → 10:00

> Cuối cùng, nhóm em tự rà lại bài theo đúng checklist của Ban Tổ chức.
>
> *[Chỉ cột Design]* Spec có số và điều kiện, slide vị trí trên flow, nhãn bậc và corner, bảng so sánh có nguồn.
> *[Cột Bài trình bày]* Câu giới thiệu một dòng, phân vai, slide dự phòng timing, power, coverage.
> *[Cột Video & demo]* Design chạy và khớp golden model — Hội đồng vừa thấy tận mắt.
>
> Lộ trình đến Chung kết: hoàn tất số post-synthesis đa corner trên Genus, P&R và DRC/LVS trên Innovus và Pegasus, sau đó nạp lõi lên FPGA để **bay thật vòng kín** với chip thay cho STM32.
>
> Nhóm FPOLY UAV xin cảm ơn Hội đồng, và rất mong nhận được câu hỏi.

`[⏱ 10:00]` — **Dừng. Không nói thêm.** Để màn hình ở Slide 10.

---

### Mẹo canh giờ

- Người bấm giờ (TV không nói ở slide đó) giơ **1 ngón** ở mốc 5:05, **2 ngón** ở 8:30. Trễ > 20 s ở 5:05 → TV2 bỏ đoạn "alpha 13/64" ở Slide 6. Trễ ở 8:30 → TV3 nói Slide 9 trong 20 s (chỉ đọc A/B/C).
- Câu cắt được đầu tiên nếu thiếu giờ: Slide 3 đoạn "Gemini Live, GPS, geofence"; Slide 7 đoạn công thức normalization (để dành cho Q&A).
- Tập 3 lần với đồng hồ, ít nhất 1 lần chạy demo thật trên đúng laptop thi.

---

## 2. Bộ 15 câu hỏi xoáy & câu trả lời

> Nguyên tắc: trả lời **≤ 30 giây**, mở bằng kết luận, sau đó một con số, cuối cùng một hướng mở. Nếu chưa có số đo → nói "chưa đo, đây là ước tính, kế hoạch đo là…". **Không bao giờ bịa số.**

### Q1. Tại sao chỉ dùng 1 bộ nhân mà không phải 3 (mỗi trục 1 cái) hay 12? *(TV1)*
**Đáp:** Vì ràng buộc là thời hạn 2.500 µs, không phải thông lượng. Một bộ nhân xong cả ba trục trong 20 chu kỳ = 2 µs, tức dùng 0,08% ngân sách thời gian. Ba bộ nhân rút xuống khoảng 8 chu kỳ — nhanh hơn ở chỗ không ai cần — nhưng diện tích datapath tăng gần 3 lần, vì bộ nhân 14×29 là khối lớn nhất của chip. Ngoài ra lịch FSM đã chồng lệnh, bộ nhân bận 4/6 trạng thái mỗi trục. Khi nào cần thông lượng cao hơn (ví dụ 8 kHz cho drone đua) thì cấu trúc tham số hoá cho phép tách ra.

### Q2. Sao không dùng FPU / IP floating-point cho khỏi lo lượng tử hoá? *(TV2)*
**Đáp:** Vì không cần. Mô hình chứng minh fixed-point lệch float tối đa 1 µs xung motor, góc bay lệch 0,013° — dưới nhiễu IMU 0,3° hơn 20 lần. Một bộ nhân-cộng float32 cần căn chỉnh mũ, chuẩn hoá, làm tròn IEEE: diện tích và công suất lớn hơn nhiều lần bộ nhân nguyên 14×29, và còn phải thêm bộ chia nếu giữ nguyên `/dt`. Nhóm đã loại hẳn phép chia bằng đại số; float là trả tiền cho dải động mà bài toán không dùng.

### Q3. Tại sao không dùng CORDIC? *(TV1)*
**Đáp:** CORDIC giải bài toán lượng giác và quay vector — PID không có phép lượng giác nào, chỉ có nhân-cộng với hằng số. Dùng CORDIC ở chế độ tuyến tính để nhân thì mỗi phép nhân tốn ~N vòng lặp cho N bit (14+ chu kỳ), mỗi trục 4 phép → hơn 160 chu kỳ cho 3 trục thay vì 20, và sai số không còn khớp bit-exact với mô hình làm tròn của chúng em. Nếu sau này đưa phép tính góc Euler từ quaternion vào chip, đó mới là chỗ cho CORDIC.

### Q4. SPI đi vào từ ESP32 với clock khác — xử lý metastability thế nào? *(TV1)*
**Đáp:** Wrapper không dùng `spi_sclk` làm clock. Cả `sclk` và `cs_n` đi qua **chuỗi 3 flip-flop** trong miền `clk`: 2 tầng đầu là bộ đồng bộ, tầng thứ ba để phát hiện cạnh lên/xuống. `mosi` qua 2 flip-flop, cùng độ trễ với `sclk` nên lấy mẫu đúng bit. Như vậy toàn bộ logic chỉ có **một miền clock**, STA chỉ cần một clock, và chỉ có các flip-flop đồng bộ đầu tiên được phép metastable. Dữ liệu chỉ được đẩy vào lõi khi `cs_n` lên và đã đếm đủ bit, nên một khung dở dang không bao giờ làm hỏng trạng thái PID.

### Q5. Vậy SPI chạy tối đa bao nhiêu MHz? Khung lỗi bit thì sao? *(TV1)*
**Đáp:** Vì lấy mẫu quá mẫu bằng `clk`, `f_sclk` phải ≤ khoảng **f_clk/4** — với clk 10 MHz là ~2,5 MHz. Ở 2 MHz, khung 192 bit mất 96 µs + 2 µs tính = ~98 µs, vẫn chỉ ~4% chu kỳ IMU 2.500 µs. Testbench `tb_spi_pid_wrapper.v` đã chạy ở SCLK 1 MHz: **PASS 16.000/16.000** mẫu qua SPI. Muốn SPI nhanh hơn thì nâng `clk` hoặc chuyển sang thanh ghi dịch chạy bằng `sclk` kèm đồng bộ hoá khung bằng handshake. Về lỗi bit: khung có 47 bit dự trữ, kế hoạch là CRC-8 trên các trường, sai CRC thì bỏ khung và giữ lệnh motor cũ.

### Q6. Các bạn chọn corner STA nào, tại sao? *(TV3)*
**Đáp:** **Setup** kiểm ở corner chậm nhất: SS, điện áp thấp (Vdd − 10%), nhiệt độ cao 125°C — với node ≤ 65 nm phải kiểm cả SS nhiệt độ thấp vì hiện tượng đảo nhiệt. **Hold** kiểm ở corner nhanh nhất: FF, điện áp cao, nhiệt độ thấp. Với 100 ns chu kỳ, setup gần như chắc chắn dư; rủi ro thật sự là **hold sau CTS** ở corner FF, nên đó là corner chúng em bám ở bước Innovus. Script Genus chạy mỗi corner một lần (`CORNER=SS` với `slow.lib`, `CORNER=TT` với `typical.lib`), báo cáo tách theo corner; hold ở FF làm bằng MMMC trên Innovus sau CTS.

### Q7. Slack dư hơn 85 ns — vậy chọn 10 MHz là thừa? f_max thật là bao nhiêu? *(TV3)*
**Đáp:** 10 MHz không chọn theo timing mà theo hệ thống: đủ để lấy mẫu SPI và vẫn xong việc rất sớm rồi nghỉ. Năng lượng động mỗi vòng gần như không phụ thuộc tần số (cùng số lần chuyển mạch), nên chạy chậm không tiết kiệm năng lượng mỗi vòng — chỉ giảm công suất đỉnh. Đường găng là bộ nhân 14×29 → cộng làm tròn → cộng 3 số hạng 28 bit. f_max sẽ lấy từ Genus bằng cách quét `PERIOD_NS`; muốn vượt xa thì chèn một thanh ghi pipeline sau bộ nhân, độ trễ tăng từ 20 lên khoảng 23 chu kỳ.

### Q8. FoM "nJ/loop" của các bạn có công bằng không? Bỏ qua công suất nghỉ à? *(TV3)*
**Đáp:** Đúng, `FoM = P_active × 20/f_clk` là năng lượng **tính toán** mỗi vòng. Năng lượng **hệ thống** mỗi chu kỳ 2,5 ms phải cộng thêm rò rỉ: `E = P_active·2 µs + P_leak·2.498 µs`. Ở chu kỳ nghỉ 99,92%, rò rỉ có thể còn lớn hơn phần tính toán, nên chúng em sẽ báo cả hai số, lấy `P_leak` từ `report_power` của Genus. Kể cả cộng rò rỉ ở mức micro-watt, năng lượng mỗi chu kỳ vẫn nhỏ hơn MCU hàng trăm lần, vì MCU không ngủ được giữa các vòng.

### Q9. Normalization giữa ASIC khác node, FPGA và MCU làm thế nào cho đúng? *(TV3)*
**Đáp:** Diện tích quy về **gate equivalent** (chia cho diện tích NAND2 của chính thư viện đó) — độc lập node, đây là cách chính. Công suất quy theo `P × (V_t/V_r)² × (L_t/L_r)` từ `C·V²·f` với C tỉ lệ kích thước — nhóm em biết công thức Dennard này kém chính xác dưới 90 nm, nên chỉ dùng để định bậc độ lớn, không để tuyên bố thắng vài phần trăm. FPGA thì không quy ra GE được tin cậy, nên giữ nguyên LUT/DSP và so ở FoM năng lượng. Và quan trọng nhất: chỉ so **cùng chức năng** — PID 3 trục + mixer.

### Q10. So công suất cả con MCU với riêng lõi ASIC có phải "so táo với cam"? Con số 9,2× tính ra sao? *(TV3)*
**Đáp:** Có một phần đúng: 118,8 mW là dòng chạy toàn chip STM32 ở 72 MHz theo datasheet, gồm cả ngoại vi. Nhưng đó chính là thứ chip chúng em thay thế trên drone, nên ở cấp hệ thống đó là so đúng. Còn 9,2× là thời gian tuyệt đối: 18,5 µs so với 2 µs. Nếu so theo số chu kỳ thì là ~1.330 chu kỳ so với 20, tức ~66×, dù chip chạy clock thấp hơn 7 lần. Số 18,5 µs nhóm sẽ đo lại bằng bộ đếm `DWT->CYCCNT` trên chính board để chuyển nhãn sang "measured".

### Q11. Khi disarm, tích phân có bị giữ lại không? Lần arm sau drone có giật? *(TV1 + TV2)*
**Đáp:** Có — và nhóm em cố ý giữ nguyên hành vi đó để chip **khớp bit-exact với firmware đang bay**. Khi `!armed` hoặc ga ≤ 1000, chip đưa 4 motor về 1000 µs và đóng băng trạng thái PID, giống hệt `Flight.cpp`. Đây là một lỗi tiềm ẩn của firmware gốc mà mô hình đã chỉ ra. Chip đã có sẵn cách sửa: cổng `clear` đồng bộ (trong khung SPI là bit 191) xoá tích phân, sai số trước và đạo hàm lọc cho cả 3 trục trong 1 chu kỳ. Chính sách đề xuất: MCU gửi khung `clear` ở **cạnh lên của arm**, áp dụng đồng thời trên STM32 để hai bên vẫn khớp nhau. Testbench đã kích `clear` ở đầu mỗi kịch bản.

### Q12. Các bạn giả định dt cố định 2,5 ms. IMU bị jitter hoặc rớt mẫu thì sao? *(TV2)*
**Đáp:** Chip không đo dt; nó tính một lần cho mỗi xung `sample_valid`, nên tần số điều khiển do IMU quyết định. BNO085 tự định thời nội bộ ở 400 Hz, jitter vào nhỏ so với 2,5 ms, và sai số dt chỉ ảnh hưởng tuyến tính tới khâu I và D. Rớt một mẫu thì chip giữ lệnh motor cũ — giống MCU. Nếu đổi tần số IMU thì chạy lại `analyze.py` với `DT` mới, script sinh lại hệ số và vector — không phải sửa RTL bằng tay.

### Q13. Golden model do chính nhóm viết — nếu mô hình sai thì RTL cũng "PASS" sai theo? *(TV2)*
**Đáp:** Đúng là có rủi ro lỗi chung, nên nhóm em kiểm hai tầng. Tầng 1: `FloatController` chép từng dòng của `UpdatePid()` trong `Flight.cpp` — đoạn code đã bay thật — và mô hình fixed-point được đo lệch so với nó (≤ 1 µs). Tầng 2: RTL so bit-exact với mô hình fixed-point. Thêm vào đó là fault injection 1 LSB để chứng minh testbench bắt lỗi. Việc còn thiếu và sẽ làm trước Chung kết: đo **code coverage** (line/toggle/FSM) bằng Xcelium + IMC, và đối chiếu thêm với log bay thật lấy từ STM32.

### Q14. Chứng minh datapath không bao giờ tràn? Anti-windup làm thế nào? *(TV2)*
**Đáp:** Độ rộng bit tính theo **trường hợp xấu nhất** từ dải đầu vào chứ không theo quan sát: sai số 23 bit đủ cho ±2.350 (sai số yaw lớn nhất), tích phân 27 bit, tích lớn nhất 40 bit — RTL dùng ít nhất bằng cột đó. Tích phân bị kẹp `|A| ≤ 100/dt` như firmware, và chỉ được cập nhật khi đầu ra **không bão hoà** (tích phân có điều kiện) — kịch bản `ket_bao_hoa` ép chip vào đúng nhánh này. Làm tròn: cộng `2^(n−1)` trước khi dịch phải; chỉ tốn một bộ cộng hằng và là điều kiện để đạt ≤ 1 µs.

### Q15. Bảng PPA vẫn còn "[__]". Vậy số nào đã đo, số nào là ước tính? *(TV3)*
**Đáp:** Nói thẳng: **đã đo** là chức năng — PASS 16.000/16.000 trên RTL, độ trễ 20 chu kỳ, sai số lượng tử từ mô hình. **Ước tính** là diện tích ~2,8–3,5k GE và công suất ~0,25 mW — chưa phải post-synthesis. Script `syn_genus.tcl` đã sẵn, chỉ chờ trỏ `PDK_LIB` tới thư viện trên server Cadence của cuộc thi; khi có report, ô trống được điền kèm nhãn "Post-Synth · corner". Chúng em để trống có chủ đích thay vì điền số đẹp.

---

## 3. Các điểm đã sửa sau khi đối chiếu slide với code

| # | Vấn đề | Trạng thái |
|---|---|---|
| 1 | Slide 12 ghi SPI 10 MHz, 19,2 µs (không khả thi vì SCLK lấy mẫu bằng clk 10 MHz) | ✅ Sửa thành SCLK ≤ f_clk/4, ví dụ 2 MHz → 98 µs; thêm kết quả PASS 16.000/16.000 qua SPI |
| 2 | `run_demo_ban_ket.ps1` in PASS cố định kể cả khi FAIL | ✅ Viết lại: chỉ PASS khi `vvp` in `PASS:`; thiếu iverilog hoặc FAIL thì báo đỏ, thoát mã 1; thêm bước kiểm thử SPI |
| 3 | Log Slide 8 có dòng testbench không in ra | ✅ Thay bằng output thật của script |
| 4 | Nhãn corner TT/SS nhưng script Genus chỉ một `.lib`, chưa đọc wrapper | ✅ `syn_genus.tcl` nhận `CORNER`, `TOP`, đọc cả `spi_pid_wrapper.v`, báo cáo theo corner; nhãn slide đổi thành "Ước tính · chờ Post-Synth TT/SS" |
| 5 | Slide 11 nói bật clock gating nhưng script không bật | ✅ Thêm `set_db lp_insert_clock_gating true` và `report_clock_gating` |
| 6 | Trích dẫn [1] Lee et al. và [2] Hassan et al. | ✅ Tìm không ra bài khớp mô tả → gỡ khỏi bảng Slide 7 và tài liệu; chỉ thêm lại khi có DOI và số liệu gốc |
| 7 | Nhãn "Measured Silicon · 90nm" của STM32 | ✅ Đổi thành "Datasheet DS5319 · thời gian ước tính" |
| 8 | Slide 6 nói `clear` "khắc phục" lỗi giữ tích phân | ✅ Viết lại đúng như Q11 |
| 9 | Comment wrapper ghi ~160 bit, slide ghi 223 chân | ✅ Thống nhất ~223 chân |
| 10 | 7 chân + VDD/VSS ghi "vừa SOIC-8"; wrapper còn cổng `busy` | ✅ Sửa thành 9 chân, vỏ QFN-16; ghi rõ `busy` là tùy chọn |

**Còn phải làm (cần công cụ / phần cứng của nhóm):**
- Chạy `syn_genus.tcl` trên server Cadence (chưa chạy được ở máy cá nhân) để điền số diện tích, công suất vào Slide 7.
- Đo 18,5 µs trên STM32 bằng `DWT->CYCCNT`.
- Nếu nhóm có bài báo gốc để so sánh, thêm lại hàng vào Slide 7 kèm DOI.
