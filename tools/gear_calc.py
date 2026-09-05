# -*- coding: utf-8 -*-
"""
传动比计算器 —— 模数 0.5 齿轮

老师给的三条基础公式：
    分度圆直径  d = m * z              (m=模数=0.5, z=齿数)
    中心距      a = (d1 + d2) / 2 = m * (z1 + z2) / 2
    传动比      i = z_从动 / z_主动

本脚本在这三条之上, 把传动比换算成车真正关心的三个量：
    极速、起步加速度、以及固件里的 COUNTS_PER_METER

用法:
    python tools/gear_calc.py                                # 默认假设, 看量级
    python tools/gear_calc.py --wheel 30 --mass 0.45         # 换成实测值
    python tools/gear_calc.py --tip-dia 15 16 9 17           # 卡尺量的外径推齿数
    python tools/gear_calc.py --teeth 10 12 28 30 --two-stage --only-ok
"""
import argparse
import itertools

# ---- 电机参数 (来自主办方 PPT) ----
MOTOR_RPM = 13000.0        # 额定转速
MOTOR_TORQUE_GCM = 28.0    # 额定扭矩 g·cm
GCM_TO_NM = 9.80665e-5     # 1 g·cm = 9.80665e-5 N·m

PI = 3.14159265


def analyse(z_drive, z_driven, module, wheel_mm, mass_kg, eff, stages=None):
    i = z_driven / z_drive if stages is None else stages
    r = wheel_mm / 2000.0                 # 轮半径, m
    circ = PI * wheel_mm / 1000.0         # 轮周长, m

    v = circ * (MOTOR_RPM / i) / 60.0     # m/s

    t_motor = MOTOR_TORQUE_GCM * GCM_TO_NM
    t_wheel = t_motor * i * eff
    force = t_wheel / r
    accel = force / mass_kg               # m/s^2, 忽略滚阻和风阻

    center = module * (z_drive + z_driven) / 2.0
    return i, v, accel, center, force


def verdict(v, accel):
    """室内小赛道的经验判断"""
    if v > 6.0:
        return "极速过高, FPV 视角来不及反应"
    if v < 1.5:
        return "太慢, 直道会被拉开"
    if accel < 1.5:
        return "起步肉, 出弯吃亏"
    if accel > 6.0:
        return "扭矩过剩, 易打滑(可用电控限斜率)"
    return "OK"


