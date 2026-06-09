"""
INVESTMENT_PLAN.py
==================
แผนลงทุน NEXUS GOLD — ทุน 1,500 บาท
รันไฟล์นี้เพื่อดูตารางทบทุนแบบ interactive
"""

# ── ตัวแปรแผนลงทุน ──────────────────────────────────

CAPITAL_START    = 1500    # ทุนเริ่มต้น (บาท)
MONTHLY_RETURN   = 0.082   # ผลตอบแทน/เดือน 8.2% (กรณีปกติ)
MONTHLY_ADD      = 0        # เพิ่มทุนทุกเดือน (บาท) ตั้งเป็น 0 = ทบทุนอย่างเดียว
TARGET_MONTHLY   = 3000    # เป้าหมายกำไรต่อเดือน (บาท)
FEE_PER_MONTH    = 34      # ค่าธรรมเนียม Binance/เดือน (บาท)

# ── คำนวณ ────────────────────────────────────────────

def calculate_plan():
    capital = CAPITAL_START
    print("=" * 60)
    print("  NEXUS GOLD — แผนทบทุน")
    print(f"  ทุนเริ่มต้น: {CAPITAL_START:,} บาท")
    print(f"  ผลตอบแทน/เดือน: {MONTHLY_RETURN*100:.1f}%")
    print(f"  ค่าธรรมเนียม/เดือน: {FEE_PER_MONTH} บาท")
    print("=" * 60)
    print(f"{'เดือน':>6} | {'ทุนสะสม':>12} | {'กำไร/เดือน':>12} | {'สถานะ':>10}")
    print("-" * 60)

    for month in range(1, 37):
        gross = capital * MONTHLY_RETURN
        net   = gross - FEE_PER_MONTH
        capital = capital + net + MONTHLY_ADD

        status = ""
        if net >= TARGET_MONTHLY:
            status = "🎯 ถึงเป้า!"
        elif net >= TARGET_MONTHLY * 0.5:
            status = "📈 ดี"
        elif net >= TARGET_MONTHLY * 0.25:
            status = "🌱 เติบโต"
        else:
            status = "🌱 เริ่มต้น"

        print(f"{month:>6} | {capital:>10,.0f} ฿ | {net:>10,.0f} ฿ | {status}")

        if net >= TARGET_MONTHLY:
            print("-" * 60)
            print(f"  🎉 ถึงเป้า {TARGET_MONTHLY:,} บาท/เดือน ที่เดือนที่ {month}!")
            break

    print("=" * 60)
    print("\nหมายเหตุ: ตัวเลขเป็นการประมาณการ ไม่รับประกันผลตอบแทน")


# ── CONFIG ปัจจุบัน ──────────────────────────────────

CURRENT_CONFIG = {
    "ทุน":              "1,500 บาท (~42 USDT)",
    "Order Size":       "8 USDT/order",
    "Stop Loss":        "0.8%",
    "Take Profit":      "1.8%",
    "R:R Ratio":        "1:2.25",
    "Confidence":       "78%+ เท่านั้น",
    "รอบเทรด":          "~2 ครั้ง/วัน (เฉลี่ย)",
    "Interval":         "5 นาที",
    "Win Rate คาด":     "67%",
    "กำไรคาด/เดือน":    "~120 บาท (กรณีปกติ)",
    "ค่า Fee/เดือน":    "~34 บาท",
}


def show_config():
    print("\n" + "=" * 60)
    print("  CONFIG ปัจจุบัน — ทุน 1,500 บาท")
    print("=" * 60)
    for k, v in CURRENT_CONFIG.items():
        print(f"  {k:<20} : {v}")
    print("=" * 60)


# ── RISK SCENARIOS ───────────────────────────────────

def show_risk():
    print("\n" + "=" * 60)
    print("  ความเสี่ยง 3 กรณี — เดือนแรก")
    print("=" * 60)
    scenarios = [
        ("🟢 ดีที่สุด",   0.12,  "Trend ชัด ตลาดดี"),
        ("🟡 ปกติ",       0.082, "ตลาดผสม"),
        ("🔴 แย่ที่สุด",  -0.06, "Sideway ตลอด"),
    ]
    for name, ret, desc in scenarios:
        profit = CAPITAL_START * ret - FEE_PER_MONTH
        print(f"  {name} ({desc})")
        print(f"    กำไร/ขาดทุน: {profit:+.0f} บาท ({ret*100:+.1f}%)")
        print()
    print("=" * 60)


if __name__ == "__main__":
    show_config()
    show_risk()
    calculate_plan()
