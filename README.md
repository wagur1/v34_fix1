# v34_fix1 — V34 + Fix1 (thử nghiệm cải tiến)

Fork từ [`munnn01/adaptive_preprocessing`](https://github.com/munnn01/adaptive_preprocessing) (commit `307b77a`), áp dụng nhóm sửa đổi "Fix1" nhắm vào các điểm yếu tìm được khi phân tích kết quả V34-R1 (AR/OT) và V34 OD:

- nhánh `calibrated` bị "chết" (chọn identity ~100%) vì bound hiệu chuẩn lớn hơn `damage_tolerance = 0.05`;
- head phân loại hội tụ về gần một action duy nhất trên AR dù nhãn train đa dạng;
- seed OD không ổn định (lệch ~5pp BD-rate giữa các seed);
- QP50 làm mAP OD sụp đổ, chỉ nên dùng 4 mức QP 30/35/40/45.

README gốc của upstream được giữ nguyên tại [`docs/upstream_readme.md`](docs/upstream_readme.md).

## Thay đổi chính so với upstream

| # | File | Thay đổi |
|---|------|----------|
| 1 | `configs/v34.json`, `configs/v34_arot_r1.json`, `adaptive_vcm/v34/protocol.py` | Bỏ QP50, chỉ dùng `qps = [30,35,40,45]`. |
| 2 | `adaptive_vcm/v34/learning.py`, `model.py` | **Loss theo từng task**: `targets_per_task()` sinh nhãn rate-aware riêng cho từng task đang hoạt động; đầu `Controller` có thể xuất logits riêng theo task (`task_logits=True`, xếp hạng mỗi task độc lập) + CE per-task có mặt nạ (`task_ce_weight`). Logits tổng hợp chỉ lấy các task active. |
| 3 | `adaptive_vcm/v34/learning.py` | **Risk head = pinball/quantile loss** (`risk_loss: "pinball"`, `risk_quantile: 0.9`): dự đoán trực tiếp cận trên 90% của damage thay vì trung bình, nhờ đó bound hiệu chuẩn không còn bị đẩy vống lên (nguyên nhân calibrated arm chết). |
| 4 | `adaptive_vcm/v34/evaluation.py`, `model.py` | **Nhánh ensemble**: trung bình logits/risk/rate của 3 seed (`EnsembleController`), calibration hợp nhất theo phần tử; xuất hiện tự động trong `evaluate()`, `run_v34_od.py` và protocol độc lập. |
| 5 | `adaptive_vcm/v34/tasks.py` | **Sửa guard cho OD**: `costs(..., source_only=True)` với hàng `od` giờ đo khoảng cách detection/feature so với *nguồn* (không dùng nhãn GT như trước). Guard nguồn thực đo trên pixel đã decode, cho phép dùng cho OD mà không rò GT. |
| 6 | `adaptive_vcm/v34/evaluation.py` | Shortlist guard thêm action `calibrated` trước xếp hạng model; `source_shortlist` cấu hình được (5 cho Fix1). |
| 7 | `scripts/run_v34_od.py` | Thêm arm `calibrated_*` (đo trực tiếp hiệu quả fix hiệu chuẩn) và các arm `*_ensemble`; bật guard nguồn khi config có `source_guard_limits`. |
| 8 | `adaptive_vcm/v34/holdout.py` | Protocol độc lập chấp nhận arm ensemble (khớp lưới arm khi `ensemble=true`), thêm so sánh `selected_ensemble`. |
| 9 | `tests/test_v34_fix1.py` | Test cho per-task targets, pinball loss, ensemble, checkpoint `task_logits`. |

Checkpoint cũ (5 đầu ra/action) vẫn nạp được: cờ `task_logits` mặc định `False` và được lưu trong file checkpoint mới.

## Chạy trên Kaggle (OD benchmark, COCO 2017)

```powershell
# push (tự lấy commit HEAD của repo này)
python scripts/submit_fix1_od_kaggle.py push --account wagur124705 --pool "C:\Users\Wagur1\Downloads\pool (2).json"

# theo dõi trạng thái
python scripts/submit_fix1_od_kaggle.py status --account wagur124705 --pool "C:\Users\Wagur1\Downloads\pool (2).json"

# tải kết quả về
python scripts/submit_fix1_od_kaggle.py output --account wagur124705 --pool "C:\Users\Wagur1\Downloads\pool (2).json"
```

Kernel tự clone repo này tại commit đang push, cài `pycocotools`, tìm `val2017` + `instances_val2017.json` trong `/kaggle/input`, rồi chạy `scripts/run_v34_od.py` với `configs/v34.json` (48 train / 16 cal / 16 dev / 64 test, GPU T4).

## Chạy local

```powershell
python -m pytest tests -q          # 48 test không-codec; 3 test codec cần FFmpeg chuẩn (thất bại cục bộ với FFmpeg 9)
python -m adaptive_vcm.v34.runner  # pipeline đầy đủ AR+OD/AR+OT như upstream
```

## Phạm vi / lưu ý

- Fix1 là **protocol thử nghiệm mới**: kết quả không so 1:1 được với con số đã công bố (V34-R1 dùng 5 QP và không có ensemble/guard OD). Muốn xác nhận thống kê cần tái chạy protocol độc lập đầy đủ.
- Guard nguồn cho OD làm tăng chi phí phía sender (encode + đo thêm shortlist), đúng như đánh đổi đã có ở AR/OT.
- `calibrated` sau fix có thể vẫn bảo thủ với các action mạnh; mục tiêu là "sống dậy" và chọn được action nhẹ thay vì identity 100%.
