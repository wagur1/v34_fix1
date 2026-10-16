# Báo Cáo Đánh Giá Object Detection (COCO 2017) Trên V34

**Tập dữ liệu:** COCO 2017 (256 ảnh TEST ngẫu nhiên, phân vùng hash cố định)
**Mô hình đánh giá:** Faster R-CNN ResNet-50 FPN (Torchvision official COCO_V1)
**Codec kiểm tra:** H.264 (x264) và H.265 (x265) | Preset: medium
**Các mức QP:** 30, 35, 40, 45

## 1. Bảng Tổng Hợp BD-Rate Trên COCO

| Codec | Nhánh (Arm) | BD-rate (%) | PCHIP BD-rate (%) | BD-quality (mAP pp) | Trạng thái |
|---|---|---:|---:|---:|---:|
| h264 | `calibrated_303401` | 0.04% | 0.04% | -0.21 | Không tiết kiệm |
| h264 | `calibrated_303402` | -0.37% | -0.11% | +0.64 | Tiết kiệm bitrate |
| h264 | `calibrated_303403` | -0.09% | -0.31% | +1.91 | Tiết kiệm bitrate |
| h264 | `calibrated_ensemble` | -0.04% | -0.01% | +0.08 | Tiết kiệm bitrate |
| h264 | `fixed` | 2.43% | -5.13% | +20.73 | Không tiết kiệm |
| h264 | `forced_303401` | 17.87% | -13.32% | +85.00 | Không tiết kiệm |
| h264 | `forced_303402` | 9.26% | -12.11% | +79.28 | Không tiết kiệm |
| h264 | `forced_303403` | 4.18% | -12.13% | +79.87 | Không tiết kiệm |
| h264 | `forced_ensemble` | 3.91% | -11.98% | +77.15 | Không tiết kiệm |
| h264 | `forced_frozen_303401` | 2.43% | -5.13% | +20.73 | Không tiết kiệm |
| h264 | `selected_303401` | -6.08% | -16.16% | +99.15 | Tiết kiệm bitrate |
| h264 | `selected_303402` | -1.16% | -16.02% | +99.69 | Tiết kiệm bitrate |
| h264 | `selected_303403` | -3.90% | -16.64% | +102.10 | Tiết kiệm bitrate |
| h264 | `selected_ensemble` | -2.91% | -16.79% | +106.53 | Tiết kiệm bitrate |
| h265 | `calibrated_303401` | -0.07% | -0.00% | +0.05 | Tiết kiệm bitrate |
| h265 | `calibrated_303402` | -0.27% | 0.03% | -0.21 | Tiết kiệm bitrate |
| h265 | `calibrated_303403` | -0.42% | -0.01% | +0.10 | Tiết kiệm bitrate |
| h265 | `calibrated_ensemble` | 0.00% | 0.00% | +0.00 | Không tiết kiệm |
| h265 | `fixed` | -4.77% | -0.25% | +3.28 | Tiết kiệm bitrate |
| h265 | `forced_303401` | -32.16% | -5.86% | +38.57 | Tiết kiệm bitrate |
| h265 | `forced_303402` | -20.00% | -4.75% | +32.44 | Tiết kiệm bitrate |
| h265 | `forced_303403` | -18.92% | -5.93% | +43.89 | Tiết kiệm bitrate |
| h265 | `forced_ensemble` | -20.59% | -4.92% | +33.99 | Tiết kiệm bitrate |
| h265 | `forced_frozen_303401` | -4.77% | -0.25% | +3.28 | Tiết kiệm bitrate |
| h265 | `selected_303401` | -8.57% | -11.71% | +103.96 | Tiết kiệm bitrate |
| h265 | `selected_303402` | -8.06% | -12.86% | +107.42 | Tiết kiệm bitrate |
| h265 | `selected_303403` | 6.75% | -13.19% | +110.54 | Không tiết kiệm |
| h265 | `selected_ensemble` | -9.36% | -12.89% | +109.21 | Tiết kiệm bitrate |

## 2. Chi Tiết Rate (bpp) và mAP@[.50:.95] Theo Từng QP

### Codec: H264

| QP | Metric | Anchor | Fixed (Action 11) | selected_ensemble | Δ mAP (selected_ensemble) | Δ Rate % (selected_ensemble) |
|---:|---|---:|---:|---:|---:|---:|
| 30 | mAP@[.5:.95] | 0.2197 | 0.2085 | 0.2151 | -0.46 pp | -18.32% |
| 30 | Rate (bpp) | 0.7936 | 0.6730 | 0.6482 | - | - |
| 35 | mAP@[.5:.95] | 0.2052 | 0.2003 | 0.2099 | +0.46 pp | -16.96% |
| 35 | Rate (bpp) | 0.4829 | 0.4117 | 0.4010 | - | - |
| 40 | mAP@[.5:.95] | 0.1817 | 0.1774 | 0.1833 | +0.16 pp | -13.21% |
| 40 | Rate (bpp) | 0.2953 | 0.2588 | 0.2563 | - | - |
| 45 | mAP@[.5:.95] | 0.1381 | 0.1360 | 0.1423 | +0.43 pp | -8.87% |
| 45 | Rate (bpp) | 0.1834 | 0.1677 | 0.1671 | - | - |

### Codec: H265

| QP | Metric | Anchor | Fixed (Action 11) | selected_ensemble | Δ mAP (selected_ensemble) | Δ Rate % (selected_ensemble) |
|---:|---|---:|---:|---:|---:|---:|
| 30 | mAP@[.5:.95] | 0.2156 | 0.2118 | 0.2163 | +0.06 pp | -16.89% |
| 30 | Rate (bpp) | 0.8262 | 0.7130 | 0.6867 | - | - |
| 35 | mAP@[.5:.95] | 0.2077 | 0.2019 | 0.2092 | +0.15 pp | -13.81% |
| 35 | Rate (bpp) | 0.5624 | 0.4946 | 0.4847 | - | - |
| 40 | mAP@[.5:.95] | 0.1860 | 0.1774 | 0.1925 | +0.66 pp | -9.64% |
| 40 | Rate (bpp) | 0.3988 | 0.3634 | 0.3603 | - | - |
| 45 | mAP@[.5:.95] | 0.1397 | 0.1280 | 0.1429 | +0.32 pp | -5.31% |
| 45 | Rate (bpp) | 0.2990 | 0.2839 | 0.2832 | - | - |

## 3. Nhận Xét & Kết Luận
- **Hiệu quả nén OD:** Xem xét BD-rate âm thể hiện mức giảm bitrate ở cùng mAP.
- **Độ chính xác Faster R-CNN:** Bounding boxes được decode từ dòng video thực, giải mã ngược về tọa độ gốc và đánh giá qua `COCOeval` chính thức.
- **Hoàn toàn độc lập:** Quá trình huấn luyện controller chỉ dùng tập train/cal, không chạm vào nhãn ground-truth của tập DEV/TEST.