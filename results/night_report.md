# Báo cáo đêm V34-Fix2 (tự động)

Bắt đầu: 2026-10-17 10:03 (giờ máy)

Chuỗi: fix1 OD (đang chạy) → cache đo đạc → 3 biến thể Fix2 OD (rank/huber/forced) → AR+OD scaled pilot → báo cáo này.
Log thô: `C:\Users\Wagur1\AppData\Local\Temp\opencode\ap_analysis\autopilot_v34.log`
[10:03:13] === Autopilot V34-Fix2 bắt đầu ===

## 1. Kernel fix1 OD (nguồn cache)

Cache fix1 đã có trong git; bỏ qua tải output fix1.
[10:03:13] HEAD để chạy biến thể: d97affd6691037ce182445b806111ae48454439a

## 2. Phân tích fix1 OD

```
=== BD-rate test (qps=[30, 35, 40, 45], n=256) ===

-- H264 --
         selected_303401  BD=   -6.08%  PCHIP=  -16.16%  dQ=+99.15pp
         selected_303403  BD=   -3.90%  PCHIP=  -16.64%  dQ=+102.10pp
       selected_ensemble  BD=   -2.91%  PCHIP=  -16.79%  dQ=+106.53pp
         selected_303402  BD=   -1.16%  PCHIP=  -16.02%  dQ=+99.69pp
       calibrated_303402  BD=   -0.37%  PCHIP=   -0.11%  dQ= +0.64pp
       calibrated_303403  BD=   -0.09%  PCHIP=   -0.31%  dQ= +1.91pp
     calibrated_ensemble  BD=   -0.04%  PCHIP=   -0.01%  dQ= +0.08pp
       calibrated_303401  BD=   +0.04%  PCHIP=   +0.04%  dQ= -0.21pp
                   fixed  BD=   +2.43%  PCHIP=   -5.13%  dQ=+20.73pp
    forced_frozen_303401  BD=   +2.43%  PCHIP=   -5.13%  dQ=+20.73pp
         forced_ensemble  BD=   +3.91%  PCHIP=  -11.98%  dQ=+77.15pp
           forced_303403  BD=   +4.18%  PCHIP=  -12.13%  dQ=+79.87pp
           forced_303402  BD=   +9.26%  PCHIP=  -12.11%  dQ=+79.28pp
           forced_303401  BD=  +17.87%  PCHIP=  -13.32%  dQ=+85.00pp

-- H265 --
           forced_303401  BD=  -32.16%  PCHIP=   -5.86%  dQ=+38.57pp
         forced_ensemble  BD=  -20.59%  PCHIP=   -4.92%  dQ=+33.99pp
           forced_303402  BD=  -20.00%  PCHIP=   -4.75%  dQ=+32.44pp
           forced_303403  BD=  -18.92%  PCHIP=   -5.93%  dQ=+43.89pp
       selected_ensemble  BD=   -9.36%  PCHIP=  -12.89%  dQ=+109.21pp
         selected_303401  BD=   -8.57%  PCHIP=  -11.71%  dQ=+103.96pp
         selected_303402  BD=   -8.06%  PCHIP=  -12.86%  dQ=+107.42pp
                   fixed  BD=   -4.77%  PCHIP=   -0.25%  dQ= +3.28pp
    forced_frozen_303401  BD=   -4.77%  PCHIP=   -0.25%  dQ= +3.28pp
       calibrated_303403  BD=   -0.42%  PCHIP=   -0.01%  dQ= +0.10pp
       calibrated_303402  BD=   -0.27%  PCHIP=   +0.03%  dQ= -0.21pp
       calibrated_303401  BD=   -0.07%  PCHIP=   -0.00%  dQ= +0.05pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
         selected_303403  BD=   +6.75%  PCHIP=  -13.19%  dQ=+110.54pp

=== Arm behavior on test rows ===
                  anchor  identity=100.0%  a0:2048
       calibrated_303401  identity= 99.5%  a0:2038, a2:4, a11:2, a6:2
       calibrated_303402  identity= 99.1%  a0:2029, a1:6, a10:5, a8:3
       calibrated_303403  identity= 98.6%  a0:2020, a12:10, a4:6, a10:3
     calibrated_ensemble  identity= 99.8%  a0:2044, a8:3, a1:1
                   fixed  identity=  0.0%  a11:2048
           forced_303401  identity=  0.9%  a6:983, a11:696, a4:341, a0:18  calibrated_nonidentity=  0.5%
           forced_303402  identity=  0.9%  a6:963, a11:673, a4:364, a0:18  calibrated_nonidentity=  0.9%
           forced_303403  identity=  0.4%  a11:850, a6:828, a4:343, a2:18  calibrated_nonidentity=  1.4%
         forced_ensemble  identity=  0.8%  a6:946, a11:722, a4:350, a0:17  calibrated_nonidentity=  0.2%
    forced_frozen_303401  identity=  0.0%  a11:2048
         selected_303401  identity=  4.1%  a11:723, a6:632, a4:392, a0:83  calibrated_nonidentity=  0.5%
         selected_303402  identity=  4.0%  a11:697, a6:646, a4:419, a5:91  calibrated_nonidentity=  0.9%
         selected_303403  identity=  3.7%  a11:705, a6:642, a4:353, a5:106  calibrated_nonidentity=  1.4%
       selected_ensemble  identity=  4.0%  a11:712, a6:653, a4:384, a5:86  calibrated_nonidentity=  0.2%

measurements.json sha256 = 9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7

=== Checkpoint calibration (bound vs tolerance) ===
training_303401.json: seed=303401 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 8, 10, 11, 12] bound_range=[0.0000..0.0904]
training_303402.json: seed=303402 tolerance_od=0.05 feasible_actions=[0, 12] bound_range=[0.0000..0.1817]
training_303403.json: seed=303403 tolerance_od=0.05 feasible_actions=[0, 1, 2, 6, 10, 11, 12] bound_range=[0.0000..0.1456]
```
measurements sha256: `9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7`
dev: test | count test: 256

