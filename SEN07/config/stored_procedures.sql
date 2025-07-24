-- SEN07 Auto Trading Database - Stored Procedures (Refactored)
-- Các thủ tục lưu trữ để truy xuất dữ liệu hiệu quả với schema mới (mỗi timeframe là một bảng riêng, dùng Id cho join)

-- 1. Lấy dữ liệu theo SymbolId, TimeframeId, DataProviderId
CREATE PROCEDURE sp_GetMarketData_ByTimeframe
    @Timeframe NVARCHAR(20), -- tên bảng timeframe (ví dụ: 'm5')
    @SymbolId INT,
    @TimeframeId INT,
    @ProviderId INT,
    @StartDate DATETIME2 = NULL,
    @EndDate DATETIME2 = NULL,
    @Limit INT = 1000
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @sql NVARCHAR(MAX);
    SET @sql = '
        SELECT TOP (' + CAST(@Limit AS NVARCHAR) + ')
            TimeStamp, [Open], [High], [Low], [Close], Volume, SymbolId, DataProviderId, TimeframeId, Exchange, CreatedAt
        FROM [' + @Timeframe + ']
        WHERE SymbolId = @SymbolId
          AND DataProviderId = @ProviderId
          AND TimeframeId = @TimeframeId
          ' + CASE WHEN @StartDate IS NOT NULL THEN ' AND TimeStamp >= @StartDate' ELSE '' END + '
          ' + CASE WHEN @EndDate IS NOT NULL THEN ' AND TimeStamp <= @EndDate' ELSE '' END + '
        ORDER BY TimeStamp DESC
    ';
    EXEC sp_executesql @sql, 
        N'@SymbolId INT, @ProviderId INT, @TimeframeId INT, @StartDate DATETIME2, @EndDate DATETIME2',
        @SymbolId, @ProviderId, @TimeframeId, @StartDate, @EndDate;
END
GO

-- 2. Lấy dữ liệu mới nhất cho mỗi SymbolId trong 1 timeframe
CREATE PROCEDURE sp_GetLatestData_ByTimeframe
    @Timeframe NVARCHAR(20),
    @ProviderId INT,
    @TimeframeId INT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @sql NVARCHAR(MAX);
    SET @sql = '
        WITH LatestData AS (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY SymbolId ORDER BY TimeStamp DESC) AS rn
            FROM [' + @Timeframe + ']
            WHERE DataProviderId = @ProviderId AND TimeframeId = @TimeframeId
        )
        SELECT * FROM LatestData WHERE rn = 1
    ';
    EXEC sp_executesql @sql, N'@ProviderId INT, @TimeframeId INT', @ProviderId, @TimeframeId;
END
GO

-- 3. Lấy log đồng bộ dữ liệu
CREATE PROCEDURE sp_GetSyncLog
    @SymbolId INT = NULL,
    @TimeframeId INT = NULL,
    @ProviderId INT = NULL,
    @Status NVARCHAR(20) = NULL,
    @Days INT = 7
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        dsl.CreatedAt AS SyncTime,
        dsl.SymbolId,
        dsl.TimeframeId,
        tf.Name AS TimeframeName,
        dsl.DataProviderId,
        dp.Name AS ProviderName,
        dsl.Status,
        dsl.RecordsCount,
        dsl.SyncDuration,
        dsl.ErrorMessage
    FROM DataSyncLog dsl
    LEFT JOIN Timeframes tf ON dsl.TimeframeId = tf.Id
    LEFT JOIN DataProviders dp ON dsl.DataProviderId = dp.Id
    WHERE (@SymbolId IS NULL OR dsl.SymbolId = @SymbolId)
      AND (@TimeframeId IS NULL OR dsl.TimeframeId = @TimeframeId)
      AND (@ProviderId IS NULL OR dsl.DataProviderId = @ProviderId)
      AND (@Status IS NULL OR dsl.Status = @Status)
      AND dsl.CreatedAt >= DATEADD(DAY, -@Days, GETDATE())
    ORDER BY dsl.CreatedAt DESC;
END
GO 