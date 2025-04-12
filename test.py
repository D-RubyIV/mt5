import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Tạo dữ liệu nến giả
data = {
    'time': pd.date_range(start='2023-01-01', periods=10, freq='D'),
    'open': [1, 2, 3, 4, 5, 4, 3, 2, 3, 4],
    'high': [2, 3, 5, 6, 7, 6, 4, 3, 4, 5],
    'low': [0, 1, 2, 3, 4, 3, 2, 1, 2, 3],
    'close': [1.5, 2.5, 4, 5, 6, 5, 3.5, 2.5, 3.5, 4.5],
}

# Chuyển thành DataFrame
df = pd.DataFrame(data)

# Sử dụng scipy để tìm các đỉnh (peaks) và đáy (troughs)
peaks, _ = find_peaks(df['high'])
troughs, _ = find_peaks(-df['low'])

# Thêm cột is_peak và is_trough vào DataFrame
df['is_peak'] = False
df['is_trough'] = False

# Đánh dấu các đỉnh và đáy trong DataFrame
df.loc[peaks, 'is_peak'] = True
df.loc[troughs, 'is_trough'] = True

# Lọc các đỉnh và đáy trong cửa sổ động
rolling_max = df['high'].rolling(window=2 * 2 + 1, center=True, min_periods=1).max()
rolling_min = df['low'].rolling(window=2 * 2 + 1, center=True, min_periods=1).min()

# Kiểm tra đỉnh và đáy trong cửa sổ
df['is_peak'] = df['is_peak'] & (df['high'] == rolling_max)
df['is_trough'] = df['is_trough'] & (df['low'] == rolling_min)
# In ra kết quả
print(df)

# Vẽ đồ thị nến và đánh dấu đỉnh, đáy
plt.plot(df['time'], df['close'], label="Close Price", color='black')
plt.scatter(df['time'].iloc[peaks], df['high'].iloc[peaks], color='red', label='Peaks')
plt.scatter(df['time'].iloc[troughs], df['low'].iloc[troughs], color='green', label='Troughs')
plt.legend()
plt.title("Peak and Trough Detection")
plt.xlabel("Time")
plt.ylabel("Price")
plt.grid(True)
plt.show()