## 3. Biến thể Fix2 OD


## 4. AR+OD scaled pilot


## 5. Theo dõi + tải + phân tích

[10:03:48] v34-fix2-od-rank: COMPLETE (tranthihongdieu)
### v34-fix2-od-rank

```
=== BD-rate test (qps=[30, 35, 40, 45], n=256) ===

-- H264 --
           forced_303403  BD=   -7.09%  PCHIP=  -10.01%  dQ= +0.71pp
         selected_303403  BD=   -5.82%  PCHIP=  -15.68%  dQ= +0.97pp
       selected_ensemble  BD=   -4.93%  PCHIP=  -15.45%  dQ= +0.96pp
           forced_303402  BD=   -4.38%  PCHIP=  -10.62%  dQ= +0.73pp
           forced_303401  BD=   -2.25%  PCHIP=  -11.82%  dQ= +0.81pp
         selected_303401  BD=   -1.36%  PCHIP=  -15.77%  dQ= +0.98pp
         forced_ensemble  BD=   -1.11%  PCHIP=  -11.17%  dQ= +0.77pp
         selected_303402  BD=   -0.42%  PCHIP=  -15.30%  dQ= +0.96pp
       calibrated_303401  BD=   -0.03%  PCHIP=   -0.03%  dQ= +0.00pp
       calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
       calibrated_303402  BD=   +0.16%  PCHIP=   -0.07%  dQ= +0.01pp
                   fixed  BD=   +2.43%  PCHIP=   -5.13%  dQ= +0.21pp
    forced_frozen_303401  BD=   +2.43%  PCHIP=   -5.13%  dQ= +0.21pp

-- H265 --
         forced_ensemble  BD=  -23.19%  PCHIP=   -6.64%  dQ= +0.48pp
           forced_303402  BD=  -19.73%  PCHIP=   -4.22%  dQ= +0.27pp
           forced_303401  BD=  -16.96%  PCHIP=   -7.95%  dQ= +0.66pp
           forced_303403  BD=  -16.64%  PCHIP=   -8.04%  dQ= +0.68pp
         selected_303402  BD=  -10.56%  PCHIP=  -12.62%  dQ= +1.05pp
       selected_ensemble  BD=   -5.55%  PCHIP=  -12.73%  dQ= +1.10pp
                   fixed  BD=   -4.77%  PCHIP=   -0.25%  dQ= +0.03pp
    forced_frozen_303401  BD=   -4.77%  PCHIP=   -0.25%  dQ= +0.03pp
         selected_303401  BD=   -2.54%  PCHIP=  -12.59%  dQ= +1.10pp
         selected_303403  BD=   -1.61%  PCHIP=  -13.34%  dQ= +1.15pp
       calibrated_303401  BD=   -0.38%  PCHIP=   -0.18%  dQ= +0.01pp
       calibrated_303403  BD=   -0.02%  PCHIP=   -0.00%  dQ= +0.00pp
       calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp

measurements.json sha256 = 9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7

=== Checkpoint calibration (bound vs tolerance) ===
training_303401.json: seed=303401 tolerance_od=0.05 feasible_actions=[0, 1, 2, 4, 5, 7, 9, 10, 11, 12] bound_range=[0.0000..0.0803]
training_303402.json: seed=303402 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 7, 9, 10, 11, 12] bound_range=[0.0000..0.0814]
training_303403.json: seed=303403 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12] bound_range=[0.0000..0.0684]
```
[10:08:13] v34-fix2-od-huber: COMPLETE (hieusunday0412)
### v34-fix2-od-huber

