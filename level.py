from scipy.signal import find_peaks


class MultiLevelPeaksTroughs:
    @staticmethod
    def detect_level_1(df):
        peaks, _ = find_peaks(df['high'], distance=1)
        troughs, _ = find_peaks(-df['low'], distance=1)
        df['peak_level_1'] = False
        df['trough_level_1'] = False
        df.loc[peaks, 'peak_level_1'] = True
        df.loc[troughs, 'trough_level_1'] = True
        return df

    @staticmethod
    def detect_level(df, level):
        prev_peak = f'peak_level_{level - 1}'
        prev_trough = f'trough_level_{level - 1}'
        curr_peak = f'peak_level_{level}'
        curr_trough = f'trough_level_{level}'

        df[curr_peak] = False
        df[curr_trough] = False

        # Lấy các chỉ số đỉnh/đáy level trước
        peak_indices = df[df[prev_peak]].index.tolist()
        trough_indices = df[df[prev_trough]].index.tolist()

        new_peak_count = 0
        new_trough_count = 0

        for i in range(1, len(peak_indices) - 1):
            prev_idx, curr_idx, next_idx = peak_indices[i - 1], peak_indices[i], peak_indices[i + 1]
            if df.loc[curr_idx, 'high'] > df.loc[prev_idx, 'high'] and df.loc[curr_idx, 'high'] > df.loc[
                next_idx, 'high']:
                df.at[curr_idx, curr_peak] = True
                new_peak_count += 1

        for i in range(1, len(trough_indices) - 1):
            prev_idx, curr_idx, next_idx = trough_indices[i - 1], trough_indices[i], trough_indices[i + 1]
            if df.loc[curr_idx, 'low'] < df.loc[prev_idx, 'low'] and df.loc[curr_idx, 'low'] < df.loc[next_idx, 'low']:
                df.at[curr_idx, curr_trough] = True
                new_trough_count += 1

        return df, new_peak_count + new_trough_count

    @staticmethod
    def detect_all_levels(df, max_level=100):
        df = MultiLevelPeaksTroughs.detect_level_1(df)
        for level in range(2, max_level + 1):
            df, count = MultiLevelPeaksTroughs.detect_level(df, level)
            if count == 0:
                print(f'Không còn đỉnh/đáy mới ở level {level}, dừng lại.')
                break
        return df
