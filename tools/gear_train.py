# -*- coding: utf-8 -*-
"""
双联齿轮传动链计算器

和 gear_calc.py 的区别:
    gear_calc.py  算"两个独立齿轮啮合"的单级/两级, 传动比是加法式地凑
    gear_train.py 算"双联齿轮串起来"的多级传动链, 传动比是乘法式地翻倍

双联齿轮(compound gear) = 大齿轮和小齿轮做在同一个轮毂上, 同轴同速。
传动链长这样:

    电机轴小齿 p0
        └啮合→ 双联A.大齿  (A.大齿 和 A.小齿 同轴, 一起转)
                    └啮合→ 双联B.大齿
                                └啮合→ 最终输出齿(差速器盘齿)

    总传动比 i = (A.大/p0) × (B.大/A.小) × (输出/B.小)

每一处啮合的中心距仍然是老师给的那条公式:  a = m(z1+z2)/2

用法:
    python tools/gear_train.py --pinion 10 12 \
        --compound 30:10 32:12 28:10 --final 40 --wheel 30 --mass 0.4
"""
import argparse
import itertools

MOTOR_RPM = 13000.0
MOTOR_TORQUE_GCM = 28.0
GCM_TO_NM = 9.80665e-5
PI = 3.14159265
MOTOR_COUNT = [1]      # 由 --motors 设定, 扭矩按电机数叠加


def parse_compound(s):
    """'30:10' -> (30, 10)  大齿:小齿"""
    try:
        big, small = s.split(":")
        big, small = int(big), int(small)
    except ValueError:
        raise argparse.ArgumentTypeError(f"双联齿轮要写成 大齿:小齿, 例如 30:10 (收到 {s!r})")
    if small >= big:
        raise argparse.ArgumentTypeError(f"{s}: 小齿数应当小于大齿数")
    return (big, small)


def evaluate(pinion, chain, final, module, wheel_mm, mass_kg, eff_per_stage):
    """返回 (总传动比, 各级中心距列表, 级数)"""
    ratio = 1.0
    centers = []
    drive = pinion                       # 当前主动齿(小齿)
    for big, small in chain:
        ratio *= big / drive
        centers.append(module * (drive + big) / 2.0)
        drive = small                    # 同轴的小齿变成下一级的主动齿
    ratio *= final / drive
    centers.append(module * (drive + final) / 2.0)
    stages = len(chain) + 1
    return ratio, centers, stages


def perf(ratio, stages, wheel_mm, mass_kg, eff_per_stage):
    circ = PI * wheel_mm / 1000.0
    r = wheel_mm / 2000.0
    v = circ * (MOTOR_RPM / ratio) / 60.0
    eff = eff_per_stage ** stages
    t_wheel = MOTOR_TORQUE_GCM * GCM_TO_NM * ratio * eff * MOTOR_COUNT[0]
    accel = (t_wheel / r) / mass_kg
    return v, accel


def verdict(v, accel):
    if v > 6.0:
        return "极速过高, FPV 来不及反应"
    if v < 1.5:
        return "太慢, 直道被拉开"
    if accel < 1.5:
        return "起步肉"
    if accel > 6.0:
        return "扭矩过剩, 易打滑(电控限斜率可解)"
    return "OK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", type=float, default=0.5)
    ap.add_argument("--pinion", type=int, nargs="+", required=True,
                    help="可装在电机轴上的小齿轮齿数(可多个, 会逐个试)")
    ap.add_argument("--compound", type=parse_compound, nargs="*", default=[],
                    help="双联齿轮, 写成 大齿:小齿, 例如 30:10 32:12")
    ap.add_argument("--final", type=int, required=True,
                    help="最终输出齿数(通常是差速器上那圈盘齿)")
    ap.add_argument("--wheel", type=float, default=30.0, help="车轮直径 mm")
    ap.add_argument("--mass", type=float, default=0.40, help="整车质量 kg")
    ap.add_argument("--eff", type=float, default=0.90, help="每级传动效率")
    ap.add_argument("--encoder-ppr", type=float, default=13.0)
    ap.add_argument("--max-stages", type=int, default=3,
                    help="最多用几个双联齿轮(级数 = 这个数 + 1)")
    ap.add_argument("--only-ok", action="store_true")
    ap.add_argument("--motors", type=int, default=1,
                    help="驱动电机数量。多个电机机械耦合到同一传动链时扭矩叠加, "
                         "极速不变(取决于转速), 只有加速度翻倍。")
    args = ap.parse_args()

    m = args.module
    MOTOR_COUNT[0] = args.motors
    print()
    print(f"电机 {MOTOR_RPM:.0f}rpm / {MOTOR_TORQUE_GCM:.0f}g·cm    "
          f"轮径 {args.wheel:.0f}mm    整车 {args.mass:.2f}kg    模数 {m}")
    print(f"电机轴可选小齿: {args.pinion}")
    print(f"双联齿轮: {['%d:%d' % c for c in args.compound] or '(无)'}")
    print(f"最终输出齿: {args.final}")
    print("=" * 100)
    print(f"{'传动链':<34}{'总减速比':>9}{'级数':>5}{'极速m/s':>9}"
          f"{'km/h':>8}{'加速m/s²':>10}  评价")
    print("-" * 100)

    rows = []
    for p in args.pinion:
        for n in range(0, min(args.max_stages, len(args.compound)) + 1):
            for chain in itertools.permutations(args.compound, n):
                ratio, centers, stages = evaluate(
                    p, chain, args.final, m, args.wheel, args.mass, args.eff)
                v, a = perf(ratio, stages, args.wheel, args.mass, args.eff)
                label = f"{p}"
                for big, small in chain:
                    label += f">{big}:{small}"
                label += f">{args.final}"
                rows.append((ratio, label, stages, centers, v, a, verdict(v, a)))

    rows.sort(key=lambda r: r[0])
    shown = 0
    for ratio, label, stages, centers, v, a, note in rows:
        if args.only_ok and note != "OK":
            continue
        mark = "  <<<" if note == "OK" else ""
        print(f"{label:<34}{ratio:>9.2f}{stages:>5}{v:>9.2f}"
              f"{v*3.6:>8.1f}{a:>10.2f}  {note}{mark}")
        cs = "  ".join(f"{c:.2f}" for c in centers)
        print(f"{'':<34}中心距: {cs} mm")
        shown += 1

    if shown == 0:
        print("  (没有方案落在可用区间)")
    print("=" * 100)

    circ = PI * args.wheel / 1000.0
    print()
    print("【给电控的换算】COUNTS_PER_METER = 编码器线数 × 4 × 传动比 / 轮周长(m)")
    print(f"    轮周长 = π × {args.wheel:.0f}mm = {circ:.4f}m")
    ok = [r for r in rows if r[6] == "OK"]
    for ratio, label, *_ in ok[:5]:
        cpm = args.encoder_ppr * 4 * ratio / circ
        print(f"    {label:<34} i={ratio:6.2f}  ->  COUNTS_PER_METER = {cpm:8.1f}")
    print()
    print("    注意: 理论值仅供核对数量级, 最终以实测标定为准"
          "(地面量 1 米, 手推车走完读总计数)。")
    print("    编码器装在电机轴上时用电机侧传动比; 装在轮轴上则 COUNTS_PER_METER "
          "与传动比无关。")


if __name__ == "__main__":
    main()
