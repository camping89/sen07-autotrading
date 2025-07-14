# Order Generation Module

## Tổng quan
Order Generation Module là central intelligence của hệ thống phân tích processed market data để identify trading opportunities và create specific trade orders. Module này implement vertical slices cho market analysis, strategy evaluation, order creation và risk management.

## Development Timeline
**Thời gian**: Tuần 6-8

## Data Flow Architecture
```
Redis Market Data → Analysis Algorithms → Strategy Rules → Risk Validation → Order Generation
     ↓
Trading Signals → Rules Engine → Core Orchestrator → Trading Orders Manager → Redis Queue
```

## Implementation Todo List

### Tuần 6: Market Analysis & Signal Generation

#### [ ] 1. Market Analysis Vertical Slice
- [ ] Tạo `AnalyzeMarketData` command và handler
- [ ] Implement multi-market data consumption từ Redis
- [ ] Thêm pattern recognition algorithms
- [ ] Tạo trend analysis và momentum detection
- [ ] Implement support/resistance level detection
- [ ] Thêm market volatility analysis

#### [ ] 2. Framework Tạo Tín hiệu
- [ ] Tạo interface ISignalGenerator
- [ ] Triển khai tín hiệu giao cắt trung bình động
- [ ] Thêm phát hiện tín hiệu RSI divergence
- [ ] Tạo tín hiệu MACD
- [ ] Triển khai tín hiệu Bollinger Bands squeeze
- [ ] Thêm xác nhận tín hiệu dựa trên volume

#### [ ] 3. Multi-Market Analytics Engine
- [ ] Tạo phân tích correlation giữa các cặp tiền tệ
- [ ] Triển khai validation tín hiệu cross-market
- [ ] Thêm phân tích tình cảm thị trường
- [ ] Tạo hệ thống chấm điểm độ mạnh tín hiệu
- [ ] Triển khai lọc và xếp hạng tín hiệu
- [ ] Thêm persistence và tracking tín hiệu

#### [ ] 4. Quản lý Tín hiệu
- [ ] Tạo entity TradingSignal và repository
- [ ] Triển khai lưu trữ tín hiệu trong Redis với TTL
- [ ] Thêm tracking lịch sử tín hiệu
- [ ] Tạo metric hiệu suất tín hiệu
- [ ] Triển khai xử lý hết hạn tín hiệu
- [ ] Thêm giải quyết xung đột tín hiệu

### Tuần 7: Strategy Engine & Đánh giá Quy tắc

#### [ ] 5. Vertical Slice Đánh giá Chiến lược
- [ ] Tạo command và handler `EvaluateStrategy`
- [ ] Triển khai framework định nghĩa chiến lược
- [ ] Thêm cấu hình chiến lược dựa trên JSON
- [ ] Tạo engine biên dịch quy tắc chiến lược
- [ ] Triển khai loading chiến lược động
- [ ] Thêm tracking hiệu suất chiến lược

#### [ ] 6. Trading Rules Engine
- [ ] Tạo interface ITradingRule
- [ ] Triển khai pipeline đánh giá quy tắc
- [ ] Thêm builder điều kiện quy tắc
- [ ] Tạo định nghĩa hành động quy tắc
- [ ] Triển khai độ ưu tiên và sắp xếp quy tắc
- [ ] Thêm validation và testing quy tắc

#### [ ] 7. Template Chiến lược
- [ ] Tạo template chiến lược trung bình động
- [ ] Triển khai template chiến lược scalping
- [ ] Thêm template chiến lược swing trading
- [ ] Tạo template chiến lược breakout
- [ ] Triển khai template chiến lược grid trading
- [ ] Thêm template chiến lược arbitrage

#### [ ] 8. Framework Backtesting
- [ ] Tạo engine backtesting
- [ ] Triển khai replay dữ liệu lịch sử
- [ ] Thêm tính toán metric hiệu suất
- [ ] Tạo báo cáo backtesting
- [ ] Triển khai tối ưu chiến lược
- [ ] Thêm walk-forward analysis

### Tuần 8: Tạo lệnh & Quản lý Rủi ro

#### [ ] 9. Vertical Slice Tạo lệnh
- [ ] Tạo command và handler `GenerateOrder`
- [ ] Triển khai tạo lệnh từ tín hiệu
- [ ] Thêm thuật toán sizing lệnh
- [ ] Tạo tính toán stop-loss và take-profit
- [ ] Triển khai tối ưu timing lệnh
- [ ] Thêm logic validation lệnh

#### [ ] 10. Core Orchestrator
- [ ] Tạo engine ra quyết định trung tâm
- [ ] Triển khai chuyển đổi tín hiệu thành lệnh
- [ ] Thêm quản lý độ ưu tiên lệnh
- [ ] Tạo batching và tối ưu lệnh
- [ ] Triển khai giải quyết xung đột lệnh
- [ ] Thêm lập lịch và timing lệnh

