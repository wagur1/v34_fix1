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

> Ghi chú đính chính: cột dQ ở bảng trên in ×100 (lỗi hiển thị cũ — đã sửa code, commit `3890709`); giá trị thật = số hiển thị ÷ 100. Ví dụ `selected_303401` H264: **+0.99pp mAP** (thay vì +99.15). Các mục sau đã in đúng đơn vị.

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
=== BD-rate test (đã đính chính: cấu trúc lồng theo model; qps=[30, 35, 40, 45]) ===

-- AR/H264 --
          swin3d_t/selected_303401  BD=  -30.38%  PCHIP=  -24.13%  dQ= +6.94pp
          swin3d_t/selected_303403  BD=  -24.58%  PCHIP=  -23.22%  dQ= +6.68pp
        swin3d_t/selected_ensemble  BD=  -23.83%  PCHIP=  -21.86%  dQ= +6.08pp
          swin3d_t/selected_303402  BD=  -20.78%  PCHIP=  -21.42%  dQ= +6.01pp
              r3d_18/forced_303401  BD=   -6.49%  PCHIP=   +4.03%  dQ= -1.58pp
                    swin3d_t/fixed  BD=   -2.16%  PCHIP=   -2.39%  dQ= +0.66pp
        swin3d_t/calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        swin3d_t/calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        swin3d_t/calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
      swin3d_t/calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
          r3d_18/calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
          r3d_18/calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
          r3d_18/calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        r3d_18/calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
            r3d_18/selected_303401  BD=   +0.24%  PCHIP=   +1.26%  dQ= -0.38pp
            r3d_18/selected_303403  BD=   +0.40%  PCHIP=   -1.44%  dQ= +0.36pp
          r3d_18/selected_ensemble  BD=   +1.66%  PCHIP=   -0.05%  dQ= -0.20pp
              r3d_18/forced_303403  BD=   +2.08%  PCHIP=   +6.67%  dQ= -1.87pp
            r3d_18/forced_ensemble  BD=   +3.86%  PCHIP=   +6.83%  dQ= -1.97pp
            swin3d_t/forced_303401  BD=   +4.09%  PCHIP=   +4.10%  dQ= -1.26pp
            swin3d_t/forced_303403  BD=   +4.12%  PCHIP=   +4.09%  dQ= -1.29pp
            r3d_18/selected_303402  BD=   +4.28%  PCHIP=   +2.51%  dQ= -0.84pp
          swin3d_t/forced_ensemble  BD=   +5.09%  PCHIP=   +4.83%  dQ= -1.55pp
            swin3d_t/forced_303402  BD=   +5.33%  PCHIP=   +5.08%  dQ= -1.61pp
              r3d_18/forced_303402  BD=   +5.67%  PCHIP=   +6.60%  dQ= -2.32pp
                      r3d_18/fixed  BD=  +11.66%  PCHIP=  +14.52%  dQ= -4.47pp

-- AR/H265 --
          swin3d_t/selected_303403  BD=  -12.16%  PCHIP=  -14.51%  dQ= +6.31pp
          swin3d_t/selected_303402  BD=  -11.84%  PCHIP=  -12.76%  dQ= +5.50pp
        swin3d_t/selected_ensemble  BD=  -11.65%  PCHIP=  -12.56%  dQ= +5.40pp
          swin3d_t/selected_303401  BD=  -10.17%  PCHIP=  -13.29%  dQ= +5.59pp
                    swin3d_t/fixed  BD=   -6.02%  PCHIP=   -5.51%  dQ= +2.54pp
            swin3d_t/forced_303401  BD=   -2.67%  PCHIP=   -2.17%  dQ= +1.14pp
          swin3d_t/forced_ensemble  BD=   -1.61%  PCHIP=   -1.48%  dQ= +0.55pp
            swin3d_t/forced_303403  BD=   -1.22%  PCHIP=   -1.40%  dQ= +0.44pp
            swin3d_t/forced_303402  BD=   -0.87%  PCHIP=   -1.31%  dQ= +0.24pp
        swin3d_t/calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        swin3d_t/calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        swin3d_t/calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
      swin3d_t/calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
          r3d_18/calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
          r3d_18/calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
          r3d_18/calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        r3d_18/calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
            r3d_18/forced_ensemble  BD=   +0.41%  PCHIP=   +0.83%  dQ= -0.49pp
              r3d_18/forced_303402  BD=   +0.45%  PCHIP=   -1.31%  dQ= +0.39pp
              r3d_18/forced_303403  BD=   +3.24%  PCHIP=   +1.02%  dQ= -0.55pp
            r3d_18/selected_303403  BD=   +3.78%  PCHIP=   +5.40%  dQ= -2.15pp
            r3d_18/selected_303401  BD=   +4.19%  PCHIP=   +3.58%  dQ= -1.12pp
          r3d_18/selected_ensemble  BD=   +5.48%  PCHIP=   +2.83%  dQ= -1.09pp
            r3d_18/selected_303402  BD=   +6.34%  PCHIP=   +3.64%  dQ= -1.27pp
              r3d_18/forced_303401  BD=  +11.23%  PCHIP=  +10.51%  dQ= -3.39pp
                      r3d_18/fixed  BD=  +15.31%  PCHIP=  +14.40%  dQ= -4.41pp

