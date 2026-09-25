# Bài 1 — Từ MOSFET tới cổng CMOS

**Mục tiêu:** hiểu vì sao mọi con chip số đều được xây từ đúng hai loại công tắc; tự tính được trễ và công suất của một cổng; hiểu vì sao chip PID của nhóm gần như không tốn điện khi rảnh.

## 1. MOSFET như một công tắc

Bạn đã học MOSFET dẫn điện nhờ kênh đảo tạo bởi điện áp cổng. Trong mạch số, ta chỉ dùng MOSFET ở **hai trạng thái: dẫn hoàn toàn hoặc tắt hoàn toàn**.

| Loại | Dẫn khi cổng G ở mức | Kéo tốt về phía | Vì sao |
|---|---|---|---|
| **NMOS** | 1 (V_DD) | GND (mức 0) | Kéo lên V_DD thì mất một V_th, chỉ lên được V_DD − V_th |
| **PMOS** | 0 (GND) | V_DD (mức 1) | Ngược lại với NMOS |

Vì vậy quy tắc vàng của CMOS là: **PMOS lo kéo lên 1, NMOS lo kéo xuống 0.**

## 2. Inverter CMOS: cổng đơn giản nhất

Một PMOS nối từ V_DD tới đầu ra, một NMOS nối từ đầu ra xuống GND, hai cổng G nối chung vào đầu vào.

- Vào = 0: PMOS dẫn, NMOS tắt → ra = 1.
- Vào = 1: PMOS tắt, NMOS dẫn → ra = 0.

Ở trạng thái đứng yên, **luôn có một transistor tắt** nằm trên đường từ V_DD xuống GND. Vì thế gần như không có dòng chạy xuyên qua: **công suất tĩnh ≈ 0** (chỉ còn dòng rò). Đây là lý do CMOS thắng mọi công nghệ khác.

## 3. NAND và NOR: quy tắc "song song – nối tiếp"

- **NAND2**: 2 PMOS **song song** (chỉ cần một đầu vào bằng 0 là kéo lên 1) + 2 NMOS **nối tiếp** (cả hai bằng 1 mới kéo xuống 0). Tổng 4 transistor.
- **NOR2**: ngược lại, 2 PMOS **nối tiếp** + 2 NMOS **song song**. Cũng 4 transistor.

Quy tắc chung: mạng PMOS là **đối ngẫu** của mạng NMOS (nối tiếp ↔ song song).

**Vì sao người ta thích NAND hơn NOR?** Hạt tải trong PMOS là lỗ trống, độ linh động chỉ khoảng 1/2–1/3 của electron, nên PMOS "yếu" hơn NMOS cùng kích thước. NOR đặt các PMOS yếu **nối tiếp** nên càng chậm; muốn nhanh bằng NAND phải làm PMOS to hơn nhiều, tốn diện tích.

**NAND là cổng vạn năng**: từ riêng NAND có thể dựng mọi cổng khác. Đó là nội dung Lab 01.

## 4. Trễ của một cổng

Khi đầu ra chuyển từ 1 xuống 0, NMOS đang dẫn giống một điện trở R_on xả điện tích của tụ tải C_L (điện dung dây nối + cổng G của các tầng sau). Thời gian trễ xấp xỉ:

> **t_d ≈ 0,69 · R_on · C_L**

Ví dụ: R_on = 5 kΩ, C_L = 10 fF → t_d ≈ 0,69 × 5·10³ × 10·10⁻¹⁵ ≈ **35 ps**.

Hệ quả: một cổng nối tới **càng nhiều** cổng khác (fan-out lớn) thì C_L càng lớn và càng chậm. Mạch dài nhiều tầng cổng nối tiếp thì cộng dồn trễ. Bài 8 (timing) sẽ dùng đúng ý này để tính tần số tối đa của chip PID.

## 5. Công suất: vì sao chip tốn điện khi chạy

Mỗi lần đầu ra chuyển 0 → 1, tụ C_L được nạp từ nguồn; chuyển 1 → 0 thì xả xuống GND. Năng lượng mất mỗi chu kỳ nạp–xả là C·V_DD². Công suất động của cả chip:

> **P_động = α · C · V_DD² · f**

- α: hệ số hoạt động, tỉ lệ số nút thực sự đổi trạng thái mỗi chu kỳ clock (0..1).
- C: tổng điện dung được chuyển mạch.
- V_DD: điện áp nguồn. Công suất tỉ lệ **bình phương** V_DD, nên giảm điện áp là cách tiết kiệm hiệu quả nhất.
- f: tần số clock.

## 6. Gắn với chip PID của nhóm

Chip PID chạy clock 10 MHz nhưng mỗi mẫu IMU chỉ cần **20 chu kỳ**, và mỗi giây chỉ có 400 mẫu. Mỗi chu kỳ điều khiển dài 10 MHz / 400 Hz = **25.000 chu kỳ clock**, trong đó mạch chỉ bận 20 chu kỳ. Nếu **tắt clock** (clock gating) ở các thanh ghi khi mạch rảnh, α của phần lớn chip gần như bằng 0 trong 99,9% thời gian. Bạn sẽ tự tính con số cụ thể ở câu hỏi 4.

## 7. Thực hành — Lab 01

File: [`labs/01_cmos/`](../labs/01_cmos/)

- `cmos_cells.v` (cho sẵn): inverter và NAND2 dựng từ `pmos`/`nmos`, tức là mô phỏng ở mức transistor.
- `gates_from_nand.v` (**bạn làm**): dựng AND, OR, XOR, NOR **chỉ bằng NAND**. NOT đã làm sẵn làm mẫu.
- Chạy `sh course/labs/01_cmos/run.sh` cho tới khi in `PASS`.

## 8. Câu hỏi

1. Vì sao ở trạng thái đứng yên, inverter CMOS gần như không tiêu thụ dòng? Chuyện gì xảy ra trong khoảnh khắc đầu vào đang chuyển giữa 0 và 1?
2. Vì sao không dùng NMOS để kéo đầu ra lên mức 1? Nếu cố làm vậy, đầu ra lên được tối đa bao nhiêu vôn (V_DD = 1,8 V, V_th = 0,5 V)?
3. Mỗi cổng bạn làm trong Lab 01 tốn bao nhiêu transistor? So với cách làm trực tiếp (AND = NAND + NOT = 6 transistor), dựng mọi thứ từ NAND có lãng phí không, và vì sao thư viện cell của nhà máy vẫn có sẵn đủ loại cổng?
4. Chip PID: tổng điện dung chuyển mạch C = 20 pF, V_DD = 1,8 V, f = 10 MHz, α = 0,15 khi đang tính.
   - a) Tính P_động nếu clock chạy liên tục và mạch luôn hoạt động như lúc đang tính.
   - b) Nếu dùng clock gating để mạch chỉ hoạt động 20 trên mỗi 25.000 chu kỳ, công suất trung bình còn bao nhiêu? Giảm bao nhiêu lần?
   - c) Nếu hạ V_DD từ 1,8 V xuống 1,2 V thì a) giảm bao nhiêu lần?
5. Một cổng có R_on = 8 kΩ, mỗi cổng phía sau góp 3 fF và dây nối góp 2 fF. Tính trễ khi cổng này nối tới 1 cổng, và khi nối tới 4 cổng.