```
=== BD-rate test (qps=[30, 35, 40, 45], n=256) ===

-- H264 --
       selected_ensemble  BD=   -6.29%  PCHIP=  -15.59%  dQ= +0.96pp
           forced_303402  BD=   -6.23%  PCHIP=   -9.83%  dQ= +0.70pp
           forced_303401  BD=   -5.26%  PCHIP=  -12.57%  dQ= +0.88pp
         selected_303403  BD=   -5.20%  PCHIP=  -15.86%  dQ= +0.97pp
         forced_ensemble  BD=   -4.86%  PCHIP=  -11.39%  dQ= +0.78pp
           forced_303403  BD=   -4.82%  PCHIP=  -10.57%  dQ= +0.72pp
         selected_303401  BD=   -4.65%  PCHIP=  -15.95%  dQ= +0.99pp
         selected_303402  BD=   -2.50%  PCHIP=  -15.70%  dQ= +0.97pp
       calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
       calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
       calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
                   fixed  BD=   +2.43%  PCHIP=   -5.13%  dQ= +0.21pp
    forced_frozen_303401  BD=   +2.43%  PCHIP=   -5.13%  dQ= +0.21pp

-- H265 --
           forced_303401  BD=  -15.57%  PCHIP=   -6.53%  dQ= +0.53pp
         forced_ensemble  BD=  -15.33%  PCHIP=   -6.64%  dQ= +0.54pp
           forced_303403  BD=  -14.95%  PCHIP=   -6.44%  dQ= +0.53pp
           forced_303402  BD=  -13.45%  PCHIP=   -6.25%  dQ= +0.51pp
         selected_303402  BD=   -8.14%  PCHIP=  -13.65%  dQ= +1.14pp
       selected_ensemble  BD=   -7.32%  PCHIP=  -13.40%  dQ= +1.13pp
         selected_303401  BD=   -7.21%  PCHIP=  -13.31%  dQ= +1.12pp
         selected_303403  BD=   -7.14%  PCHIP=  -13.43%  dQ= +1.13pp
                   fixed  BD=   -4.77%  PCHIP=   -0.25%  dQ= +0.03pp
    forced_frozen_303401  BD=   -4.77%  PCHIP=   -0.25%  dQ= +0.03pp
       calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
       calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
       calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp

measurements.json sha256 = 9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7

=== Checkpoint calibration (bound vs tolerance) ===
training_303401.json: seed=303401 tolerance_od=0.05 feasible_actions=[0] bound_range=[0.0000..0.3226]
training_303402.json: seed=303402 tolerance_od=0.05 feasible_actions=[0] bound_range=[0.0000..0.3174]
training_303403.json: seed=303403 tolerance_od=0.05 feasible_actions=[0] bound_range=[0.0000..0.3141]
```
[10:13:17] v34-fix2-od-forced: COMPLETE (nguyenhoanglan1232)
### v34-fix2-od-forced