-- OD/H264 --
          resnet50/selected_303402  BD=   -8.03%  PCHIP=   -7.99%  dQ= +1.20pp
            resnet50/forced_303401  BD=   -7.79%  PCHIP=   -7.90%  dQ= +1.20pp
          resnet50/selected_303403  BD=   -6.76%  PCHIP=   -6.74%  dQ= +1.02pp
          resnet50/selected_303401  BD=   -6.68%  PCHIP=   -6.64%  dQ= +0.99pp
        resnet50/selected_ensemble  BD=   -6.64%  PCHIP=   -6.51%  dQ= +0.96pp
            resnet50/forced_303403  BD=   -4.67%  PCHIP=   -4.58%  dQ= +0.72pp
          resnet50/forced_ensemble  BD=   -4.51%  PCHIP=   -4.44%  dQ= +0.69pp
            resnet50/forced_303402  BD=   -3.65%  PCHIP=   -3.53%  dQ= +0.56pp
                    resnet50/fixed  BD=   -1.65%  PCHIP=   -1.26%  dQ= +0.11pp
        resnet50/calibrated_303403  BD=   -0.08%  PCHIP=   -0.05%  dQ= +0.01pp
        resnet50/calibrated_303401  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        resnet50/calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
      resnet50/calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp

-- OD/H265 --
            resnet50/forced_303402  BD=   -9.90%  PCHIP=   -9.12%  dQ= +1.70pp
        resnet50/selected_ensemble  BD=   -9.36%  PCHIP=   -9.12%  dQ= +1.80pp
            resnet50/forced_303403  BD=   -9.04%  PCHIP=   -8.83%  dQ= +1.71pp
          resnet50/selected_303401  BD=   -8.90%  PCHIP=   -8.49%  dQ= +1.65pp
          resnet50/selected_303402  BD=   -8.29%  PCHIP=   -8.18%  dQ= +1.67pp
          resnet50/selected_303403  BD=   -8.14%  PCHIP=   -7.63%  dQ= +1.45pp
                    resnet50/fixed  BD=   -7.04%  PCHIP=   -6.63%  dQ= +1.48pp
          resnet50/forced_ensemble  BD=   -6.74%  PCHIP=   -5.88%  dQ= +1.03pp
            resnet50/forced_303401  BD=   -6.41%  PCHIP=   -5.95%  dQ= +1.12pp
        resnet50/calibrated_303402  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        resnet50/calibrated_303403  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
      resnet50/calibrated_ensemble  BD=   +0.00%  PCHIP=   +0.00%  dQ= +0.00pp
        resnet50/calibrated_303401  BD=   +0.01%  PCHIP=   +0.01%  dQ= -0.00pp

=== Selection counts (identity share per arm) ===
                  anchor  identity=100.0%  rate_fallback=0  q8_changed=0  total=2048
       calibrated_303401  identity= 99.6%  rate_fallback=0  q8_changed=1  total=2048
       calibrated_303402  identity=100.0%  rate_fallback=0  q8_changed=0  total=2048
       calibrated_303403  identity= 99.8%  rate_fallback=0  q8_changed=4  total=2048
     calibrated_ensemble  identity=100.0%  rate_fallback=0  q8_changed=0  total=2048
                   fixed  identity=  0.0%  rate_fallback=0  q8_changed=2048  total=2048
           forced_303401  identity= 18.0%  rate_fallback=0  q8_changed=1679  total=2048
           forced_303402  identity= 27.5%  rate_fallback=0  q8_changed=1485  total=2048
           forced_303403  identity= 30.7%  rate_fallback=0  q8_changed=1419  total=2048
         forced_ensemble  identity= 29.3%  rate_fallback=0  q8_changed=1447  total=2048
         selected_303401  identity= 27.3%  rate_fallback=0  q8_changed=1489  total=2048
         selected_303402  identity= 26.5%  rate_fallback=0  q8_changed=1506  total=2048
         selected_303403  identity= 27.5%  rate_fallback=0  q8_changed=1485  total=2048
       selected_ensemble  identity= 27.4%  rate_fallback=0  q8_changed=1486  total=2048

