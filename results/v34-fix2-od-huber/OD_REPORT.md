# Báo Cáo Đánh Giá Object Detection (COCO 2017) Trên V34

**Tập dữ liệu:** COCO 2017 (256 ảnh TEST ngẫu nhiên, phân vùng hash cố định)
**Mô hình đánh giá:** Faster R-CNN ResNet-50 FPN (Torchvision official COCO_V1)
**Codec kiểm tra:** H.264 (x264) và H.265 (x265) | Preset: medium
**Các mức QP:** 30, 35, 40, 45

## 1. Bảng Tổng Hợp BD-Rate Trên COCO

| Codec | Nhánh (Arm) | BD-rate (%) | PCHIP BD-rate (%) | BD-quality (mAP pp) | Trạng thái |
|---|---|---:|---:|---:|---:|
| h264 | `calibrated_303401` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h264 | `calibrated_303402` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h264 | `calibrated_303403` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h264 | `calibrated_ensemble` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h264 | `fixed` | 2.43% | -5.13% | +20.73 | Không tiết kiệm |
| h264 | `forced_303401` | -5.26% | -12.57% | +88.14 | Tiết kiệm bitrate |
| h264 | `forced_303402` | -6.23% | -9.83% | +70.25 | Tiết kiệm bitrate |
| h264 | `forced_303403` | -4.82% | -10.57% | +71.57 | Tiết kiệm bitrate |
| h264 | `forced_ensemble` | -4.86% | -11.39% | +78.41 | Tiết kiệm bitrate |
| h264 | `forced_frozen_303401` | 2.43% | -5.13% | +20.73 | Không tiết kiệm |
| h264 | `selected_303401` | -4.65% | -15.95% | +98.93 | Tiết kiệm bitrate |
| h264 | `selected_303402` | -2.50% | -15.70% | +97.02 | Tiết kiệm bitrate |
| h264 | `selected_303403` | -5.20% | -15.86% | +96.95 | Tiết kiệm bitrate |
| h264 | `selected_ensemble` | -6.29% | -15.59% | +95.96 | Tiết kiệm bitrate |
| h265 | `calibrated_303401` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `calibrated_303402` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `calibrated_303403` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `calibrated_ensemble` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `fixed` | -4.77% | -0.25% | +3.28 | Tiết kiệm bitrate |
| h265 | `forced_303401` | -15.57% | -6.53% | +52.65 | Tiết kiệm bitrate |
| h265 | `forced_303402` | -13.45% | -6.25% | +51.39 | Tiết kiệm bitrate |
| h265 | `forced_303403` | -14.95% | -6.44% | +53.24 | Tiết kiệm bitrate |
| h265 | `forced_ensemble` | -15.33% | -6.64% | +53.53 | Tiết kiệm bitrate |
| h265 | `forced_frozen_303401` | -4.77% | -0.25% | +3.28 | Tiết kiệm bitrate |
| h265 | `selected_303401` | -7.21% | -13.31% | +112.47 | Tiết kiệm bitrate |
| h265 | `selected_303402` | -8.14% | -13.65% | +114.12 | Tiết kiệm bitrate |
| h265 | `selected_303403` | -7.14% | -13.43% | +113.31 | Tiết kiệm bitrate |
| h265 | `selected_ensemble` | -7.32% | -13.40% | +113.04 | Tiết kiệm bitrate |

## 2. Chi Tiết Rate (bpp) và mAP@[.50:.95] Theo Từng QP

### Codec: H264

| QP | Metric | Anchor | Fixed (Action 11) | selected_ensemble | Δ mAP (selected_ensemble) | Δ Rate % (selected_ensemble) |
|---:|---|---:|---:|---:|---:|---:|
| 30 | mAP@[.5:.95] | 0.2197 | 0.2085 | 0.2148 | -0.49 pp | -18.37% |
| 30 | Rate (bpp) | 0.7936 | 0.6730 | 0.6478 | - | - |
| 35 | mAP@[.5:.95] | 0.2052 | 0.2003 | 0.2071 | +0.19 pp | -16.97% |
| 35 | Rate (bpp) | 0.4829 | 0.4117 | 0.4009 | - | - |
| 40 | mAP@[.5:.95] | 0.1817 | 0.1774 | 0.1841 | +0.25 pp | -13.33% |
| 40 | Rate (bpp) | 0.2953 | 0.2588 | 0.2560 | - | - |
| 45 | mAP@[.5:.95] | 0.1381 | 0.1360 | 0.1402 | +0.22 pp | -8.93% |
| 45 | Rate (bpp) | 0.1834 | 0.1677 | 0.1670 | - | - |

### Codec: H265

| QP | Metric | Anchor | Fixed (Action 11) | selected_ensemble | Δ mAP (selected_ensemble) | Δ Rate % (selected_ensemble) |
|---:|---|---:|---:|---:|---:|---:|
| 30 | mAP@[.5:.95] | 0.2156 | 0.2118 | 0.2162 | +0.06 pp | -16.93% |
| 30 | Rate (bpp) | 0.8262 | 0.7130 | 0.6863 | - | - |
| 35 | mAP@[.5:.95] | 0.2077 | 0.2019 | 0.2100 | +0.23 pp | -13.85% |
| 35 | Rate (bpp) | 0.5624 | 0.4946 | 0.4845 | - | - |
| 40 | mAP@[.5:.95] | 0.1860 | 0.1774 | 0.1917 | +0.58 pp | -9.70% |
| 40 | Rate (bpp) | 0.3988 | 0.3634 | 0.3601 | - | - |
| 45 | mAP@[.5:.95] | 0.1397 | 0.1280 | 0.1451 | +0.54 pp | -5.47% |
| 45 | Rate (bpp) | 0.2990 | 0.2839 | 0.2827 | - | - |

## 3. Nhận Xét & Kết Luận
- **Hiệu quả nén OD:** Xem xét BD-rate âm thể hiện mức giảm bitrate ở cùng mAP.
- **Độ chính xác Faster R-CNN:** Bounding boxes được decode từ dòng video thực, giải mã ngược về tọa độ gốc và đánh giá qua `COCOeval` chính thức.
- **Hoàn toàn độc lập:** Quá trình huấn luyện controller chỉ dùng tập train/cal, không chạm vào nhãn ground-truth của tập DEV/TEST.