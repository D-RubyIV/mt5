from object.model import TrendObject


class TrendDetector:
    @staticmethod
    def detect_latest_trend(df, level_max=3):
        latest_trend_by_level = {}
        current_price = df.iloc[-1]['close']  # Giá hiện tại

        for level in range(1, level_max + 1):
            peak_col = f"peak_level_{level}"
            trough_col = f"trough_level_{level}"

            peaks = df[df[peak_col]].reset_index(drop=True)
            troughs = df[df[trough_col]].reset_index(drop=True)

            if len(peaks) >= 1 and len(troughs) >= 1:
                # Đỉnh và đáy gần nhất
                latest_peak = peaks.iloc[-1]
                latest_trough = troughs.iloc[-1]

                # Kiểm tra xu hướng của Level
                if level == 1:
                    # Level 1: So với đỉnh và đáy gần nhất
                    if current_price > latest_trough['low']:
                        latest_trend_by_level[level] = f"Uptrend at {latest_trough['time']}"
                    elif current_price < latest_peak['high']:
                        latest_trend_by_level[level] = f"Downtrend at {latest_peak['time']}"
                    else:
                        latest_trend_by_level[level] = f"Sideways at {latest_peak['time']}"

                elif level == 2:
                    # Level 2: So với đỉnh đáy gần nhất ở Level 2
                    if current_price > latest_trough['low']:
                        latest_trend_by_level[level] = f"Uptrend at {latest_trough['time']}"
                    elif current_price < latest_peak['high']:
                        latest_trend_by_level[level] = f"Downtrend at {latest_peak['time']}"
                    else:
                        latest_trend_by_level[level] = f"Sideways at {latest_peak['time']}"

                elif level == 3:
                    # Level 3: So với đỉnh đáy gần nhất ở Level 3
                    if current_price > latest_trough['low']:
                        latest_trend_by_level[level] = f"Uptrend at {latest_trough['time']}"
                    elif current_price < latest_peak['high']:
                        latest_trend_by_level[level] = f"Downtrend at {latest_peak['time']}"
                    else:
                        latest_trend_by_level[level] = f"Sideways at {latest_peak['time']}"

        return latest_trend_by_level

    @staticmethod
    def print_latest_trends(latest_trend_by_level) -> list[TrendObject]:
        list_trend_objects: list[TrendObject] = []
        for level, trend in latest_trend_by_level.items():
            # print(f"Level {level}:\n  {trend}\n")
            list_trend_objects.append(TrendObject(level, trend))
        return list_trend_objects
