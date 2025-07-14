# Data Provider Module

## Tổng quan
Data Provider Module xử lý toàn bộ lifecycle của market data từ external sources đến processed indicators. Module này implement vertical slices cho data ingestion, candle generation và technical indicator calculation.

## Development Timeline
**Thời gian**: Tuần 3-5

## Data Flow Architecture
```
External APIs → Redis Cache → Background Processor → Database Persistence
     ↓
Raw Tick Data → Candle Generation → Technical Indicators → Redis + Database
```

## Implementation Todo List

### Tuần 3: External Data Ingestion

#### [ ] 1. Data Source Integration
- [ ] Tạo IDataProvider interface cho external APIs
- [ ] Implement Alpha Vantage data provider
- [ ] Implement Yahoo Finance data provider
- [ ] Thêm Polygon.io data provider (backup)
- [ ] Tạo data provider factory pattern
- [ ] Cấu hình rate limiting và API key management

#### [ ] 2. Data Ingestion Vertical Slice
- [ ] Tạo `IngestMarketData` command và handler
- [ ] Implement real-time data polling service
- [ ] Thêm data validation và normalization
- [ ] Tạo market data models và DTOs
- [ ] Implement error handling và retry logic
- [ ] Thêm data quality checks và anomaly detection

#### [ ] 3. Data Storage Foundation
- [ ] Tạo MarketData entity và configuration
- [ ] Implement tick data repository
- [ ] Thêm bulk insert operations cho high-throughput
- [ ] Tạo database indexes cho performance
- [ ] Thêm data retention policies
- [ ] Implement data compression strategies

#### [ ] 4. Redis Integration cho Real-time Data
- [ ] Tạo Redis market data service
- [ ] Implement real-time data caching
- [ ] Thêm Redis pub/sub cho data distribution
- [ ] Cấu hình Redis key expiration policies
- [ ] Tạo Redis data structures cho tick data
- [ ] Thêm Redis monitoring và health checks

### Tuần 4: Candle Generation & Processing

#### [ ] 5. Candle Generation Vertical Slice
- [ ] Tạo `GenerateCandles` command và handler
- [ ] Implement OHLCV calculation từ tick data
- [ ] Thêm multiple timeframe support (1m, 5m, 15m, 1h, 4h, 1d)
- [ ] Tạo Candle entity và repository
- [ ] Implement real-time candle updates
- [ ] Thêm candle aggregation algorithms

#### [ ] 6. Background Processing Services
- [ ] Tạo Quartz.NET jobs cho candle generation
- [ ] Implement scheduled data processing
- [ ] Thêm job monitoring và error handling
- [ ] Tạo job configuration và scheduling
- [ ] Thêm job persistence và recovery
- [ ] Implement parallel processing cho multiple symbols

#### [ ] 7. Đồng bộ Dữ liệu
- [ ] Tạo dịch vụ đồng bộ dữ liệu
- [ ] Triển khai phát hiện và điền gap
- [ ] Thêm kiểm tra tính nhất quán dữ liệu
- [ ] Tạo quá trình backfill dữ liệu lịch sử
- [ ] Thêm reconciliation dữ liệu giữa các nguồn
- [ ] Triển khai versioning và audit trail dữ liệu

#### [ ] 8. Tối ưu Hiệu suất
- [ ] Tối ưu database query với index
- [ ] Triển khai batch processing cho bulk operation
- [ ] Thêm cấu trúc dữ liệu hiệu quả về memory
- [ ] Tạo nén và lưu trữ dữ liệu
- [ ] Thêm chiến lược caching query
- [ ] Triển khai tối ưu connection pooling

### Tuần 5: Chỉ báo Kỹ thuật & Xử lý Nâng cao

#### [ ] 9. Vertical Slice Chỉ báo Kỹ thuật
- [ ] Tạo command và handler `CalculateIndicators`
- [ ] Triển khai Simple Moving Average (SMA)
- [ ] Triển khai Exponential Moving Average (EMA)
- [ ] Thêm Relative Strength Index (RSI)
- [ ] Thêm Moving Average Convergence Divergence (MACD)
- [ ] Thêm tính toán Bollinger Bands
- [ ] Tạo framework tính toán chỉ báo

#### [ ] 10. Phân tích Kỹ thuật Nâng cao
- [ ] Triển khai Stochastic Oscillator
- [ ] Thêm Average True Range (ATR)
- [ ] Tạo mức Fibonacci retracement
- [ ] Thêm phát hiện support và resistance
- [ ] Triển khai chỉ báo volume
- [ ] Thêm hệ thống plugin chỉ báo tùy chỉnh

#### [ ] 11. Chất lượng & Validation Dữ liệu
- [ ] Tạo metric chất lượng dữ liệu
- [ ] Triển khai phát hiện outlier
- [ ] Thêm kiểm tra tính đầy đủ dữ liệu
- [ ] Tạo validation tính chính xác dữ liệu
- [ ] Thêm monitoring độ tươi dữ liệu
- [ ] Triển khai báo cáo chất lượng dữ liệu

#### [ ] 12. Pipeline Xử lý Thời gian thực
- [ ] Tạo pipeline xử lý dữ liệu thời gian thực
- [ ] Triển khai streaming data processing
- [ ] Thêm kiến trúc event-driven
- [ ] Tạo dịch vụ chuyển đổi dữ liệu
- [ ] Thêm cập nhật chỉ báo thời gian thực
- [ ] Triển khai phân phối dữ liệu độ trễ thấp

## Thành phần Chính

### Interface Nhà cung cấp Dữ liệu
```csharp
public interface IDataProvider
{
    Task<IEnumerable<TickData>> GetTickDataAsync(string symbol, DateTime from, DateTime to);
    Task<IEnumerable<TickData>> GetRealTimeDataAsync(string symbol);
    Task<bool> IsAvailableAsync();
}
```

