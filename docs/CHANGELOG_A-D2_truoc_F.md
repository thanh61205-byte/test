# Nhật ký sửa A–D2 trước khi sang F

*Cập nhật 18/10/2026, lần sửa 4. Lần 1 xử lý 7 việc nhóm A. Lần 2 xử lý các mục còn mở trong `Kiem_tra_ban_Claude_sua_A-D2_VI.md` (R1–R4) và toàn bộ phát hiện nhóm B có thể làm ở A–D2. Lần 3 xử lý 3 phát hiện Astra còn nêu sau khi kiểm tra v2 (B02, C202, D203) và lỗi bố cục DOCX (mục 0). Lần 4 xử lý báo cáo kiểm tra v3 (mục 00).*

## 00. Lần sửa 4 (sau kiểm tra v3 của Astra, `Kiem_tra_A-D2_v3_VI.md`)

| Mục Astra nêu | Đã sửa | Bằng chứng |
|---|---|---|
| **V3-01 (D203):** ngày chọn mô hình chưa đồng bộ với fit date mới | `docs/F1_validation_design.md` thêm khái niệm **selection cutoff** (= fit date của mô hình cuối mỗi nhánh). Bảng fit date theo từng nhánh / horizon / fold. Bằng chứng để chọn mô hình pre_arrival chỉ dùng dòng validation có nhãn biết trước cutoff (fold 3 bị cắt). Calibration và threshold theo cùng cutoff. Feature có bước fit (ADR reference, top agent) phải dựng lại cho mô hình pre_arrival cuối cùng; giá trị trong `modeling_dataset.csv` chỉ hợp lệ cho mô hình booking_time cuối cùng | F1 design §§2–3 |
| **V3-02a:** sensitivity lệch 1 ngày | Ghi rõ "cutoff cũ = ngày **trước** cửa sổ" (408/664); nếu dùng chính ngày đầu cửa sổ thì 433/668 (đã tính lại, khớp Astra). NB03: bảng có cột `old_cutoff`, `primary_fit_date` và assert số booking có score ≤ primary fit date = 0 ở mọi cửa sổ; sửa comment "loại ở F1" | NB03 §3.3 |
| **V3-02b:** quy tắc "không score trước fit" phát biểu quá rộng | Quy tắc nghiêm ngặt chỉ áp dụng cho booking-date view và nhánh pre_arrival; arrival-cohort headline ghi rõ là ngoại lệ hồi cứu | F1 design §2, §4 |
| **V3-02c:** "0 nhãn chưa biết" cần nêu theo quy ước | Ghi "0 **theo quy ước** label-known (Check-Out/No-Show → arrival_date); dataset không có log thời điểm ghi nhận" ở F1 design, NB03 và changelog | — |
| **V3-03 (B02):** 96/100 cột | Thêm 4 dòng `is_synthetic` (ops ghi rõ dòng trộn DERIVED + SYNTHETIC). Bỏ ngoại lệ coverage; NB02 assert tập (bảng, cột) của dictionary **bằng đúng** tập cột của cả 10 bảng trong `schema.sql`. Thống nhất `dim_room_type.room_type` = REAL (mã phòng PMS) ở ERD | Dictionary 100 dòng; đối chiếu `information_schema` của PostgreSQL thật: 100/100, không thiếu không thừa |
| **V3-04 (C202):** B2/C2 không phải ITT | B2 đổi thành "late-cancellation share (descriptive, conditional)", ghi rõ không dùng làm hiệu ứng nhân quả. Thêm **B9 = late-cancellation incidence (ITT)** = số hủy muộn / **mọi** booking được phân nhóm (baseline 4,9%). C2 thành guardrail có điều kiện, báo kèm số assigned / stayed / invited / responded theo arm. Chỉ B1, B9, C1, B6/B7 là theo arm trên toàn bộ booking được phân | `docs/kpi_register.csv` (21 KPI) |
| **V3-05:** CHECK approval nhận metadata nửa vời | CHECK hai nhánh: approved/rejected phải có **cả** approved_by và approved_at; auto/pending phải **không có cả hai**. `verify_load.sql` thêm 5 test từ chối và test chấp nhận 4 trạng thái hợp lệ | PostgreSQL 16.15: **30/30 PASS** |
| **DOCX** | Đã dựng trang bằng Microsoft Word trên máy này (xuất PDF hết khoảng 2–3 giây, không treo) và xem từng trang. Phát hiện và sửa: (1) đoạn chứa ảnh bị chép nhầm định dạng đánh số nên hiện heading trống "3." (lỗi do lần sửa 3); (2) ảnh 6,5 inch thì chữ quá nhỏ khi in → vẽ lại hình gọn chữ hơn, đặt trên **một trang ngang riêng** rộng 9 inch; (3) bảng Expected Business Value giãn dòng 1,5 và cấm ngắt hàng (có từ bản gốc) → giãn dòng đơn, cho ngắt hàng, header lặp lại; (4) ô Objective 1 rút gọn, câu phạm vi hồi cứu chuyển xuống ghi chú dưới bảng. 9 → 8 trang | `docs/Problem Statement.pdf` (bản Word xuất ra) |
| **Các điểm nhỏ còn sót từ báo cáo v2** | Decision I2: booking vào nhóm sau mốc 30/14 ngày nhận reminder ngay; thêm thứ tự ưu tiên I5 > I6 > I3 > I2 > I1. DOCX: "targeted contact … only" → "routine confirmation for all; enhanced, prioritised contact for high-risk". NB01: "không đưa **trực tiếp** cột outcome vào key; outcome vẫn có thể ảnh hưởng gián tiếp". Runner: kernel khóa vào đúng interpreter đang chạy (kernelspec tạm) và in phiên bản thư viện | `docs/decision_table_draft.md`, `src/run_notebooks.py` |