```
=== BD-rate test (qps=[30, 35, 40, 45], n=256) ===

-- H264 --
           forced_303403  BD=   -7.09%  PCHIP=  -10.01%  dQ= +0.71pp
         selected_303403  BD=   -5.82%  PCHIP=  -15.68%  dQ= +0.97pp
           forced_303402  BD=   -4.38%  PCHIP=  -10.62%  dQ= +0.73pp
       selected_ensemble  BD=   -4.30%  PCHIP=  -15.27%  dQ= +0.95pp
         selected_303402  BD=   -2.45%  PCHIP=  -15.33%  dQ= +0.96pp
           forced_303401  BD=   -2.25%  PCHIP=  -11.82%  dQ= +0.81pp
         selected_303401  BD=   -1.38%  PCHIP=  -15.79%  dQ= +0.98pp
         forced_ensemble  BD=   -1.11%  PCHIP=  -11.17%  dQ= +0.77pp
       calibrated_303401  BD=   -0.03%  PCHIP=   -0.03%  dQ= +0.00pp
       calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
       calibrated_303402  BD=   +0.16%  PCHIP=   -0.07%  dQ= +0.01pp
                   fixed  BD=   +2.43%  PCHIP=   -5.13%  dQ= +0.21pp
    forced_frozen_303401  BD=   +2.43%  PCHIP=   -5.13%  dQ= +0.21pp

-- H265 --
         forced_ensemble  BD=  -23.19%  PCHIP=   -6.64%  dQ= +0.48pp
           forced_303402  BD=  -19.73%  PCHIP=   -4.22%  dQ= +0.27pp
           forced_303401  BD=  -16.96%  PCHIP=   -7.95%  dQ= +0.66pp
           forced_303403  BD=  -16.64%  PCHIP=   -8.04%  dQ= +0.68pp
         selected_303402  BD=  -10.63%  PCHIP=  -12.82%  dQ= +1.07pp
       selected_ensemble  BD=   -5.50%  PCHIP=  -12.73%  dQ= +1.10pp
                   fixed  BD=   -4.77%  PCHIP=   -0.25%  dQ= +0.03pp
    forced_frozen_303401  BD=   -4.77%  PCHIP=   -0.25%  dQ= +0.03pp
         selected_303401  BD=   -2.54%  PCHIP=  -12.59%  dQ= +1.10pp
         selected_303403  BD=   -2.05%  PCHIP=  -13.41%  dQ= +1.15pp
       calibrated_303401  BD=   -0.38%  PCHIP=   -0.18%  dQ= +0.01pp
       calibrated_303403  BD=   -0.02%  PCHIP=   -0.00%  dQ= +0.00pp
       calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
     calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp

measurements.json sha256 = 9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7

=== Checkpoint calibration (bound vs tolerance) ===
training_303401.json: seed=303401 tolerance_od=0.05 feasible_actions=[0, 1, 2, 4, 5, 7, 9, 10, 11, 12] bound_range=[0.0000..0.0803]
training_303402.json: seed=303402 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 7, 9, 10, 11, 12] bound_range=[0.0000..0.0801]
training_303403.json: seed=303403 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12] bound_range=[0.0000..0.0684]
```
[10:17:57] v34-fix2-ar-od-scaled: RUNNING (dngbolm)
[14:49:39] v34-fix2-ar-od-scaled: COMPLETE (dngbolm)
### v34-fix2-ar-od-scaled

```
=== BD-rate test (qps=None, n=None) ===

-- AR/H264 --
                swin3d_t  BD=      N/A  PCHIP=      N/A  dQ=     N/A
                  r3d_18  BD=      N/A  PCHIP=      N/A  dQ=     N/A

-- AR/H265 --
                swin3d_t  BD=      N/A  PCHIP=      N/A  dQ=     N/A
                  r3d_18  BD=      N/A  PCHIP=      N/A  dQ=     N/A

-- OD/H264 --
                resnet50  BD=      N/A  PCHIP=      N/A  dQ=     N/A

-- OD/H265 --
                resnet50  BD=      N/A  PCHIP=      N/A  dQ=     N/A

measurements.json sha256 = d5fceedc3bfd75792201b18577dcb1aa672abfa9466c835945ed80f87b9f9d09

=== Checkpoint calibration (bound vs tolerance) ===
training_303401.json: seed=303401 tolerance_od=0.05 feasible_actions=[0, 1, 2, 5, 6, 9, 10, 11, 12] bound_range=[0.0000..0.1264]
training_303402.json: seed=303402 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12] bound_range=[0.0000..0.0736]
training_303403.json: seed=303403 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12] bound_range=[0.0000..0.1378]
```

## 6. Tổng hợp BD-rate (các arm chính)