### Command Vertical Slice
```csharp
// Tiếp nhận Dữ liệu
public record IngestMarketDataCommand(string Symbol, DateTime From, DateTime To) : IRequest<Result>;

// Tạo Candle
public record GenerateCandlesCommand(string Symbol, TimeFrame TimeFrame, DateTime From, DateTime To) : IRequest<Result>;

// Chỉ báo Kỹ thuật
public record CalculateIndicatorsCommand(string Symbol, IndicatorType Type, int Period) : IRequest<Result>;
```

### Model Dữ liệu
```csharp
public class TickData
{
    public DateTime Timestamp { get; set; }
    public string Symbol { get; set; }
    public decimal Bid { get; set; }
    public decimal Ask { get; set; }
    public decimal Volume { get; set; }
}

public class CandleData
{
    public DateTime Timestamp { get; set; }
    public string Symbol { get; set; }
    public TimeFrame TimeFrame { get; set; }
    public decimal Open { get; set; }
    public decimal High { get; set; }
    public decimal Low { get; set; }
    public decimal Close { get; set; }
    public decimal Volume { get; set; }
}
```

## Cấu trúc Dữ liệu Redis

### Cache Dữ liệu Thị trường
```redis
market:data:{symbol}:tick -> Hash: {timestamp, bid, ask, volume}
market:data:{symbol}:candles:{timeframe} -> SortedSet: {timestamp, ohlcv}
market:indicators:{symbol}:{indicator} -> Hash: {timestamp, value}
```

### Kênh Pub/Sub
```redis
dp:tick-data -> Cập nhật tick thời gian thực
dp:candles -> Thông báo candle mới
dp:indicators -> Cập nhật chỉ báo kỹ thuật
```

## Schema Cơ sở dữ liệu

### Bảng MarketData
```sql
CREATE TABLE MarketData (
    Id BIGINT IDENTITY(1,1) PRIMARY KEY,
    Symbol VARCHAR(10) NOT NULL,
    Timestamp DATETIME2 NOT NULL,
    Bid DECIMAL(18,6) NOT NULL,
    Ask DECIMAL(18,6) NOT NULL,
    Volume DECIMAL(18,6) NOT NULL,
    DataSource VARCHAR(50) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_MarketData_Symbol_Timestamp ON MarketData(Symbol, Timestamp);
CREATE INDEX IX_MarketData_Timestamp ON MarketData(Timestamp);
```

### Bảng Candles
```sql
CREATE TABLE Candles (
    Id BIGINT IDENTITY(1,1) PRIMARY KEY,
    Symbol VARCHAR(10) NOT NULL,
    TimeFrame VARCHAR(10) NOT NULL,
    Timestamp DATETIME2 NOT NULL,
    Open DECIMAL(18,6) NOT NULL,
    High DECIMAL(18,6) NOT NULL,
    Low DECIMAL(18,6) NOT NULL,
    Close DECIMAL(18,6) NOT NULL,
    Volume DECIMAL(18,6) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE UNIQUE INDEX IX_Candles_Symbol_TimeFrame_Timestamp ON Candles(Symbol, TimeFrame, Timestamp);
```

### Bảng TechnicalIndicators
```sql
CREATE TABLE TechnicalIndicators (
    Id BIGINT IDENTITY(1,1) PRIMARY KEY,
    Symbol VARCHAR(10) NOT NULL,
    IndicatorType VARCHAR(50) NOT NULL,
    Period INT NOT NULL,
    Timestamp DATETIME2 NOT NULL,
    Value DECIMAL(18,6) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_TechnicalIndicators_Symbol_Type_Timestamp ON TechnicalIndicators(Symbol, IndicatorType, Timestamp);
```

## Cấu hình

### Cài đặt Nhà cung cấp Dữ liệu
```json
{
  "DataProviders": {
    "AlphaVantage": {
      "ApiKey": "your-api-key",
      "BaseUrl": "https://www.alphavantage.co/query",
      "RateLimit": 5,
      "RetryCount": 3
    },
    "YahooFinance": {
      "BaseUrl": "https://query1.finance.yahoo.com/v8/finance/chart",
      "RateLimit": 2000,
      "RetryCount": 2
    }
  },
  "Processing": {
    "BatchSize": 1000,
    "ProcessingInterval": "00:00:01",
    "MaxRetries": 3,
    "TimeoutSeconds": 30
  }
}
```

## Chiến lược Testing

### Unit Test
- [ ] Triển khai nhà cung cấp dữ liệu
- [ ] Thuật toán tạo candle
- [ ] Tính toán chỉ báo kỹ thuật
- [ ] Logic validation dữ liệu
- [ ] Operation Redis
- [ ] Operation Database

### Integration Test
- [ ] Kết nối API bên ngoài
- [ ] Tích hợp database
- [ ] Tích hợp Redis
- [ ] Luồng dữ liệu end-to-end
- [ ] Benchmark hiệu suất
- [ ] Scenario xử lý lỗi

## Tiêu chí Thành công
- [ ] Tiếp nhận thành công dữ liệu thời gian thực từ nhiều nguồn
- [ ] Tạo candle OHLCV chính xác cho tất cả timeframe
- [ ] Tính toán chỉ báo kỹ thuật chính xác
- [ ] Đạt độ trễ dưới 100ms cho xử lý dữ liệu
- [ ] Xử lý 10,000+ tick/giây cho mỗi symbol
- [ ] 99.9% uptime cho tiếp nhận dữ liệu
- [ ] Tất cả unit và integration test pass
- [ ] Benchmark hiệu suất đạt yêu cầu