Chạy lại sạch 01 → 02 → 03 bằng runner mới (Python 3.13.7, pandas 2.2.3, numpy 2.1.3, scikit-learn 1.6.1); dữ liệu dưới `data/` không đổi giá trị; **76/76** kiểm tra độc lập đạt. Ngưỡng/target vẫn là placeholder (chốt ở F2/G1); guard thực thi phê duyệt vẫn thuộc G2.

## 0. Lần sửa 3 (sau kiểm tra v2 của Astra)

| Mục Astra nêu | Đã sửa |
|---|---|
| **B02:** dictionary thiếu 7 trường system có trong SQL | Thêm `risk_scores.model_version`, `days_to_arrival`; `action_plan.booking_id`, `stay_date`, `room_type`, `approved_by`, `created_at`. Thêm luôn `approved_at` và bảng `pilot_assignment` (mới, xem dòng dưới). NB02 giờ **assert** danh sách cột system khớp DDL trong `schema.sql`; kiểm tra độc lập xác nhận dictionary phủ các trường của 10 bảng trừ 4 cờ `is_synthetic` (96 trường; lần 4 bổ sung đủ 100) |
| **C202:** uplift phải so theo nhóm phân ngẫu nhiên | Schema thêm bảng `pilot_assignment` (pilot_id, booking_id, arm treatment/holdout, stratum, assigned_at). KPI C1, C2, B1, B2, B6, B7 so sánh **theo arm được phân** (intention to treat), tính mọi booking được phân dù liên hệ thành công hay không. Problem Statement và decision table cũng sửa theo |
| **C202:** B6 chưa đồng bộ deposit/handling với contribution mới | B6 tính contribution thực hiện cho từng booking theo đúng cơ sở của NB03 §2.6: ở → gross × (1 − commission) − room cost × nights; hủy → deposit giữ lại − handling + resale × (1 − resale commission) − room cost × resold nights. Phần tăng thêm = (trung bình treatment − trung bình holdout) × số booking treatment − chi phí can thiệp |
| **C202:** KPI approval thiếu timestamp nguồn | `action_plan.approved_at` (mới). P3 = approved_at − created_at. Thêm CHECK: action cần duyệt không được ở trạng thái `auto`; approved/rejected phải có approved_by + approved_at; approved_at ≥ created_at |
| **D203:** pre-arrival có score date trước fit date (408 với H=14, 664 với H=30 ở test) | NB03 §3.3 đếm cho test và cả 3 fold. Ở fold, số này lớn hơn nhiều: 806–1.025 (H=14), 1.646–1.915 (H=30). Quy tắc chính trong `docs/F1_validation_design.md` §5: mô hình pre_arrival của mỗi cửa sổ fit tại **ngày đầu cửa sổ − H − 1 ngày** (test: 2016-12-17 / 2016-12-01), nên mọi score date đều sau fit date và không phải bỏ dòng nào. Phân tích độ nhạy: giữ fit date, loại các booking đó và báo cáo số lượng |
| **DOCX:** ảnh PDMT và bảng Expected Business Value rộng hơn vùng chữ; Word treo khi dựng trang | Lỗi có từ bản gốc. Ảnh PDMT trước đây là ảnh **floating, neo bên trong đoạn heading** "Detailed Expected Business Value" (thụt lề treo, lệch trái −0,38 inch, rộng 7,4 inch). Đã chuyển thành ảnh **inline** trong đoạn riêng, căn giữa ngay sau "PDMT Map", rộng đúng 6,5 inch. Bảng 7: 10.206 → 9.360 dxa, các cột co theo tỷ lệ. Vẫn **chưa render được bằng Word** trên máy kiểm tra |

