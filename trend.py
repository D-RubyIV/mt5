class TrendDetector:
    @staticmethod
    def detect_latest_trend(df, level_max=3):
        latest_trend_by_level = {}

        for level in range(1, level_max + 1):
            peak_col = f"peak_level_{level}"
            trough_col = f"trough_level_{level}"

            peaks = df[df[peak_col]]
            troughs = df[df[trough_col]]

            # Gộp đỉnh và đáy lại để so thời gian
            combined = []
            for i in range(1, len(peaks)):
                combined.append((peaks.iloc[i]['time'], 'peak', peaks.iloc[i]['high'], peaks.iloc[i - 1]['high']))
            for i in range(1, len(troughs)):
                combined.append((troughs.iloc[i]['time'], 'trough', troughs.iloc[i]['low'], troughs.iloc[i - 1]['low']))

            # Sắp xếp theo thời gian giảm dần
            combined.sort(reverse=True, key=lambda x: x[0])

            # Lấy xu hướng gần nhất
            if combined:
                time, kind, current, previous = combined[0]
                if kind == 'peak':
                    if current > previous:
                        latest_trend_by_level[level] = f"Uptrend at {time}"
                    elif current < previous:
                        latest_trend_by_level[level] = f"Downtrend at {time}"
                    else:
                        latest_trend_by_level[level] = f"Sideways at {time}"
                else:  # trough
                    if current > previous:
                        latest_trend_by_level[level] = f"Uptrend at {time}"
                    elif current < previous:
                        latest_trend_by_level[level] = f"Downtrend at {time}"
                    else:
                        latest_trend_by_level[level] = f"Sideways at {time}"
            else:
                latest_trend_by_level[level] = "No trend data"

        return latest_trend_by_level

    @staticmethod
    def print_latest_trends(latest_trend_by_level):
        for level, trend in latest_trend_by_level.items():
            print(f"Level {level}:\n  {trend}\n")