def teeth_from_tip(dias, module):
    """卡尺量到的是齿顶圆(齿尖到齿尖), 不是分度圆 —— 分度圆在齿廓中间, 量不到。
         齿顶圆 d_tip = m*(z+2)   =>   z = d_tip/m - 2
       和按分度圆算相比差 2 个齿, 折算到中心距是 0.5mm 误差,
       足以让齿轮卡死或打滑, 所以务必数一遍齿数核对。"""
    return [round(d / module - 2) for d in dias]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", type=float, default=0.5, help="齿轮模数, 默认 0.5")
    ap.add_argument("--teeth", type=int, nargs="+",
                    default=[10, 12, 15, 16, 20, 24, 30, 40],
                    help="手头可用的齿数(实测后填真实值)")
    ap.add_argument("--tip-dia", type=float, nargs="+", default=None,
                    help="卡尺量到的齿顶圆外径(mm), 自动推齿数: z = d/m - 2")
    ap.add_argument("--pitch-dia", type=float, nargs="+", default=None,
                    help="已知分度圆直径(mm), 推齿数: z = d/m")
    ap.add_argument("--wheel", type=float, default=40.0, help="车轮直径 mm(实测)")
    ap.add_argument("--mass", type=float, default=0.40, help="整车质量 kg(实测)")
    ap.add_argument("--eff", type=float, default=0.90, help="单级传动效率")
    ap.add_argument("--encoder-ppr", type=float, default=13.0,
                    help="编码器单圈脉冲数(每通道), 4 倍频前")
    ap.add_argument("--two-stage", action="store_true", help="同时枚举两级减速")
    ap.add_argument("--only-ok", action="store_true", help="只列出评价为 OK 的方案")
    args = ap.parse_args()

    m = args.module

    if args.tip_dia:
        args.teeth = teeth_from_tip(args.tip_dia, m)
        print()
        print("由齿顶圆外径推算齿数(卡尺量的是齿顶圆, 不是分度圆):")
        for d, z in zip(args.tip_dia, args.teeth):
            print(f"    外径 {d:5.1f}mm  ->  {z:>3d} 齿    "
                  f"分度圆 {m*z:5.1f}mm    反算外径 {m*(z+2):5.1f}mm")
        print("    注意: 请数一遍齿数核对。若实际比这里多 2 齿, "
              "说明你量的是分度圆, 改用 --pitch-dia。")
    elif args.pitch_dia:
        args.teeth = [round(d / m) for d in args.pitch_dia]
        print()
        print("由分度圆直径推算齿数:")
        for d, z in zip(args.pitch_dia, args.teeth):
            print(f"    分度圆 {d:5.1f}mm  ->  {z:>3d} 齿")

    print()
    print(f"电机 {MOTOR_RPM:.0f}rpm / {MOTOR_TORQUE_GCM:.0f}g·cm    "
          f"轮径 {args.wheel:.0f}mm    整车 {args.mass:.2f}kg    模数 {m}")
    print(f"可用齿数: {sorted(args.teeth)}")
    print("=" * 94)
    print(f"{'齿数配对':<15}{'传动比':>7}{'中心距mm':>15}{'极速m/s':>9}"
          f"{'极速km/h':>10}{'加速m/s²':>10}  评价")
    print("-" * 94)

    rows = []
    for z1, z2 in itertools.permutations(args.teeth, 2):
        if z2 <= z1:
            continue                      # 只看减速
        i, v, a, c, _ = analyse(z1, z2, m, args.wheel, args.mass, args.eff)
        rows.append((i, f"{z1}T -> {z2}T", c, v, a, verdict(v, a)))

    if args.two_stage:
        seen = set()
        for z1, z2, z3, z4 in itertools.permutations(args.teeth, 4):
            if z2 <= z1 or z4 <= z3:
                continue
            key = frozenset([(z1, z2), (z3, z4)])   # 两级顺序对调是同一套传动
            if key in seen:
                continue
            seen.add(key)
            i = (z2 / z1) * (z4 / z3)
            _, v, a, _, _ = analyse(1, 1, m, args.wheel, args.mass,
                                    args.eff ** 2, stages=i)
            c = (m * (z1 + z2) / 2.0, m * (z3 + z4) / 2.0)
            rows.append((i, f"{z1}>{z2} {z3}>{z4}", c, v, a, verdict(v, a)))

    rows.sort(key=lambda r: r[0])
    shown = 0
    for i, label, c, v, a, note in rows:
        if args.only_ok and note != "OK":
            continue
        cs = f"{c:.2f}" if isinstance(c, float) else f"{c[0]:.2f}+{c[1]:.2f}"
        mark = "  <<<" if note == "OK" else ""
        print(f"{label:<15}{i:>7.2f}{cs:>15}{v:>9.2f}{v*3.6:>10.1f}"
              f"{a:>10.2f}  {note}{mark}")
        shown += 1

    if shown == 0:
        print("  (没有任何方案落在可用区间 —— 现有齿轮凑不出合适的减速比)")
    print("=" * 94)

    best = max((r[0] for r in rows), default=0.0)
    print()
    print(f"现有齿轮能凑出的最大减速比: {best:.2f}")

    print()
    print("【给电控的换算】固件里的 COUNTS_PER_METER：")
    print("    COUNTS_PER_METER = 编码器每圈脉冲数 × 4(四倍频) × 传动比 / 轮周长(m)")
    circ = PI * args.wheel / 1000.0
    print(f"    轮周长 = π × {args.wheel:.0f}mm = {circ*1000:.1f}mm = {circ:.4f}m")
    for i in (2, 3, 5, 8, 10, 15):
        cpm = args.encoder_ppr * 4 * i / circ
        print(f"    传动比 {i:>2}  ->  COUNTS_PER_METER = {cpm:8.1f}"
              f"   (按 {args.encoder_ppr:.0f} 线编码器)")
    print()
    print("    注意: 这只是理论值。实测标定永远优先: 地面量 1 米, 手推车走完读总计数。")


if __name__ == "__main__":
    main()