Chạy lại sạch 01 → 02 → 03 không lỗi; **72/72** kiểm tra độc lập đạt.

## 1. Kết quả chạy lại (lần 2)

- **Môi trường:** Python 3.13, pandas 2.2.3, numpy 2.1.3, scikit-learn 1.6.1, scipy 1.18.1, matplotlib 3.10.0, seaborn 0.13.2, PyYAML 6.0.3. Đã ghi vào `requirements.txt`.
- **Chạy sạch:** `python src/run_notebooks.py` chạy 01 → 02 → 03, mỗi notebook một kernel mới, không lỗi. Execution count liền mạch: 1..30, 1..15, 1..29.
- **Baseline trước khi sửa:** chạy lại bản ZIP lần 1 trong cùng môi trường thì tái lập đủ 11 CSV và `column_groups.json` (chỉ khác ký tự xuống dòng).
- **So với baseline, dữ liệu dưới `data/` sau lần sửa 2–3** (CSV trong `docs/` thay đổi có chủ đích; nói "giống từng byte" chỉ đúng khi so với lần chạy baseline trên cùng máy, còn so với ZIP lần 1 thì khác ký tự xuống dòng CRLF/LF):
  - Giống hệt về giá trị: `bookings_city_clean`, `cx_contact`, `cx_feedback`, `dim_room_type`, `ops_inventory_daily`, `sample_extract_bookings`, `modeling_dataset` (78.892 × 61). Như vậy việc chuyển hằng số sang YAML không làm đổi một giá trị nào.
  - Thay đổi có chủ đích: `fin_booking.csv` thêm cột `rebooked_room_nights`; `bookings_prepared.csv` thêm `syn_rebooked_room_nights`. Các cột cũ không đổi.
  - `data_dictionary.csv`: 96 trường × 12 thuộc tính (lần 3). `kpi_register.csv`: 20 KPI.
- **Kiểm tra độc lập:** 72/72 kiểm tra đạt (lần 3), gồm notebook, dữ liệu, hợp đồng config, tài liệu và đối chiếu tĩnh SQL ↔ CSV.
- **PostgreSQL (đã kiểm thử runtime, lần 3):** cài PostgreSQL 16.15 bằng winget; chạy trên một cluster test tạm (port 5433, đã xoá sau khi chạy): `schema.sql` và `load.sql` chạy không lỗi, 6 bảng đủ dòng (9 / 79.330 × 4 / 7.227). `sql/verify_load.sql` (mới) đạt **25/25**: số dòng, các tổng khớp Python (33.102 hủy; €25.274.069,96; €10.879.659,78; €4.832.439,67; 49.491 đêm bán lại; €42.863,62; occupancy 70,8%), null có điều kiện, và DB từ chối đúng 6 dòng sai (auto khi cần duyệt, duyệt thiếu người/thời điểm, approved_at < created_at, arm sai, booking không tồn tại, số đêm âm). Phát hiện nhỏ: tổng `syn_net_booking_value` của view cao hơn CSV €1,58 vì 158 booking có giá trị đúng bằng nửa cent: SQL làm tròn số thập phân chính xác lên, pandas làm tròn số thực nhị phân xuống. Không phải lỗi load; giữ nguyên dữ liệu và ghi chú trong script. Chạy lại toàn bộ lần thứ hai từ đầu cũng đạt. Lần 4: schema có CHECK hai nhánh cho metadata phê duyệt; `verify_load.sql` mở rộng lên **30/30 PASS**.

