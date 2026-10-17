# Báo Cáo Đánh Giá Object Detection (COCO 2017) Trên V34

**Tập dữ liệu:** COCO 2017 (256 ảnh TEST ngẫu nhiên, phân vùng hash cố định)
**Mô hình đánh giá:** Faster R-CNN ResNet-50 FPN (Torchvision official COCO_V1)
**Codec kiểm tra:** H.264 (x264) và H.265 (x265) | Preset: medium
**Các mức QP:** 30, 35, 40, 45

## 1. Bảng Tổng Hợp BD-Rate Trên COCO

| Codec | Nhánh (Arm) | BD-rate (%) | PCHIP BD-rate (%) | BD-quality (mAP pp) | Trạng thái |
|---|---|---:|---:|---:|---:|
| h264 | `calibrated_303401` | -0.03% | -0.03% | +0.22 | Tiết kiệm bitrate |
| h264 | `calibrated_303402` | 0.16% | -0.07% | +0.60 | Không tiết kiệm |
| h264 | `calibrated_303403` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h264 | `calibrated_ensemble` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h264 | `fixed` | 2.43% | -5.13% | +20.73 | Không tiết kiệm |
| h264 | `forced_303401` | -2.25% | -11.82% | +81.15 | Tiết kiệm bitrate |
| h264 | `forced_303402` | -4.38% | -10.62% | +72.94 | Tiết kiệm bitrate |
| h264 | `forced_303403` | -7.09% | -10.01% | +70.84 | Tiết kiệm bitrate |
| h264 | `forced_ensemble` | -1.11% | -11.17% | +76.86 | Tiết kiệm bitrate |
| h264 | `forced_frozen_303401` | 2.43% | -5.13% | +20.73 | Không tiết kiệm |
| h264 | `selected_303401` | -1.36% | -15.77% | +98.14 | Tiết kiệm bitrate |
| h264 | `selected_303402` | -0.42% | -15.30% | +95.51 | Tiết kiệm bitrate |
| h264 | `selected_303403` | -5.82% | -15.68% | +97.04 | Tiết kiệm bitrate |
| h264 | `selected_ensemble` | -4.93% | -15.45% | +95.97 | Tiết kiệm bitrate |
| h265 | `calibrated_303401` | -0.38% | -0.18% | +1.44 | Tiết kiệm bitrate |
| h265 | `calibrated_303402` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `calibrated_303403` | -0.02% | -0.00% | +0.03 | Tiết kiệm bitrate |
| h265 | `calibrated_ensemble` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `fixed` | -4.77% | -0.25% | +3.28 | Tiết kiệm bitrate |
| h265 | `forced_303401` | -16.96% | -7.95% | +65.50 | Tiết kiệm bitrate |
| h265 | `forced_303402` | -19.73% | -4.22% | +26.67 | Tiết kiệm bitrate |
| h265 | `forced_303403` | -16.64% | -8.04% | +67.68 | Tiết kiệm bitrate |
| h265 | `forced_ensemble` | -23.19% | -6.64% | +47.80 | Tiết kiệm bitrate |
| h265 | `forced_frozen_303401` | -4.77% | -0.25% | +3.28 | Tiết kiệm bitrate |
| h265 | `selected_303401` | -2.54% | -12.59% | +110.42 | Tiết kiệm bitrate |
| h265 | `selected_303402` | -10.56% | -12.62% | +105.41 | Tiết kiệm bitrate |
| h265 | `selected_303403` | -1.61% | -13.34% | +114.64 | Tiết kiệm bitrate |
| h265 | `selected_ensemble` | -5.55% | -12.73% | +109.74 | Tiết kiệm bitrate |

## 2. Chi Tiết Rate (bpp) và mAP@[.50:.95] Theo Từng QP

### Codec: H264

| QP | Metric | Anchor | Fixed (Action 11) | selected_ensemble | Δ mAP (selected_ensemble) | Δ Rate % (selected_ensemble) |
|---:|---|---:|---:|---:|---:|---:|
| 30 | mAP@[.5:.95] | 0.2197 | 0.2085 | 0.2148 | -0.49 pp | -18.37% |
| 30 | Rate (bpp) | 0.7936 | 0.6730 | 0.6478 | - | - |
| 35 | mAP@[.5:.95] | 0.2052 | 0.2003 | 0.2074 | +0.22 pp | -16.97% |
| 35 | Rate (bpp) | 0.4829 | 0.4117 | 0.4009 | - | - |
| 40 | mAP@[.5:.95] | 0.1817 | 0.1774 | 0.1840 | +0.23 pp | -13.25% |
| 40 | Rate (bpp) | 0.2953 | 0.2588 | 0.2562 | - | - |
| 45 | mAP@[.5:.95] | 0.1381 | 0.1360 | 0.1396 | +0.15 pp | -8.92% |
| 45 | Rate (bpp) | 0.1834 | 0.1677 | 0.1670 | - | - |

### Codec: H265

| QP | Metric | Anchor | Fixed (Action 11) | selected_ensemble | Δ mAP (selected_ensemble) | Δ Rate % (selected_ensemble) |
|---:|---|---:|---:|---:|---:|---:|
| 30 | mAP@[.5:.95] | 0.2156 | 0.2118 | 0.2162 | +0.06 pp | -16.93% |
| 30 | Rate (bpp) | 0.8262 | 0.7130 | 0.6863 | - | - |
| 35 | mAP@[.5:.95] | 0.2077 | 0.2019 | 0.2101 | +0.24 pp | -13.85% |
| 35 | Rate (bpp) | 0.5624 | 0.4946 | 0.4845 | - | - |
| 40 | mAP@[.5:.95] | 0.1860 | 0.1774 | 0.1907 | +0.47 pp | -9.76% |
| 40 | Rate (bpp) | 0.3988 | 0.3634 | 0.3599 | - | - |
| 45 | mAP@[.5:.95] | 0.1397 | 0.1280 | 0.1432 | +0.35 pp | -5.40% |
| 45 | Rate (bpp) | 0.2990 | 0.2839 | 0.2829 | - | - |

## 3. Nhận Xét & Kết Luận
- **Hiệu quả nén OD:** Xem xét BD-rate âm thể hiện mức giảm bitrate ở cùng mAP.
- **Độ chính xác Faster R-CNN:** Bounding boxes được decode từ dòng video thực, giải mã ngược về tọa độ gốc và đánh giá qua `COCOeval` chính thức.
- **Hoàn toàn độc lập:** Quá trình huấn luyện controller chỉ dùng tập train/cal, không chạm vào nhãn ground-truth của tập DEV/TEST.