| Run | Codec | arm | BD-rate | PCHIP |
|---|---|---|---:|---:|
| v34-fix1-od-coco | - | (no test_summary) | - | - |
| v34-fix2-od-rank | h264 | `selected_303401` | -1.36% | -15.77% |
| v34-fix2-od-rank | h264 | `selected_ensemble` | -4.93% | -15.45% |
| v34-fix2-od-rank | h264 | `calibrated_303401` | -0.03% | -0.03% |
| v34-fix2-od-rank | h264 | `calibrated_ensemble` | +0.00% | +0.00% |
| v34-fix2-od-rank | h264 | `forced_303401` | -2.25% | -11.82% |
| v34-fix2-od-rank | h264 | `fixed` | +2.43% | -5.13% |
| v34-fix2-od-rank | h265 | `selected_303401` | -2.54% | -12.59% |
| v34-fix2-od-rank | h265 | `selected_ensemble` | -5.55% | -12.73% |
| v34-fix2-od-rank | h265 | `calibrated_303401` | -0.38% | -0.18% |
| v34-fix2-od-rank | h265 | `calibrated_ensemble` | +0.00% | +0.00% |
| v34-fix2-od-rank | h265 | `forced_303401` | -16.96% | -7.95% |
| v34-fix2-od-rank | h265 | `fixed` | -4.77% | -0.25% |
| v34-fix2-od-huber | h264 | `selected_303401` | -4.65% | -15.95% |
| v34-fix2-od-huber | h264 | `selected_ensemble` | -6.29% | -15.59% |
| v34-fix2-od-huber | h264 | `calibrated_303401` | +0.00% | +0.00% |
| v34-fix2-od-huber | h264 | `calibrated_ensemble` | +0.00% | +0.00% |
| v34-fix2-od-huber | h264 | `forced_303401` | -5.26% | -12.57% |
| v34-fix2-od-huber | h264 | `fixed` | +2.43% | -5.13% |
| v34-fix2-od-huber | h265 | `selected_303401` | -7.21% | -13.31% |
| v34-fix2-od-huber | h265 | `selected_ensemble` | -7.32% | -13.40% |
| v34-fix2-od-huber | h265 | `calibrated_303401` | +0.00% | +0.00% |
| v34-fix2-od-huber | h265 | `calibrated_ensemble` | +0.00% | +0.00% |
| v34-fix2-od-huber | h265 | `forced_303401` | -15.57% | -6.53% |
| v34-fix2-od-huber | h265 | `fixed` | -4.77% | -0.25% |
| v34-fix2-od-forced | h264 | `selected_303401` | -1.38% | -15.79% |
| v34-fix2-od-forced | h264 | `selected_ensemble` | -4.30% | -15.27% |
| v34-fix2-od-forced | h264 | `calibrated_303401` | -0.03% | -0.03% |
| v34-fix2-od-forced | h264 | `calibrated_ensemble` | +0.00% | +0.00% |
| v34-fix2-od-forced | h264 | `forced_303401` | -2.25% | -11.82% |
| v34-fix2-od-forced | h264 | `fixed` | +2.43% | -5.13% |
| v34-fix2-od-forced | h265 | `selected_303401` | -2.54% | -12.59% |
| v34-fix2-od-forced | h265 | `selected_ensemble` | -5.50% | -12.73% |
| v34-fix2-od-forced | h265 | `calibrated_303401` | -0.38% | -0.18% |
| v34-fix2-od-forced | h265 | `calibrated_ensemble` | +0.00% | +0.00% |
| v34-fix2-od-forced | h265 | `forced_303401` | -16.96% | -7.95% |
| v34-fix2-od-forced | h265 | `fixed` | -4.77% | -0.25% |

cache sha256 = `9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7` — mọi biến thể tái sử dụng cùng cache này (đối chiếu `measurements.json sha256` trong log từng biến thể).

## 7. Trạng thái kernel cuối

- `wagur124705/v34-fix1-od-coco`: **UNKNOWN**  https://www.kaggle.com/code/wagur124705/v34-fix1-od-coco
- `tranthihongdieu/v34-fix2-od-rank`: **COMPLETE**  https://www.kaggle.com/code/tranthihongdieu/v34-fix2-od-rank
- `hieusunday0412/v34-fix2-od-huber`: **COMPLETE**  https://www.kaggle.com/code/hieusunday0412/v34-fix2-od-huber
- `nguyenhoanglan1232/v34-fix2-od-forced`: **COMPLETE**  https://www.kaggle.com/code/nguyenhoanglan1232/v34-fix2-od-forced
- `dngbolm/v34-fix2-ar-od-scaled`: **COMPLETE**  https://www.kaggle.com/code/dngbolm/v34-fix2-ar-od-scaled
