# Order Fulfillment Module

## Tổng quan
Order Fulfillment Module quản lý execution của trade orders trên live market thông qua broker APIs. Module này implement vertical slices cho broker communication, order execution, position management và real-time feedback processing.

## Development Timeline
**Thời gian**: Tuần 9-10

## Data Flow Architecture
```
Redis Order Queue → Broker APIs → Execution Results → Position Updates → Feedback Loop
     ↓
Order Validation → Broker Communication → Order Tracking → Position Management → Redis + Database
```

## Implementation Todo List

### Tuần 9: Broker Integration & Order Execution

#### [ ] 1. Broker Communication Vertical Slice
- [ ] Tạo `ExecuteOrder` command và handler
- [ ] Implement IBrokerProvider interface
- [ ] Thêm OANDA broker integration
- [ ] Implement Interactive Brokers TWS API
- [ ] Thêm MetaTrader 5 broker support
- [ ] Tạo broker factory pattern

#### [ ] 2. Triển khai API Nhà môi giới
- [ ] Tạo OANDA REST API client
- [ ] Triển khai OANDA streaming API
- [ ] Thêm kết nối socket Interactive Brokers
- [ ] Tạo bridge Python MetaTrader 5
- [ ] Triển khai xử lý authentication nhà môi giới
- [ ] Thêm rate limiting và throttling API

#### [ ] 3. Engine Thực thi Lệnh
- [ ] Tạo pipeline thực thi lệnh
- [ ] Triển khai validation lệnh trước khi thực thi
- [ ] Thêm chuyển đổi lệnh cho định dạng nhà môi giới
- [ ] Tạo logic retry thực thi
- [ ] Triển khai xử lý sửa đổi lệnh
- [ ] Thêm hỗ trợ hủy lệnh

#### [ ] 4. Quản lý Lệnh Thời gian thực
- [ ] Tạo hệ thống theo dõi trạng thái lệnh
- [ ] Triển khai state machine lệnh
- [ ] Thêm quản lý vòng đời lệnh
- [ ] Tạo xử lý sự kiện lệnh
- [ ] Triển khai xử lý timeout lệnh
- [ ] Thêm giải quyết xung đột lệnh

### Tuần 10: Quản lý Vị thế & Hệ thống Phản hồi

#### [ ] 5. Vertical Slice Theo dõi Lệnh
- [ ] Tạo command và handler `TrackOrderStatus`
- [ ] Triển khai giám sát lệnh thời gian thực
- [ ] Thêm cập nhật trạng thái lệnh từ nhà môi giới
- [ ] Tạo thông báo fill lệnh
- [ ] Triển khai xử lý fill một phần
- [ ] Thêm xử lý từ chối lệnh

#### [ ] 6. Vertical Slice Quản lý Vị thế
- [ ] Tạo command và handler `ManagePositions`
- [ ] Triển khai theo dõi vị thế thời gian thực
- [ ] Thêm tính toán P&L vị thế
- [ ] Tạo giám sát rủi ro vị thế
- [ ] Triển khai tổng hợp vị thế
- [ ] Thêm reconciliation vị thế

#### [ ] 7. Giám sát Chất lượng Thực thi
- [ ] Tạo hệ thống đo lường slippage
- [ ] Triển khai theo dõi thời gian thực thi
- [ ] Thêm phân tích giá fill
- [ ] Tạo metric chất lượng thực thi
- [ ] Triển khai so sánh hiệu suất nhà môi giới
- [ ] Thêm phân tích chi phí thực thi

#### [ ] 8. Kiểm soát Rủi ro & Circuit Breaker
- [ ] Tạo giám sát rủi ro thời gian thực
- [ ] Triển khai thực thi giới hạn vị thế
- [ ] Thêm kiểm tra giới hạn exposure
- [ ] Tạo trigger stop-loss tự động
- [ ] Triển khai đóng vị thế khẩn cấp
- [ ] Thêm hệ thống cảnh báo rủi ro

#### [ ] 9. Phản hồi & Báo cáo
- [ ] Tạo hệ thống phản hồi thực thi
- [ ] Triển khai xử lý xác nhận giao dịch
- [ ] Thêm báo cáo hiệu suất
- [ ] Tạo báo cáo vị thế
- [ ] Triển khai tạo audit trail
- [ ] Thêm báo cáo tuân thủ