#### [ ] 11. Vertical Slice Quản lý Rủi ro
- [ ] Tạo command và handler `ValidateRisk`
- [ ] Triển khai sizing vị thế dựa trên rủi ro
- [ ] Thêm bảo vệ maximum drawdown
- [ ] Tạo quản lý rủi ro correlation
- [ ] Triển khai giới hạn exposure cho mỗi symbol
- [ ] Thêm đánh giá rủi ro portfolio

#### [ ] 12. Trading Orders Manager
- [ ] Tạo validation lệnh toàn diện
- [ ] Triển khai kiểm tra tham số rủi ro
- [ ] Thêm thực thi giới hạn vị thế
- [ ] Tạo xử lý sửa đổi lệnh
- [ ] Triển khai logic hủy lệnh
- [ ] Thêm audit trail lệnh

## Thành phần Chính

### Interface Tạo Tín hiệu
```csharp
public interface ISignalGenerator
{
    Task<IEnumerable<TradingSignal>> GenerateSignalsAsync(string symbol, CancellationToken cancellationToken);
    SignalType SupportedSignalType { get; }
    bool IsEnabled { get; }
}

public interface ITradingRule
{
    Task<bool> EvaluateAsync(TradingSignal signal, MarketContext context);
    string RuleName { get; }
    int Priority { get; }
}
```

### Command Vertical Slice
```csharp
// Phân tích Thị trường
public record AnalyzeMarketDataCommand(string Symbol, DateTime From, DateTime To) : IRequest<Result<IEnumerable<TradingSignal>>>;

// Đánh giá Chiến lược
public record EvaluateStrategyCommand(string StrategyId, TradingSignal Signal) : IRequest<Result<TradingDecision>>;

// Tạo lệnh
public record GenerateOrderCommand(TradingDecision Decision, RiskParameters Risk) : IRequest<Result<TradingOrder>>;

// Validation Rủi ro
public record ValidateRiskCommand(TradingOrder Order, Portfolio Portfolio) : IRequest<Result<ValidationResult>>;
```

### Model Domain
```csharp
public class TradingSignal
{
    public string Id { get; set; }
    public string Symbol { get; set; }
    public SignalType Type { get; set; }
    public SignalDirection Direction { get; set; }
    public decimal Strength { get; set; }
    public DateTime Timestamp { get; set; }
    public decimal EntryPrice { get; set; }
    public decimal StopLoss { get; set; }
    public decimal TakeProfit { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}

public class TradingStrategy
{
    public string Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public bool IsEnabled { get; set; }
    public List<TradingRule> Rules { get; set; }
    public RiskParameters RiskParameters { get; set; }
    public StrategyConfiguration Configuration { get; set; }
}

public class TradingOrder
{
    public string Id { get; set; }
    public string Symbol { get; set; }
    public OrderType Type { get; set; }
    public OrderSide Side { get; set; }
    public decimal Quantity { get; set; }
    public decimal Price { get; set; }
    public decimal StopLoss { get; set; }
    public decimal TakeProfit { get; set; }
    public DateTime CreatedAt { get; set; }
    public OrderStatus Status { get; set; }
    public string StrategyId { get; set; }
    public string SignalId { get; set; }
}
```

## Cấu trúc Dữ liệu Redis

### Cache Tín hiệu
```redis
signals:{symbol}:active -> Hash: {signal_id, strength, direction, timestamp}
signals:{symbol}:history -> List: {historical_signals}
signals:global:stats -> Hash: {total_signals, success_rate, avg_strength}
```

### Cache Chiến lược
```redis
strategies:active -> Hash: {strategy_id, enabled, performance}
strategies:{strategy_id}:rules -> List: {rule_definitions}
strategies:{strategy_id}:performance -> Hash: {win_rate, avg_profit, drawdown}
```

### Hàng đợi Lệnh
```redis
orders:pending -> List: {order_json}
orders:processing -> Hash: {order_id, status, timestamp}
orders:completed -> SortedSet: {order_id, completion_time}
```

## Schema Cơ sở dữ liệu

### Bảng TradingSignals
```sql
CREATE TABLE TradingSignals (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Symbol VARCHAR(10) NOT NULL,
    SignalType VARCHAR(50) NOT NULL,
    Direction VARCHAR(10) NOT NULL,
    Strength DECIMAL(5,4) NOT NULL,
    EntryPrice DECIMAL(18,6) NOT NULL,
    StopLoss DECIMAL(18,6),
    TakeProfit DECIMAL(18,6),
    Timestamp DATETIME2 NOT NULL,
    ExpiresAt DATETIME2,
    Metadata NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_TradingSignals_Symbol_Timestamp ON TradingSignals(Symbol, Timestamp);
CREATE INDEX IX_TradingSignals_Type_Direction ON TradingSignals(SignalType, Direction);
```

