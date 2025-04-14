import pandas as pd


def detect_msb(df):
    # MSB đơn giản: Higher Highs và Higher Lows bị phá
    hh1 = df['high'].iloc[-3]
    hh2 = df['high'].iloc[-2]
    hl1 = df['low'].iloc[-3]
    hl2 = df['low'].iloc[-2]
    curr_low = df['low'].iloc[-1]
    curr_high = df['high'].iloc[-1]

    # Bullish MSB: phá đỉnh
    if curr_high > max(hh1, hh2) and curr_low > min(hl1, hl2):
        return "bullish", 40
    # Bearish MSB: phá đáy
    elif curr_low < min(hl1, hl2) and curr_high < max(hh1, hh2):
        return "bearish", 40
    return None, 0

def detect_pda_zone(df, zone="discount"):
    # Premium/Discount Zone theo Fibonacci 50%
    recent_high = df['high'].iloc[-20:].max()
    recent_low = df['low'].iloc[-20:].min()
    curr_price = df['close'].iloc[-1]

    mid = (recent_high + recent_low) / 2

    if zone == "discount" and curr_price < mid:
        return True, 20
    elif zone == "premium" and curr_price > mid:
        return True, 20
    return False, 0

def detect_trend(df):
    # Dựa trên cấu trúc thị trường đơn giản: Higher Highs / Lower Lows
    if df['high'].iloc[-1] > df['high'].iloc[-5] and df['low'].iloc[-1] > df['low'].iloc[-5]:
        return "bullish", 30
    elif df['high'].iloc[-1] < df['high'].iloc[-5] and df['low'].iloc[-1] < df['low'].iloc[-5]:
        return "bearish", 30
    return "sideways", 10

def detect_liquidity_sweep(df):
    # Sweep đơn giản: giá vượt đỉnh/đáy trước đó rồi quay đầu
    last_high = df['high'].iloc[-2]
    last_low = df['low'].iloc[-2]
    curr_high = df['high'].iloc[-1]
    curr_low = df['low'].iloc[-1]
    if curr_high > last_high and df['close'].iloc[-1] < last_high:
        return "sweep_high", 10
    elif curr_low < last_low and df['close'].iloc[-1] > last_low:
        return "sweep_low", 10
    return None, 0

def detect_fvg(df):
    # FVG đơn giản: gap lớn giữa close của nến 1 và open của nến 3
    fvg = []
    for i in range(2, len(df)):
        if df['low'].iloc[i] > df['high'].iloc[i-2]:
            fvg.append((df['time'].iloc[i], "up_fvg"))
        elif df['high'].iloc[i] < df['low'].iloc[i-2]:
            fvg.append((df['time'].iloc[i], "down_fvg"))
    return fvg[-1] if fvg else (None, None)

def detect_order_block(df):
    # OB đơn giản: nến giảm mạnh trước khi tăng mạnh (hoặc ngược lại)
    last = df.iloc[-3]
    current = df.iloc[-2]
    next_candle = df.iloc[-1]
    if last['close'] < last['open'] and current['close'] > current['open'] and next_candle['close'] > current['close']:
        return "bullish_ob", 15
    elif last['close'] > last['open'] and current['close'] < current['open'] and next_candle['close'] < current['close']:
        return "bearish_ob", 15
    return None, 0

def detect_consolidation(df):
    # Nếu phạm vi giá nhỏ trong 5 nến
    last_5 = df.tail(5)
    range_size = last_5['high'].max() - last_5['low'].min()
    avg_range = df['high'] - df['low']
    if range_size < avg_range.mean():
        return "consolidation", 10
    return None, 0

def analyze_ict_signals_with_pda(df):
    signals = []

    for i in range(30, len(df)):
        chunk = df.iloc[i-30:i+1].copy()
        timestamp = chunk['time'].iloc[-1]
        score = 0
        factors = []

        # 1. MSB
        trend, s = detect_msb(chunk)
        if trend:
            score += s
            factors.append(f"MSB ({trend})")

        # 2. PDA Zone
        pda_ok, s = detect_pda_zone(chunk, "discount" if trend == "bullish" else "premium")
        if pda_ok:
            score += s
            factors.append("PDA Zone")

        # 3. Sweep
        sweep, s = detect_liquidity_sweep(chunk)
        if sweep:
            score += s
            factors.append(f"Sweep ({sweep})")

        # 4. OB
        ob_type, s = detect_order_block(chunk)
        if ob_type:
            score += s
            factors.append(f"Order Block ({ob_type})")

        # 5. FVG
        fvg_time, fvg_type = detect_fvg(chunk)
        if fvg_type:
            score += 10
            factors.append(f"FVG ({fvg_type})")

        # 6. Consolidation
        cons, s = detect_consolidation(chunk)
        if cons:
            score += s
            factors.append("Consolidation")

        # ✅ Điều kiện vào lệnh: có MSB + PDA zone + ít nhất 1 yếu tố phụ
        if trend and pda_ok and len(factors) >= 3 and score >= 60:
            signals.append({
                "time": str(timestamp),
                "signal": "BUY" if trend == "bullish" else "SELL",
                "score": score,
                "factors": factors
            })

    return signals