#### [ ] 10. Xử lý Lỗi & Khôi phục
- [ ] Tạo giám sát kết nối nhà môi giới
- [ ] Triển khai failover kết nối
- [ ] Thêm thủ tục khôi phục lệnh
- [ ] Tạo hệ thống phân loại lỗi
- [ ] Triển khai khôi phục lỗi tự động
- [ ] Thêm cảnh báo can thiệp thủ công

## Thành phần Chính

### Interface Tích hợp Nhà môi giới
```csharp
public interface IBrokerProvider
{
    Task<ExecutionResult> ExecuteOrderAsync(TradingOrder order, CancellationToken cancellationToken);
    Task<OrderStatus> GetOrderStatusAsync(string orderId, CancellationToken cancellationToken);
    Task<IEnumerable<Position>> GetPositionsAsync(CancellationToken cancellationToken);
    Task<bool> CancelOrderAsync(string orderId, CancellationToken cancellationToken);
    Task<bool> ModifyOrderAsync(string orderId, ModifyOrderRequest request, CancellationToken cancellationToken);
    string BrokerName { get; }
    bool IsConnected { get; }
}

public interface IPositionManager
{
    Task<Position> GetPositionAsync(string symbol);
    Task<IEnumerable<Position>> GetAllPositionsAsync();
    Task UpdatePositionAsync(Position position);
    Task<decimal> CalculateUnrealizedPnLAsync(string symbol);
    Task<decimal> CalculateRealizedPnLAsync(string symbol, DateTime from, DateTime to);
}
```

### Command Vertical Slice
```csharp
// Thực thi Lệnh
public record ExecuteOrderCommand(TradingOrder Order, string BrokerName) : IRequest<Result<ExecutionResult>>;

// Theo dõi Lệnh
public record TrackOrderStatusCommand(string OrderId, string BrokerName) : IRequest<Result<OrderStatusUpdate>>;

// Quản lý Vị thế
public record ManagePositionsCommand(string Symbol) : IRequest<Result<Position>>;

// Giám sát Rủi ro
public record MonitorRiskCommand(Portfolio Portfolio) : IRequest<Result<RiskAssessment>>;
```

### Model Domain
```csharp
public class ExecutionResult
{
    public string OrderId { get; set; }
    public string BrokerOrderId { get; set; }
    public ExecutionStatus Status { get; set; }
    public decimal ExecutedQuantity { get; set; }
    public decimal ExecutedPrice { get; set; }
    public decimal Commission { get; set; }
    public DateTime ExecutionTime { get; set; }
    public string ErrorMessage { get; set; }
    public Dictionary<string, object> BrokerMetadata { get; set; }
}

public class Position
{
    public string Symbol { get; set; }
    public decimal Quantity { get; set; }
    public decimal AveragePrice { get; set; }
    public decimal CurrentPrice { get; set; }
    public decimal UnrealizedPnL { get; set; }
    public decimal RealizedPnL { get; set; }
    public DateTime LastUpdate { get; set; }
    public string BrokerName { get; set; }
    public PositionSide Side { get; set; }
}

public class OrderStatusUpdate
{
    public string OrderId { get; set; }
    public string BrokerOrderId { get; set; }
    public OrderStatus Status { get; set; }
    public decimal FilledQuantity { get; set; }
    public decimal RemainingQuantity { get; set; }
    public decimal AveragePrice { get; set; }
    public DateTime LastUpdate { get; set; }
    public List<Fill> Fills { get; set; }
}

public class Fill
{
    public string Id { get; set; }
    public decimal Quantity { get; set; }
    public decimal Price { get; set; }
    public decimal Commission { get; set; }
    public DateTime Time { get; set; }
}
```

## Cấu trúc Dữ liệu Redis

### Hàng đợi Lệnh
```redis
orders:pending -> List: {order_json}
orders:processing -> Hash: {order_id, broker, status, timestamp}
orders:executed -> SortedSet: {order_id, execution_time}
orders:failed -> List: {order_id, error_message, timestamp}
```

