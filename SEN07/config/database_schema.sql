-- SQL Server Database Design

-- 1. Bảng DataProviders (Nguồn dữ liệu)
CREATE TABLE DataProviders (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(200),
    Active BIT DEFAULT 1
);

-- 2. Bảng Timeframes
CREATE TABLE Timeframes (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(20) NOT NULL UNIQUE,
    Minutes INT NOT NULL,
    Description NVARCHAR(100),
    Active BIT DEFAULT 1
);

-- 3. Bảng Symbols
CREATE TABLE Symbols (
    Id INT PRIMARY KEY,
    Symbol NVARCHAR(20) NOT NULL,
    RefName NVARCHAR(100),
    Type NVARCHAR(50),
    Active BIT DEFAULT 1
);

-- 4. Bảng DataSyncLog (log đồng bộ)
CREATE TABLE DataSyncLog (
    Id BIGINT IDENTITY(1,1) PRIMARY KEY,
    SymbolId INT NOT NULL,
    TimeframeId INT NOT NULL,
    DataProviderId INT NOT NULL,
    LastSyncTime DATETIME2,
    RecordsCount INT DEFAULT 0,
    Status NVARCHAR(20) DEFAULT 'SUCCESS',
    ErrorMessage NVARCHAR(500),
    SyncDuration INT,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

-- 5. Các bảng dữ liệu market data theo timeframe (ví dụ: [1m], [3m], ...)
-- (Tạo thủ công hoặc tự động bằng script Python, ví dụ:)
-- CREATE TABLE [1m] (...), CREATE TABLE [1h] (...), ...

-- ===========================
-- INSERT DỮ LIỆU MẪU
-- ===========================

-- DataProviders
INSERT INTO DataProviders (Name, Description, Active) VALUES
('CAPITALCOM', N'TradingView Data', 1),
('FTMO', N'MetaTrader 5', 1);

-- Timeframes
INSERT INTO Timeframes (Name, Minutes, Description, Active) VALUES
('m1', 1, N'1 phút', 1),
('m3', 3, N'3 phút', 1),
('m5', 5, N'5 phút', 1),
('m15', 15, N'15 phút', 1),
('m30', 30, N'30 phút', 1),
('h1', 60, N'1 giờ', 1),
('h4', 240, N'4 giờ', 1),
('h8', 480, N'8 giờ', 1),
('D', 1440, N'1 ngày', 1),
('W', 10080, N'1 tuần', 1),
('M', 43200, N'1 tháng', 1);

-- Symbols (Id tường minh)
INSERT INTO Symbols (Id, Symbol, RefName, Type, Active) VALUES
(2, 'FRA40', 'FRA40', 'INDICE', 1),
(3, 'GER30', 'GER40', 'INDICE', 1),
(4, 'HKG33', 'HK50', 'INDICE', 1),
(5, 'JPN225', 'JPN225', 'INDICE', 1),
(6, 'ESP35', 'SPA35', 'INDICE', 1),
(7, 'UK100', 'UK100', 'INDICE', 1),
(8, 'SPX500', 'US500', 'INDICE', 1),
(9, 'NAS100', 'NQ100', 'INDICE', 1),
(10, 'US30', 'US30', 'INDICE', 1),
(11, 'AUDCAD', 'AUDCAD', 'FOREX', 1),
(12, 'AUDJPY', 'AUDJPY', 'FOREX', 1),
(13, 'AUDNZD', 'AUDNZD', 'FOREX', 1),
(14, 'AUDCHF', 'AUDCHF', 'FOREX', 1),
(15, 'AUDUSD', 'AUDUSD', 'FOREX', 1),
(16, 'GBPAUD', 'GBPAUD', 'FOREX', 1),
(17, 'GBPCAD', 'GBPCAD', 'FOREX', 1),
(18, 'GBPJPY', 'GBPJPY', 'FOREX', 1),
(19, 'GBPNZD', 'GBPNZD', 'FOREX', 1),
(20, 'GBPCHF', 'GBPCHF', 'FOREX', 1),
(21, 'GBPUSD', 'GBPUSD', 'FOREX', 1),
(22, 'CADJPY', 'CADJPY', 'FOREX', 1),
(23, 'CADCHF', 'CADCHF', 'FOREX', 1),
(24, 'EURAUD', 'EURAUD', 'FOREX', 1),
(25, 'EURGBP', 'EURGBP', 'FOREX', 1),
(26, 'EURCAD', 'EURCAD', 'FOREX', 1),
(27, 'EURJPY', 'EURJPY', 'FOREX', 1),
(28, 'EURNZD', 'EURNZD', 'FOREX', 1),
(32, 'EURCHF', 'EURCHF', 'FOREX', 1),
(33, 'EURUSD', 'EURUSD', 'FOREX', 1),
(34, 'NZDCAD', 'NZDCAD', 'FOREX', 1),
(35, 'NZDJPY', 'NZDJPY', 'FOREX', 1),
(36, 'NZDUSD', 'NZDUSD', 'FOREX', 1),
(37, 'USCAD', 'USDCAD', 'FOREX', 1),
(41, 'USDJPY', 'USDJPY', 'FOREX', 1),
(48, 'USDCHF', 'USDCHF', 'FOREX', 1),
(56, 'GOLD', 'XAUUSD', 'METAL', 1),
(81, 'BTCUSD', 'BTCUSD', 'CRYPTO', 1);

-- Ví dụ truy vấn lấy Id từ Name (chuẩn hóa cho ETL/backtest):
-- SELECT Id FROM DataProviders WHERE Name = 'FTMO';
-- SELECT Id FROM Timeframes WHERE Name = 'm5';

-- OHLCV Table Template
-- {timeframe} sẽ được thay bằng tên timeframe
CREATE TABLE [{timeframe}] (
    SymbolId INT NOT NULL,
    DataProviderId INT NOT NULL,
    TimeframeId INT NOT NULL,
    TimeStamp DATETIME2 NOT NULL,
    [Open] FLOAT NOT NULL,
    [High] FLOAT NOT NULL,
    [Low] FLOAT NOT NULL,
    [Close] FLOAT NOT NULL,
    Volume BIGINT,
    Exchange NVARCHAR(50),
    PRIMARY KEY (SymbolId, DataProviderId, TimeframeId, TimeStamp)
);