### Bảng TradingStrategies
```sql
CREATE TABLE TradingStrategies (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Name VARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    IsEnabled BIT DEFAULT 1,
    Configuration NVARCHAR(MAX),
    RiskParameters NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_TradingStrategies_Name ON TradingStrategies(Name);
CREATE INDEX IX_TradingStrategies_IsEnabled ON TradingStrategies(IsEnabled);
```

### Bảng TradingOrders
```sql
CREATE TABLE TradingOrders (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Symbol VARCHAR(10) NOT NULL,
    OrderType VARCHAR(20) NOT NULL,
    Side VARCHAR(10) NOT NULL,
    Quantity DECIMAL(18,6) NOT NULL,
    Price DECIMAL(18,6) NOT NULL,
    StopLoss DECIMAL(18,6),
    TakeProfit DECIMAL(18,6),
    Status VARCHAR(20) NOT NULL,
    StrategyId UNIQUEIDENTIFIER,
    SignalId UNIQUEIDENTIFIER,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_TradingOrders_Symbol_Status ON TradingOrders(Symbol, Status);
CREATE INDEX IX_TradingOrders_StrategyId ON TradingOrders(StrategyId);
CREATE INDEX IX_TradingOrders_CreatedAt ON TradingOrders(CreatedAt);
```

### Bảng RiskParameters
```sql
CREATE TABLE RiskParameters (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    StrategyId UNIQUEIDENTIFIER NOT NULL,
    Symbol VARCHAR(10),
    MaxPositionSize DECIMAL(18,6),
    MaxDailyLoss DECIMAL(18,6),
    MaxDrawdown DECIMAL(5,4),
    RiskPerTrade DECIMAL(5,4),
    MaxCorrelatedPositions INT,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_RiskParameters_StrategyId ON RiskParameters(StrategyId);
```

## Cấu hình

### Cài đặt Chiến lược
```json
{
  "OrderGeneration": {
    "MaxConcurrentSignals": 100,
    "SignalExpirationMinutes": 30,
    "MinSignalStrength": 0.6,
    "MaxOrdersPerSymbol": 3
  },
  "RiskManagement": {
    "MaxPortfolioExposure": 500000,
    "MaxDrawdownPercent": 5.0,
    "MaxDailyLossPercent": 2.0,
    "MaxPositionsPerSymbol": 2,
    "MaxCorrelatedPositions": 5
  },
  "BacktestingEngine": {
    "DefaultCommission": 0.0001,
    "DefaultSpread": 0.00015,
    "SlippagePercent": 0.1
  }
}
```

### Ví dụ Template Chiến lược
```json
{
  "id": "ma-crossover-strategy",
  "name": "Moving Average Crossover",
  "description": "Chiến lược giao cắt trung bình động đơn giản",
  "rules": [
    {
      "name": "MA_CROSSOVER_BUY",
      "condition": "SMA(20) > SMA(50) AND Previous(SMA(20)) <= Previous(SMA(50))",
      "action": "GENERATE_BUY_SIGNAL",
      "priority": 1
    },
    {
      "name": "MA_CROSSOVER_SELL",
      "condition": "SMA(20) < SMA(50) AND Previous(SMA(20)) >= Previous(SMA(50))",
      "action": "GENERATE_SELL_SIGNAL",
      "priority": 1
    }
  ],
  "riskParameters": {
    "maxPositionSize": 10000,
    "stopLossPercent": 2.0,
    "takeProfitPercent": 4.0,
    "riskPerTrade": 1.0
  }
}
```

## Chiến lược Testing

### Unit Test
- [ ] Thuật toán tạo tín hiệu
- [ ] Đánh giá quy tắc chiến lược
- [ ] Logic tạo lệnh
- [ ] Tính toán quản lý rủi ro
- [ ] Độ chính xác nhận dạng mẫu
- [ ] Tính toán metric hiệu suất

### Integration Test
- [ ] Caching tín hiệu Redis
- [ ] Persistence database
- [ ] Loading và thực thi chiến lược
- [ ] Tạo lệnh end-to-end
- [ ] Framework backtesting
- [ ] Scenario validation rủi ro

### Performance Test
- [ ] Tốc độ tạo tín hiệu
- [ ] Độ trễ đánh giá chiến lược
- [ ] Throughput xử lý lệnh
- [ ] Tối ưu sử dụng memory
- [ ] Hiệu suất query database
- [ ] Hiệu quả operation Redis

## Tiêu chí Thành công
- [ ] Tạo tín hiệu giao dịch với độ chính xác >70%
- [ ] Xử lý 1000+ tín hiệu/giây
- [ ] Độ trễ đánh giá chiến lược <10ms
- [ ] Tạo lệnh <50ms end-to-end
- [ ] Validation rủi ro ngăn chặn tất cả vi phạm giới hạn
- [ ] Framework backtesting validation chiến lược
- [ ] Tất cả unit và integration test pass
- [ ] Benchmark hiệu suất đạt yêu cầu