### Cache Vị thế
```redis
positions:{symbol} -> Hash: {quantity, avg_price, current_price, unrealized_pnl}
positions:all -> Hash: {symbol, position_summary}
positions:pnl:total -> String: {total_unrealized_pnl}
```

### Metric Thực thi
```redis
execution:metrics:{broker} -> Hash: {avg_latency, success_rate, slippage}
execution:quality:{symbol} -> Hash: {avg_slippage, execution_time}
```

## Schema Cơ sở dữ liệu

### Bảng Executions
```sql
CREATE TABLE Executions (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    OrderId UNIQUEIDENTIFIER NOT NULL,
    BrokerOrderId VARCHAR(100) NOT NULL,
    Symbol VARCHAR(10) NOT NULL,
    Side VARCHAR(10) NOT NULL,
    Quantity DECIMAL(18,6) NOT NULL,
    ExecutedPrice DECIMAL(18,6) NOT NULL,
    Commission DECIMAL(18,6) NOT NULL,
    ExecutionTime DATETIME2 NOT NULL,
    BrokerName VARCHAR(50) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    Metadata NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE INDEX IX_Executions_OrderId ON Executions(OrderId);
CREATE INDEX IX_Executions_Symbol_ExecutionTime ON Executions(Symbol, ExecutionTime);
CREATE INDEX IX_Executions_BrokerName ON Executions(BrokerName);
```

### Bảng Positions
```sql
CREATE TABLE Positions (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Symbol VARCHAR(10) NOT NULL,
    Quantity DECIMAL(18,6) NOT NULL,
    AveragePrice DECIMAL(18,6) NOT NULL,
    CurrentPrice DECIMAL(18,6) NOT NULL,
    UnrealizedPnL DECIMAL(18,6) NOT NULL,
    RealizedPnL DECIMAL(18,6) NOT NULL,
    BrokerName VARCHAR(50) NOT NULL,
    Side VARCHAR(10) NOT NULL,
    LastUpdate DATETIME2 NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE UNIQUE INDEX IX_Positions_Symbol_Broker ON Positions(Symbol, BrokerName);
CREATE INDEX IX_Positions_LastUpdate ON Positions(LastUpdate);
```

### Bảng OrderStatusHistory
```sql
CREATE TABLE OrderStatusHistory (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    OrderId UNIQUEIDENTIFIER NOT NULL,
    BrokerOrderId VARCHAR(100) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FilledQuantity DECIMAL(18,6) NOT NULL,
    RemainingQuantity DECIMAL(18,6) NOT NULL,
    AveragePrice DECIMAL(18,6),
    Timestamp DATETIME2 NOT NULL,
    BrokerName VARCHAR(50) NOT NULL,
    Details NVARCHAR(MAX)
);

CREATE INDEX IX_OrderStatusHistory_OrderId_Timestamp ON OrderStatusHistory(OrderId, Timestamp);
CREATE INDEX IX_OrderStatusHistory_BrokerOrderId ON OrderStatusHistory(BrokerOrderId);
```

### Bảng ExecutionQuality
```sql
CREATE TABLE ExecutionQuality (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    OrderId UNIQUEIDENTIFIER NOT NULL,
    Symbol VARCHAR(10) NOT NULL,
    BrokerName VARCHAR(50) NOT NULL,
    ExpectedPrice DECIMAL(18,6) NOT NULL,
    ExecutedPrice DECIMAL(18,6) NOT NULL,
    Slippage DECIMAL(18,6) NOT NULL,
    ExecutionLatency INT NOT NULL,
    Commission DECIMAL(18,6) NOT NULL,
    ExecutionTime DATETIME2 NOT NULL,
    QualityScore DECIMAL(5,4)
);

CREATE INDEX IX_ExecutionQuality_Symbol_BrokerName ON ExecutionQuality(Symbol, BrokerName);
CREATE INDEX IX_ExecutionQuality_ExecutionTime ON ExecutionQuality(ExecutionTime);
```

## Cấu hình

