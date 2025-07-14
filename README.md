# HỆ THỐNG GIAO DỊCH SEN

## Tổng quan Project
HỆ THỐNG GIAO DỊCH SEN là một nền tảng giao dịch forex tự động được xây dựng bằng .NET 8 sử dụng vertical slice architecture. Hệ thống được thiết kế để thu thập và xử lý market data, áp dụng các phân tích phức tạp và rules để tạo ra trading decisions, và thực hiện các decisions đó một cách liền mạch với các brokers bên ngoài.

## Tổng quan Architecture
Hệ thống bao gồm ba modules chính hoạt động cùng nhau thông qua Redis communication tốc độ cao và persistent SQL Server/PostgreSQL storage:

### Module 1: Data Provider (DP)
Module cơ sở này xử lý toàn bộ lifecycle của market data, từ collection ban đầu đến processing và storage.

**Key Components:**
- **External Sourcing & Ingestion**: Kết nối với nhiều data providers sử dụng dedicated APIs
- **Centralized Data Storage**: Lưu trữ historical price data, configuration settings, và trading activity
- **Primary Data Processing**: Chuyển đổi raw price streams thành structured candlestick formats và tính toán technical indicators

**Data Flow:** External APIs → Redis cache → Background processor → Database persistence

### Module 2: Order Generation (OG)
Central intelligence của hệ thống phân tích processed data để xác định trading opportunities và tạo ra specific trade orders.

**Key Components:**
- **Multi-markets Data Analytics**: Thực hiện sophisticated analysis trên nhiều currency pairs
- **Trading Rules Library**: Database của pre-programmed strategies và rule evaluation
- **CORE & Execution Command**: Central orchestrator chuyển đổi signals thành concrete orders
- **Trading Orders Manager**: Risk management module đảm bảo compliance với predefined parameters

**Data Flow:** Redis market data → Analysis algorithms → Strategy rules → Risk validation → Order generation

### Module 3: Order Fulfillment (OF)
Quản lý execution của trade orders trên live market thông qua broker APIs.

**Key Components:**
- **API (Execution Interface)**: Xử lý real-time communication với forex brokers
- **Order Tracking**: Monitors order status và execution results
- **Position Management**: Tracks open positions và calculates real-time P&L

**Data Flow:** Redis order queue → Broker APIs → Execution results → Position updates

## Technology Stack
- **Language**: C# .NET 8
- **Architecture**: Vertical Slice Architecture with MediatR
- **Database**: SQL Server hoặc PostgreSQL for persistence
- **Cache**: Redis for high-speed data communication
- **Web Framework**: ASP.NET Core Web API (minimal APIs)
- **ORM**: Entity Framework Core + Dapper for performance-critical queries
- **Scheduling**: Quartz.NET for background processing
- **Testing**: xUnit, Moq, FluentAssertions
- **Containerization**: Docker + Docker Compose

## Key Features
- **High Performance**: Sub-50ms latency với Redis caching
- **Scalable**: Vertical slice architecture cho phép independent module scaling
- **Reliable**: Multi-provider data sources và robust error handling
- **Risk Management**: Comprehensive position và exposure monitoring
- **Real-time**: Live market data processing và order execution

## Data Communication Strategy
- **Redis**: High-speed cache cho live data và inter-module communication
- **Database**: Persistent storage cho historical data và audit trails
- **Pub/Sub**: Redis publish/subscribe cho real-time updates giữa modules

## Development Timeline
**Tổng thời gian**: 12 tuần (3 tháng)
- **Phase 1**: Foundation & Infrastructure (Tuần 1-2)
- **Phase 2**: Data Provider Module (Tuần 3-5)
- **Phase 3**: Order Generation Module (Tuần 6-8)
- **Phase 4**: Order Fulfillment Module (Tuần 9-10)
- **Phase 5**: Integration & Optimization (Tuần 11-12)

## Module Communication
- **DP → OG**: Redis cache cho market data và indicators
- **OG → OF**: Redis queue cho validated orders
- **OF → OG**: Redis updates cho execution feedback và position changes
- **All Modules**: Database cho persistent storage và audit trails

## Development Plans
Detailed implementation plans cho mỗi module có trong thư mục `/doc`:
- [Foundation & Infrastructure](./doc/01-foundation-infrastructure-vi.md)
- [Data Provider Module](./doc/02-data-provider-module-vi.md)
- [Order Generation Module](./doc/03-order-generation-module-vi.md)
- [Order Fulfillment Module](./doc/04-order-fulfillment-module-vi.md)
- [Integration & Optimization](./doc/05-integration-optimization-vi.md)