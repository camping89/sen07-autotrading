# SEN07 - Auto Trading Data Fetcher

Chương trình lấy dữ liệu thị trường từ nhiều nguồn khác nhau, lưu vào SQL Server, backtest chiến lược, xuất file, show chart, với cấu trúc project chuẩn hóa, dễ mở rộng.

## Cài đặt

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Cấu hình file `config/config.json`:
```json
{
    "sql": { ... },
    "tv": { ... },
    "mt5": { ... },
    ...
}
```

## Cấu trúc thư mục

```
SEN07/
├── apps/
│   ├── database/      # Script thao tác database, ETL, sync
│   │   ├── setup_database.py           # Khởi tạo DB, tạo bảng, insert mẫu
│   │   ├── clear_data_tables.py        # Xóa dữ liệu các bảng data
│   │   ├── historical_mt5_to_sql.py    # Lấy dữ liệu lịch sử từ MT5 về SQL
│   │   └── realtime_mt5_to_sql.py      # Lấy dữ liệu realtime từ MT5 về SQL
│   └── backtest/      # Script backtest, xuất file, show chart
│       ├── export_combo_backtest.py
│       └── backtest_combo.py
├── src/
│   ├── utils/         # Tiện ích dùng chung (time_helper.py, ...)
│   ├── fetchers/      # Lấy dữ liệu từ nguồn ngoài (mt5_fetcher.py, tv_fetcher.py, ...)
│   ├── connectors/    # Kết nối hệ thống ngoài (SQL, MT5, TV, ...)
│   ├── backtest/      # Core backtest, metrics, result
│   ├── indicators/    # Indicator kỹ thuật
│   ├── strategies/    # Chiến lược giao dịch
├── config/
│   ├── config.json
│   ├── database_schema.sql
│   └── stored_procedures.sql
├── requirements.txt
├── README.md
└── .gitignore
```


## Chạy các script

- **Khởi tạo database:**
  ```bash
  python -m apps.database.setup_database
  ```
- **Lấy dữ liệu lịch sử từ MT5:**
  ```bash
  python -m apps.database.historical_mt5_to_sql
  ```
- **Chạy realtime fetch dữ liệu từ MT5:**
  ```bash
  python -m apps.database.realtime_mt5_to_sql
  ```
- **Xóa dữ liệu các bảng data:**
  ```bash
  python -m apps.database.clear_data_tables
  ```

## Kích hoạt Symbol/Timeframe để lấy dữ liệu

Để script chỉ lấy dữ liệu cho các symbol và timeframe đang được kích hoạt (active), bạn cần đảm bảo các symbol và timeframe mong muốn có cột `Active = 1` trong database.

- **Kích hoạt Symbol:**
  ```sql
  UPDATE table_symbols SET Active = 1 WHERE Symbol = 'EURUSD';
  -- Hoặc tắt symbol:
  UPDATE table_symbols SET Active = 0 WHERE Symbol = 'EURUSD';
  ```
- **Kích hoạt Timeframe:**
  ```sql
  UPDATE table_timeframes SET Active = 1 WHERE Name = 'm5';
  -- Hoặc tắt timeframe:
  UPDATE table_timeframes SET Active = 0 WHERE Name = 'm5';
  ```

Chỉ các symbol và timeframe có `Active = 1` mới được script lấy dữ liệu khi chạy các script như:
```bash
python -m apps.database.realtime_mt5_to_sql
python -m apps.database.historical_mt5_to_sql
```

## Yêu cầu môi trường
- Python >= 3.8
- SQL Server (hoặc tương thích)
- MetaTrader5 (nếu dùng MT5)
- **Thư viện:**
  - MetaTrader5
  - pandas
  - sqlalchemy
  - pytz (nếu dùng timezone chuẩn DST)
  - pyodbc


## Mở rộng
- Nếu thêm nhóm chức năng mới, hãy tạo thư mục con tương ứng trong `apps/`.
- Nếu có hàm tiện ích dùng chung, hãy đặt vào `src/utils/`.