## 2. Trạng thái 7 việc nhóm A và R1–R4

| # | Việc | Trạng thái | Sửa ở đâu |
|---|---|---|---|
| 1 | Kiểm tra 32 cột (B01) | Đạt (lần 1) | NB01 cell 9 |
| 2 | Bỏ 2 feature capacity (D202) | Đạt (lần 1) | NB03, `excluded_features` |
| 3 | Phạm vi hồi cứu, 2 bộ feature theo thời điểm (D201) | **Đạt** | Lần 2 bổ sung Objective 1 trong Problem Statement (R3) và thiết kế F1 (`docs/F1_validation_design.md`) |
| 4 | Đổi tên danh sách trung gian | Đạt (lần 1) | NB01/02/03 |
| 5 | Công bố EDA đã xem nhãn 2017 (D205) | Đạt | NB03 (sửa lại số mục cho đúng), README, F1 design |
| 6 | Hướng dẫn model export đã lọc (D103) | **Đạt** | Lần 2 (R4): README, config `scope_note` và NB03 ghi rõ "chỉ lọc chất lượng dữ liệu; lọc eligibility của pre_arrival làm ở F1" |
| 7 | Feature availability | **Đạt** | Lần 2 sửa R1 và R2 (bên dưới) |
| R1 | Block-size không được coi là "biết lúc đặt" | **Đã sửa** | NB01 cells 34–35, NB02 dictionary, NB03 (2.0, 3, 3.2), config `population_note`, README §6.2. Ghi là proxy hồi cứu từ snapshot, chưa xác minh availability. Thí nghiệm booking-time nghiêm ngặt phải bỏ/tạo lại feature **và** quy tắc population |
| R2 | Metadata nhất quán | **Đã sửa** | `adr_clean` = DERIVED ở cả hai bảng (kiểm tra tự động: 25/25 feature trùng provenance). Dictionary tách `needed_at` (lúc nghiệp vụ cần) khỏi `in_dataset_as` (giá trị thực có trong bản trích xuất). `country` ghi "booking-time value not verified", bỏ câu "corrected at check-in for many guests" |
| R3 | Problem Statement cập nhật | **Đã sửa** | `docs/Problem Statement.docx` (chi tiết ở mục 4) |
| R4 | Cách viết thời hạn | **Đã sửa** | Mục 5 của file này; README tách "lọc chất lượng" khỏi "lọc eligibility" |

## 3. Trạng thái 21 phát hiện