measurements.json sha256 = d5fceedc3bfd75792201b18577dcb1aa672abfa9466c835945ed80f87b9f9d09 (tải từ kernel)

=== Checkpoint calibration (bound vs tolerance) ===
training_303401.json: seed=303401 tolerance_od=0.05 feasible_actions=[0, 1, 2, 5, 6, 9, 10, 11, 12] bound_range=[0.0000..0.1264]
training_303402.json: seed=303402 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12] bound_range=[0.0000..0.0736]
training_303403.json: seed=303403 tolerance_od=0.05 feasible_actions=[0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12] bound_range=[0.0000..0.1378]
```

## 6. Tổng hợp BD-rate (các arm chính)

| Run | Codec | arm | BD-rate | PCHIP |
|---|---|---|---:|---:|
| v34-fix1-od-coco | h264 | `selected_303401` | -6.08% | -16.16% |
| v34-fix1-od-coco | h264 | `selected_ensemble` | -2.91% | -16.79% |
| v34-fix1-od-coco | h264 | `calibrated_303401` | +0.04% | +0.04% |
| v34-fix1-od-coco | h264 | `forced_303401` | +17.87% | -13.32% |
| v34-fix1-od-coco | h265 | `selected_303401` | -8.57% | -11.71% |
| v34-fix1-od-coco | h265 | `selected_ensemble` | -9.36% | -12.89% |
| v34-fix1-od-coco | h265 | `calibrated_303401` | -0.07% | -0.00% |
| v34-fix1-od-coco | h265 | `forced_303401` | -32.16% | -5.86% |
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
| v34-fix2-ar-od-scaled | ar-h264 | `swin3d_t/selected_303401` | -30.38% | -24.13% |
| v34-fix2-ar-od-scaled | ar-h264 | `r3d_18/selected_ensemble` | +1.66% | -0.05% |
| v34-fix2-ar-od-scaled | od-h264 | `resnet50/selected_303401` | -6.68% | -6.64% |
| v34-fix2-ar-od-scaled | od-h265 | `resnet50/selected_ensemble` | -9.36% | -9.12% |

cache sha256 = `9012c962b81fe7851330957261f203f32408c0fd996c6aa451189604735821d7` — mọi biến thể tái sử dụng cùng cache này (đối chiếu `measurements.json sha256` trong log từng biến thể).

## 7. Trạng thái kernel cuối

- `wagur124705/v34-fix1-od-coco`: **COMPLETE**  https://www.kaggle.com/code/wagur124705/v34-fix1-od-coco
- `tranthihongdieu/v34-fix2-od-rank`: **COMPLETE**  https://www.kaggle.com/code/tranthihongdieu/v34-fix2-od-rank
- `hieusunday0412/v34-fix2-od-huber`: **COMPLETE**  https://www.kaggle.com/code/hieusunday0412/v34-fix2-od-huber
- `nguyenhoanglan1232/v34-fix2-od-forced`: **COMPLETE**  https://www.kaggle.com/code/nguyenhoanglan1232/v34-fix2-od-forced
- `dngbolm/v34-fix2-ar-od-scaled`: **COMPLETE**  https://www.kaggle.com/code/dngbolm/v34-fix2-ar-od-scaled
[14:54:56] === Autopilot hoàn tất ===

## 8. Đọc nhanh (sau đính chính)

- **fix1 (pinball trước units — chỉ để chẩn đoán)**: `selected` H264 −6.08% (401) nhưng spread theo seed lớn (1.2–6.1pp); `forced_*` bất ổn định (H264 linear dương +2.4..+17.9% trong khi H265 linear −19..−32% — dấu ngược nhau giữa hai codec; PCHIP lại trái chiều) → supervision trước fix2 chưa đáng tin.
- **Fix2 rank**: `forced_*` ổn định và âm đều ở cả 2 codec (H264 −1.1..−7.1%, H265 −17..−23% linear / −4..−8% PCHIP); calibration bounds khỏe (feasible 9–12/13 action, bound ≤ 0.081). Spread `selected` trên split này 0.4–5.8pp (chưa thu hẹp rõ so fix1); trên split scaled (AR+OD cùng kernel) gọn hơn: −6.6..−8.0% (H264), −8.1..−9.4% (H265).
- **huber**: bounds 0.31–0.32 → chỉ action 0 feasible → calibrated bị khóa về identity; selected H265 ổn định nhất (−7.1..−7.3%). Kết luận: giữ **pinball**, huber không phù hợp cho risk head.
- **rank vs forced (shortlist_seed) trên OD**: gần như trùng nhau (cùng top action a11/a6/a4; identity ~1–4% vs anchor 100%) — khác không đáng kể. Trên AR, forced hại rõ (+4..+5% ở swin3d_t) → giữ mặc định **rank**.
- **Calibrated "sống" chưa?** Chưa: bounds đã feasible (rank: 9–12 action) nhưng action được chọn vẫn identity 99.0–100% (cả `selection_counts` lẫn test rows) → xem §9: trần chặn thật là chính dự đoán q0.9 (~0.25), coverage sweep post-hoc không hồi sinh được; không phải chuyện units.
- **AR scaled**: swin3d_t `selected` −20.8..−30.4% (H264) / −10.2..−12.2% (H265) — tín hiệu mạnh; **r3d_18** ~0..+6% — model yếu không hưởng lợi (hại nhẹ). `target_confirmed=false` (thiếu joint GT) — đây là pilot thăm dò, không phải kết luận production.
- **Hành vi chọn action (rank, OD test)**: selected/forced chọn a11/a6/a4 (≈36%/31%/19%); identity chỉ 4.2%; `fixed` = a11 100%; calibrated ≈ a0 (99%+).

## 9. Điều tra calibrated (hậu đêm) — chẩn đoán + thí nghiệm coverage sweep

**Chẩn đoán (cache `9012c962…`, 2048 rows train+cal):** calibrated không sống không phải chuyện rate-gate/guard — 2017/2048 rows bị chặn bởi **risk bound**, chỉ 10 bởi rate; residual calibration (a11=0.0, a6=0.0803, a4=0.028) không phải thủ phạm. `predicted_risk` (pinball q0.9) cho mọi action ≠ 0 ≈ **0.23–0.28 >> tolerance 0.05**. Damage thật: median 0.02–0.035 nhưng **p90 0.15–0.39** (đuôi nặng, kể cả từng ô codec×QP) → head q0.9 ≈ 0.25 là ước lượng phân vị 0.9 **đúng vai trò**, nhưng "cận tin cậy 90% ≤ 5%" đòi p90 ≤ 5% — không action nào đạt. Calibrated = identity là hành vi đúng của định nghĩa an toàn hiện tại, không phải bug.

**Thí nghiệm `v34-fix2-od-cal`** (ngynanhthuw, cache-reuse 192/64/48/256; arms `calibrated_c50/c60/c70` tính hậu huấn luyện từ residual CAL — không retrain):

- Ba mức coverage 0.5/0.6/0.7 cho **arm giống hệt nhau** (residual CAL tại các mức đó đều = 0 — head q0.9 vốn over-predict phần lớn rows); khác 0.9 chỉ ở residual nhỏ phía trên.
- Aliveness tăng không đáng kể: identity 98.1–99.7% (so 99.0–99.8% ở 0.9); chỉ các action "nhẹ" lọt qua (a8/a12/a9/a3).
- BD-rate ≈ 0: H264 −0.46..+0.40% (ensemble +0.13%), H265 −1.21..0% (ensemble −0.59%); dQ ≈ 0.
- **Kết luận**: trần chặn thật là **chính dự đoán q0.9 của head (~0.25)**, không phải residual → coverage sweep post-hoc không thể hồi sinh calibrated. Muốn "sống" phải hạ `risk_quantile` (retrain 1 run) hoặc nâng `damage_tolerance` — cả hai là đổi policy (đánh đổi an toàn), cần quyết định; mặc định giữ nguyên. Đường phân phối chính vẫn là source-guard: `selected` PCHIP −15.3..−15.8% (H264) / −12.6..−13.3% (H265) — **tái lập đúng biến thể rank** (cùng cache, cùng recipe).

