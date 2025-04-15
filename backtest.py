import pandas as pd


def backtest(df):
    # Thêm các cột cho entry_price, tp_price, sl_price, trạng thái lệnh (win, loss)
    df['entry_price'] = None
    df['tp_price'] = None
    df['sl_price'] = None
    df['status'] = None
    df['profit_loss'] = None

    win_count = 0
    loss_count = 0
    total_pnl = 0

    for i in range(1, len(df)):  # Bắt đầu từ chỉ số 1 để so sánh với nến trước đó
        if df['signal'][i] == 'BUY':  # Tín hiệu mua
            entry_price = df['close'][i]
            stop_loss = df['low'][i]  # SL là giá thấp nhất của nến tín hiệu buy
            df.at[i, 'sl_price'] = stop_loss  # Ghi nhận giá SL

            tp_price = None  # TP sẽ được tính theo tín hiệu đảo chiều

            # Tìm tín hiệu đảo chiều SELL sau BUY
            for j in range(i + 1, len(df)):
                if df['signal'][j] == 'SELL':
                    tp_price = df['close'][j]
                    break

            if tp_price:  # Nếu tìm được TP
                df.at[i, 'entry_price'] = entry_price
                df.at[i, 'tp_price'] = tp_price

                # Xử lý việc thắng hay thua
                if tp_price > entry_price:  # Lệnh thắng
                    df.at[i, 'status'] = 'win'
                    win_count += 1
                    total_pnl += (tp_price - entry_price)
                else:  # Lệnh thua
                    df.at[i, 'status'] = 'loss'
                    loss_count += 1
                    total_pnl += (tp_price - entry_price)
            else:
                df.at[i, 'status'] = 'no_tp'
        elif df['signal'][i] == 'SELL':  # Tín hiệu bán
            entry_price = df['close'][i]
            stop_loss = df['high'][i]  # SL là giá cao nhất của nến tín hiệu SELL
            df.at[i, 'sl_price'] = stop_loss  # Ghi nhận giá SL
            tp_price = None  # TP sẽ được tính theo tín hiệu đảo chiều

            # Tìm tín hiệu đảo chiều BUY sau SELL
            for j in range(i + 1, len(df)):
                if df['signal'][j] == 'BUY':
                    tp_price = df['close'][j]
                    break

            if tp_price:  # Nếu tìm được TP
                df.at[i, 'entry_price'] = entry_price
                df.at[i, 'tp_price'] = tp_price

                # Xử lý việc thắng hay thua
                if tp_price < entry_price:  # Lệnh thắng
                    df.at[i, 'status'] = 'win'
                    win_count += 1
                    total_pnl += (entry_price - tp_price)
                else:  # Lệnh thua
                    df.at[i, 'status'] = 'loss'
                    loss_count += 1
                    total_pnl += (entry_price - tp_price)
            else:
                df.at[i, 'status'] = 'no_tp'

    # Tính toán tỷ lệ PnL
    if win_count + loss_count > 0:
        pnl_ratio = win_count / (win_count + loss_count)
    else:
        pnl_ratio = 0

    # Trả về kết quả cần thiết
    return df, win_count, loss_count, pnl_ratio, total_pnl


# Ví dụ sử dụng:
# Giả sử bạn đã có DataFrame df chứa dữ liệu của bạn
# df = pd.read_csv('your_data.csv')  # hoặc cách khác để tạo DataFrame