| Mã | Trạng thái | Nội dung đã sửa / việc còn lại |
|---|---|---|
| A01 | **Đã sửa** | Problem Statement: các câu về hiện trạng tổ chức được gắn nhãn *Assumed (to validate)*, phân biệt với *Measured*; có thêm ghi chú. NB02 §3.6 và `assumptions.yaml` gọi việc liên hệ thủ công là **giả định**. Con số resale 50,7% (không gồm no-show) được ghi là kết quả mô phỏng |
| A02 | **Đã sửa** | Ngưỡng 75% chỉ còn là tham khảo từ nghiên cứu churn; ngưỡng thật chọn trên validation fold. Bỏ con số 2,27% của Cha (2026): bài báo có tồn tại (Crossref) nhưng không xác minh được con số. Con số 4,20% của Dong & Ling (2015) được ghi đúng căn cứ (ví dụ số 1 khách sạn + 2 website, theo abstract) |
| A03 | **Đã sửa** | Vẽ lại PDMT map (`docs/pdmt_map.png`, đã thay trong DOCX), chia 3 làn: dự báo / quyết định và mô phỏng / phân tích hồi cứu. Mỗi làn có nhãn REAL / DERIVED / SYNTHETIC; có bước staff approval trước khi n8n thực thi; ghi rõ "không có luồng từ làn 3 vào model" |
| B01 | Đã sửa (lần 1) | — |
| B02 | **Đã sửa** | Dictionary có thêm dtype, null rule (được assert theo dữ liệu thật), key, `needed_at`, `in_dataset_as`; thêm khóa của các bảng mở rộng và bảng system. Lần 3: thêm 7 trường system còn thiếu (96 trường, chưa tính 4 cờ `is_synthetic`). Lần 4: đủ 100/100 cột SQL, NB02 assert khớp `schema.sql`, khớp `information_schema` của PostgreSQL |
| C101 | Đã sửa phần tài liệu | Đặc tả approval guard và test cho G2 trong `docs/decision_table_draft.md` §6. Việc code guard vẫn thuộc G2. Lần 3: schema có thêm CHECK cho trạng thái duyệt và `approved_at` |
| C102 | **Đã sửa** | Đã chuyển vào YAML: trần xác suất liên hệ 0,95, ngưỡng lead time 30/180, hệ số ADR 1,3, xác suất chữ thường 0,15, cửa sổ capacity, seed mẫu 7 và 1. Thêm sensitivity range cho các giả định CX, nhãn `proxy_note` cho số liệu quốc tế, ràng buộc capacity ≥ rooms_sold (range đổi thành [1,00; 1,10]). Dữ liệu synthetic sinh ra không đổi giá trị (giống từng byte so với baseline chạy trên cùng máy) |
| C103 | Đã sửa (lần 1) | — |
| C201 | **Bản nháp hoàn chỉnh** | `docs/decision_table_draft.md`: eligibility, quy tắc risk × value × thời gian → action cho 2 population, owner, approval, giới hạn năng lực, điều kiện dừng. **Ngưỡng vẫn là placeholder**, chốt ở F2/G1 |
| C202 | **Đã sửa** | `docs/kpi_register.csv`: 20 KPI có công thức, cohort, kỳ đo, owner, baseline tính từ dữ liệu, trạng thái target và nguồn. Lift@20% dùng event rate của chính cohort đánh giá. Lần 3: uplift/B6/B7 so theo arm phân ngẫu nhiên (`pilot_assignment`), B6 cùng cơ sở contribution với NB03, P3 dùng `approved_at` |
| C203 | **Đã sửa phép tính** | NB02 lưu số đêm bán lại. NB03 §2.6 đưa mọi khoản về **một cơ sở contribution**: contribution mất − deposit giữ lại + chi phí xử lý − contribution của lần bán lại (trừ commission và room cost). Có tham số `deposit_retained_share` và `resale_commission_rate` cùng sensitivity. Tổng proxy ≈ €3,8M; Online TA khoảng 58% (định nghĩa cũ cho ra 65%). Nếu deposit Non Refund được giữ 100% thì Groups và Offline TA/TO chuyển thành lãi ròng. Vẫn là proxy mô phỏng; chi phí can thiệp thuộc ROI ở G1 |
| D101 | **Đã sửa** | `requirements.txt`, `src/run_notebooks.py`, hướng dẫn chạy sạch ở README §10 |
| D102 | **Đã sửa** | NB03 cell 9: kiểm tra theo `booking_id`, có test xáo trộn thứ tự các bảng (kết quả không đổi) |
| D103 | Đã sửa | Xem việc 6 / R4 |
| D201 | Đã sửa phần A–D2 | Phạm vi, Objective 1, thiết kế eligibility pre_arrival trong F1 design. Còn lại: F1 triển khai bộ lọc này |
| D202 | Đã sửa (lần 1) | — |
| D203 | **Thiết kế xong; triển khai ở F1** | NB03 §3.3 đo được: 9.946/27.396 booking test (36,3%) đặt trước cutoff; 218 dòng train có ngày trạng thái sau cutoff đều là Check-Out, **0 nhãn** chưa biết tại cutoff **theo quy ước** label-known (không có log thời điểm ghi nhận để kiểm chứng). `docs/F1_validation_design.md` quy định fit/score/label date, 3 rolling fold trong 2016, refit ADR reference / top-agent trong từng fold, và view theo booking date. Lần 3: thêm quy tắc fit date cho pre_arrival (cửa sổ − H − 1 ngày) và số booking bị ảnh hưởng ở test/fold |
| D204 | **Đã sửa** | NB03 §2.0.1: bảng chéo với `customer_type` (281 Group, 1.552 Contract ở individual, có giải thích) và độ nhạy với 5 quy tắc. 91–98% booking giữ nguyên nhãn; tỷ lệ hủy individual ổn định (27,8–28,3% train, 33,9–34,8% test). F1 phải báo cáo ít nhất quy tắc A và B |
| D205 | Đã sửa phần công bố | Không gọi test là "untouched" |
| D206 | **Đã sửa** | PSI dùng hợp các category, smoothing 0,5 trên count. Có thêm `agent_id`: PSI 1,09, có 40 agent chỉ xuất hiện trong test (5,1% booking test). Heatmap hiện n, ô có n < 30 chỉ hiện count. Câu về Direct đổi thành "≤ 25% ở mọi bin có ≥ 30 booking" (bin > 365 ngày chỉ có 1 booking) |
| D207 | **Đã sửa** | NB03 in số liệu: median ADR 95,0 → 110,7 (+16,5%), mean 99,3 → 118,0 (+18,8%). Lợi ích mùa cao điểm chuyển thành **giả thuyết** cho scenario/pilot |

