# Foundation & Infrastructure Module

## Tổng quan
Thiết lập các components architecture nền tảng và infrastructure cho Hệ thống Giao dịch SEN. Module này tập trung vào việc thiết lập core project structure, database configuration, Redis integration và các essential architecture patterns.

## Development Timeline
**Thời gian**: Tuần 1-2

## Implementation Todo List

### Tuần 1: Project Structure & Core Setup

#### [ ] 1. Solution Structure
- [ ] Tạo .NET 8 solution với vertical slice architecture
- [ ] Thiết lập project references và dependencies
- [ ] Cấu hình NuGet packages cho tất cả projects
- [ ] Thiết lập folder structure cho vertical slices
- [ ] Tạo shared contracts và interfaces

#### [ ] 2. Database Foundation
- [ ] Thiết kế database schema cho market data storage
- [ ] Tạo Entity Framework Core models cho core entities
- [ ] Thiết lập database context với proper configurations
- [ ] Implement database migrations cho initial schema
- [ ] Cấu hình connection strings và database options
- [ ] Thêm database health checks

#### [ ] 3. Redis Integration
- [ ] Thiết lập Redis connection và configuration
- [ ] Tạo Redis service interfaces và implementations
- [ ] Implement Redis pub/sub cho inter-module communication
- [ ] Cấu hình Redis caching strategies
- [ ] Thêm Redis health checks và monitoring
- [ ] Tạo Redis key naming conventions

#### [ ] 4. Core Architecture Components
- [ ] Thiết lập MediatR cho vertical slice communication
- [ ] Tạo base classes cho commands, queries, và handlers
- [ ] Implement dependency injection configuration
- [ ] Thiết lập AutoMapper cho object mapping
- [ ] Tạo common result và error handling patterns
- [ ] Thêm logging infrastructure với Serilog

### Tuần 2: Infrastructure Services & Configuration

#### [ ] 5. Configuration Management
- [ ] Tạo strongly-typed configuration classes
- [ ] Implement configuration validation
- [ ] Thiết lập environment-specific configurations
- [ ] Tạo configuration cho trading parameters
- [ ] Thêm secrets management cho API keys
- [ ] Cấu hình options pattern cho tất cả services

#### [ ] 6. Background Services Framework
- [ ] Thiết lập Quartz.NET cho scheduled tasks
- [ ] Tạo base classes cho background workers
- [ ] Implement job scheduling infrastructure
- [ ] Thêm job monitoring và error handling
- [ ] Cấu hình job persistence và clustering
- [ ] Tạo job management interfaces

#### [ ] 7. API Infrastructure
- [ ] Thiết lập ASP.NET Core minimal APIs
- [ ] Cấu hình HTTP client factory với Polly
- [ ] Implement API versioning và documentation
- [ ] Thêm request/response logging middleware
- [ ] Cấu hình CORS và security headers
- [ ] Thiết lập OpenAPI/Swagger documentation

#### [ ] 8. Data Access Layer
- [ ] Tạo repository pattern interfaces
- [ ] Implement Entity Framework repositories
- [ ] Thiết lập Dapper cho performance-critical queries
- [ ] Tạo unit of work pattern
- [ ] Thêm database transaction management
- [ ] Implement audit trail functionality

#### [ ] 9. Testing Infrastructure
- [ ] Thiết lập xUnit test project structure
- [ ] Tạo test utilities và helpers
- [ ] Thiết lập integration test framework
- [ ] Cấu hình test databases (in-memory/testcontainers)
- [ ] Thêm test data builders và fixtures
- [ ] Tạo mock services cho external dependencies

#### [ ] 10. Monitoring & Observability
- [ ] Thiết lập Application Insights integration
- [ ] Cấu hình structured logging với Serilog
- [ ] Thêm performance counters và metrics
- [ ] Implement health check endpoints
- [ ] Tạo custom telemetry cho trading operations
- [ ] Thiết lập log aggregation và alerting

## Key Database Tables

### Core Tables
- **MarketData**: Raw tick data storage
- **Candles**: OHLCV candlestick data
- **TechnicalIndicators**: Calculated indicator values
- **TradingOrders**: Order information và status
- **Positions**: Current position tracking
- **TradingRules**: Strategy và rule definitions
- **SystemConfiguration**: Application settings

### Audit Tables
- **AuditLog**: System activity tracking
- **TradingHistory**: Historical trading activity
- **SystemEvents**: System event logging

## Redis Key Patterns

### Data Structures
- **market:data:{symbol}**: Real-time market data
- **candles:{symbol}:{timeframe}**: Candlestick data
- **indicators:{symbol}**: Technical indicator values
- **orders:queue**: Order processing queue
- **positions:{symbol}**: Current position data
- **signals:{symbol}**: Trading signals

### Pub/Sub Channels
- **dp:market-data**: Market data updates
- **og:signals**: Trading signals
- **of:executions**: Order executions
- **system:events**: System-wide events

## Configuration Structure

### appsettings.json
```json
{
  "Database": {
    "ConnectionString": "",
    "Provider": "SqlServer|PostgreSQL"
  },
  "Redis": {
    "ConnectionString": "",
    "DefaultDatabase": 0,
    "KeyPrefix": "sen:"
  },
  "Trading": {
    "MaxPositions": 10,
    "MaxExposure": 100000,
    "DefaultRiskPercent": 2.0
  },
  "DataProviders": {
    "Primary": "AlphaVantage",
    "Secondary": "YahooFinance"
  }
}
```

## Package Dependencies

### Core Packages
- Microsoft.EntityFrameworkCore
- StackExchange.Redis
- MediatR
- AutoMapper
- Serilog.AspNetCore
- Quartz.Extensions.Hosting

### Data Access
- Microsoft.EntityFrameworkCore.SqlServer
- Npgsql.EntityFrameworkCore.PostgreSQL
- Dapper

### HTTP & Resilience
- Microsoft.Extensions.Http.Polly
- Polly.Extensions.Http

### Testing
- xUnit
- Moq
- FluentAssertions
- Microsoft.AspNetCore.Mvc.Testing

## Success Criteria
- [ ] Tất cả projects compile thành công
- [ ] Database migrations chạy không có lỗi
- [ ] Redis connection được thiết lập và test
- [ ] Basic API endpoints response chính xác
- [ ] Unit tests pass cho core components
- [ ] Health checks trả về healthy status
- [ ] Configuration loading hoạt động đúng
- [ ] Logging capture tất cả required information