### Cài đặt Nhà môi giới
```json
{
  "Brokers": {
    "OANDA": {
      "ApiKey": "your-api-key",
      "AccountId": "your-account-id",
      "Environment": "practice",
      "BaseUrl": "https://api-fxpractice.oanda.com",
      "MaxOrdersPerSecond": 10,
      "TimeoutSeconds": 30
    },
    "InteractiveBrokers": {
      "Host": "127.0.0.1",
      "Port": 7497,
      "ClientId": 1,
      "ConnectionTimeout": 30,
      "MaxOrdersPerSecond": 5
    }
  },
  "ExecutionSettings": {
    "DefaultSlippageTolerancePercent": 0.1,
    "MaxExecutionTimeSeconds": 60,
    "RetryAttempts": 3,
    "RetryDelaySeconds": 1
  },
  "RiskSettings": {
    "MaxPositionValue": 50000,
    "MaxDailyLoss": 5000,
    "MaxOpenPositions": 20,
    "EmergencyStopPercent": 10.0
  }
}
```

## Chiến lược Xử lý Lỗi

### Lỗi Kết nối
```csharp
public class BrokerConnectionStrategy
{
    private readonly IRetryPolicy _retryPolicy;
    private readonly ICircuitBreaker _circuitBreaker;
    
    public async Task<T> ExecuteWithRetryAsync<T>(Func<Task<T>> operation)
    {
        return await _retryPolicy.ExecuteAsync(async () =>
        {
            return await _circuitBreaker.ExecuteAsync(operation);
        });
    }
}
```

### Xử lý Từ chối Lệnh
```csharp
public class OrderRejectionHandler
{
    public async Task HandleRejectionAsync(OrderRejection rejection)
    {
        switch (rejection.ReasonCode)
        {
            case "INSUFFICIENT_MARGIN":
                await _riskManager.ReducePositionSizeAsync(rejection.OrderId);
                break;
            case "INVALID_PRICE":
                await _orderManager.UpdateOrderPriceAsync(rejection.OrderId);
                break;
            case "MARKET_CLOSED":
                await _orderManager.ScheduleOrderAsync(rejection.OrderId);
                break;
        }
    }
}
```

## Chiến lược Testing

### Unit Test
- [ ] Triển khai API nhà môi giới
- [ ] Logic thực thi lệnh
- [ ] Độ chính xác tính toán vị thế
- [ ] Scenario xử lý lỗi
- [ ] Cơ chế kiểm soát rủi ro
- [ ] Tính toán metric hiệu suất

### Integration Test
- [ ] Kết nối API nhà môi giới
- [ ] Thực thi lệnh end-to-end
- [ ] Đồng bộ vị thế
- [ ] Thủ tục khôi phục lỗi
- [ ] Benchmark hiệu suất
- [ ] Scenario failover

### Load Test
- [ ] Thực thi lệnh đồng thời
- [ ] Xử lý lệnh tần suất cao
- [ ] Hiệu suất cập nhật vị thế
- [ ] Sử dụng memory dưới tải
- [ ] Tính ổn định kết nối
- [ ] Tỷ lệ lỗi dưới stress

## Giám sát & Cảnh báo

### Metric Chính
- [ ] Độ trễ thực thi lệnh
- [ ] Tỷ lệ phần trăm fill
- [ ] Đo lường slippage
- [ ] Thời gian hoạt động kết nối
- [ ] Tỷ lệ lỗi theo nhà môi giới
- [ ] Độ chính xác vị thế

### Điều kiện Cảnh báo
- [ ] Độ trễ thực thi > 5 giây
- [ ] Tỷ lệ fill < 95%
- [ ] Slippage > 0.5%
- [ ] Thời gian ngắt kết nối > 30 giây
- [ ] Tỷ lệ lỗi > 5%
- [ ] Phát hiện không khớp vị thế

## Tiêu chí Thành công
- [ ] Thực thi lệnh với độ trễ trung bình <2 giây
- [ ] Đạt tỷ lệ fill lệnh >98%
- [ ] Duy trì slippage trung bình <0.2%
- [ ] 99.9% thời gian kết nối nhà môi giới
- [ ] Theo dõi vị thế chính xác (100% reconciliation)
- [ ] Xử lý lỗi và khôi phục toàn diện
- [ ] Tất cả unit và integration test pass
- [ ] Benchmark hiệu suất đạt yêu cầu