**Part 3 (bất nhất liên tệp):** stakeholders trong DOCX có thêm CX, Finance, Distribution/Sales, Data team. Comment occupancy trong `assumptions.yaml` sửa thành ~71,3%. Checklist README §9 ghi trạng thái theo từng thành phần. View `v_booking_360` có thêm `syn_rebooked_room_nights`.

## 4. Thay đổi trong Problem Statement (.docx)

Objective 1 mới (phạm vi hồi cứu, 2 thời điểm chấm điểm). Các câu hiện trạng → giả định. 12,0% có ghi rõ mẫu số. Expected value: recall ≥ 70% là mục tiêu tạm thời trên cohort test 2017 (holdout đã khám phá một phần), bỏ `booking_changes` khỏi danh sách dữ liệu, Lift theo cohort, ngưỡng 75% chỉ để tham khảo, sửa căn cứ 4,20%, bỏ 2,27%, net recovery trên một cơ sở contribution. Thêm 4 stakeholder. Thay ảnh PDMT map. Môi trường kiểm tra không có Word/LibreOffice nên **chưa xem bố cục bằng mắt**. Nhóm nên mở file kiểm tra một lần, nhất là ô Objective 1 (dài hơn trước) và 4 dòng stakeholder mới.

## 5. Việc còn lại và thời hạn

Không có việc nào đồng loạt chặn việc **bắt đầu** F, nhưng từng việc phải xong **trước bước sử dụng tương ứng**:

| Việc | Phải xong trước |
|---|---|
| Triển khai F1 theo `docs/F1_validation_design.md`: rolling fold, label maturity, refit trong fold, bộ lọc eligibility pre_arrival, báo cáo theo quy tắc population A và B | Train / so sánh model ở F1 |
| Chọn ngưỡng của decision table và target của KPI (đang là placeholder) | Chọn threshold phục vụ workflow (F2) và trước G1 |
| Nếu F dùng giá trị tiền để weighting / xếp hạng: dùng proxy mới và chạy sensitivity về deposit | Bước weighting / capture theo giá trị |
| Code và test approval guard theo §6 của decision table | Tự động hóa ở G2 |
| Xác nhận các giả định hiện trạng (A01) với giảng viên/case; mở DOCX kiểm tra bố cục | Pitch / nộp bài |
