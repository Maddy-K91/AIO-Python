/*
    Marketplace database schema for MyPythonApp.
    SQL Server compatible. Safe to run more than once: existing tables are kept.

    Main flow:
    User -> Address -> Order -> OrderItem -> Product
    Product -> Category, Inventory, ProductImage, Review
    User -> Cart -> CartItem
*/

-- 1. Users and customer addresses
IF OBJECT_ID(N'dbo.[User]', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.[User]
    (
        UserId          INT IDENTITY(1, 1) CONSTRAINT PK_User PRIMARY KEY,
        Email           NVARCHAR(255) NOT NULL,
        Password        NVARCHAR(255) NOT NULL,
        FirstName       NVARCHAR(100) NOT NULL,
        LastName        NVARCHAR(100) NULL,
        PhoneNumber     NVARCHAR(20) NULL,
        IsActive        BIT NOT NULL CONSTRAINT DF_User_IsActive DEFAULT 1,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_User_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_User_UpdatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_User_Email UNIQUE (Email)
    );
END;
GO

IF OBJECT_ID(N'dbo.Address', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Address
    (
        AddressId       INT IDENTITY(1, 1) CONSTRAINT PK_Address PRIMARY KEY,
        UserId          INT NOT NULL,
        AddressType     VARCHAR(20) NOT NULL CONSTRAINT DF_Address_Type DEFAULT 'Home',
        RecipientName   NVARCHAR(200) NOT NULL,
        PhoneNumber     NVARCHAR(20) NOT NULL,
        AddressLine1    NVARCHAR(255) NOT NULL,
        AddressLine2    NVARCHAR(255) NULL,
        City            NVARCHAR(100) NOT NULL,
        State           NVARCHAR(100) NOT NULL,
        PostalCode      NVARCHAR(20) NOT NULL,
        Country         NVARCHAR(100) NOT NULL CONSTRAINT DF_Address_Country DEFAULT 'India',
        IsDefault       BIT NOT NULL CONSTRAINT DF_Address_IsDefault DEFAULT 0,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Address_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_Address_User FOREIGN KEY (UserId) REFERENCES dbo.[User](UserId),
        CONSTRAINT CK_Address_Type CHECK (AddressType IN ('Home', 'Work', 'Other'))
    );
END;
GO

-- 2. Product catalog
IF OBJECT_ID(N'dbo.Category', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Category
    (
        CategoryId      INT IDENTITY(1, 1) CONSTRAINT PK_Category PRIMARY KEY,
        ParentCategoryId INT NULL,
        CategoryName    NVARCHAR(150) NOT NULL,
        CategorySlug    VARCHAR(160) NOT NULL,
        IsActive        BIT NOT NULL CONSTRAINT DF_Category_IsActive DEFAULT 1,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Category_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_Category_Slug UNIQUE (CategorySlug),
        CONSTRAINT FK_Category_Parent FOREIGN KEY (ParentCategoryId) REFERENCES dbo.Category(CategoryId)
    );
END;
GO

IF OBJECT_ID(N'dbo.Product', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Product
    (
        ProductId       INT IDENTITY(1, 1) CONSTRAINT PK_Product PRIMARY KEY,
        CategoryId      INT NOT NULL,
        ProductName     NVARCHAR(255) NOT NULL,
        ProductSlug     VARCHAR(280) NOT NULL,
        Description     NVARCHAR(MAX) NULL,
        BrandName       NVARCHAR(100) NULL,
        SellingPrice    DECIMAL(12, 2) NOT NULL,
        MRP             DECIMAL(12, 2) NOT NULL,
        IsActive        BIT NOT NULL CONSTRAINT DF_Product_IsActive DEFAULT 1,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Product_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Product_UpdatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_Product_Slug UNIQUE (ProductSlug),
        CONSTRAINT FK_Product_Category FOREIGN KEY (CategoryId) REFERENCES dbo.Category(CategoryId),
        CONSTRAINT CK_Product_Prices CHECK (SellingPrice >= 0 AND MRP >= SellingPrice)
    );
END;
GO

IF OBJECT_ID(N'dbo.ProductImage', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ProductImage
    (
        ProductImageId  INT IDENTITY(1, 1) CONSTRAINT PK_ProductImage PRIMARY KEY,
        ProductId       INT NOT NULL,
        ImageUrl        NVARCHAR(1000) NOT NULL,
        DisplayOrder    INT NOT NULL CONSTRAINT DF_ProductImage_Order DEFAULT 1,
        IsPrimary       BIT NOT NULL CONSTRAINT DF_ProductImage_IsPrimary DEFAULT 0,
        CONSTRAINT FK_ProductImage_Product FOREIGN KEY (ProductId) REFERENCES dbo.Product(ProductId),
        CONSTRAINT CK_ProductImage_Order CHECK (DisplayOrder > 0)
    );
END;
GO

IF OBJECT_ID(N'dbo.Inventory', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Inventory
    (
        InventoryId     INT IDENTITY(1, 1) CONSTRAINT PK_Inventory PRIMARY KEY,
        ProductId       INT NOT NULL,
        AvailableQty    INT NOT NULL CONSTRAINT DF_Inventory_Available DEFAULT 0,
        ReservedQty     INT NOT NULL CONSTRAINT DF_Inventory_Reserved DEFAULT 0,
        UpdatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Inventory_UpdatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_Inventory_Product UNIQUE (ProductId),
        CONSTRAINT FK_Inventory_Product FOREIGN KEY (ProductId) REFERENCES dbo.Product(ProductId),
        CONSTRAINT CK_Inventory_Quantities CHECK (AvailableQty >= 0 AND ReservedQty >= 0)
    );
END;
GO

-- 3. Shopping cart
IF OBJECT_ID(N'dbo.Cart', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Cart
    (
        CartId          INT IDENTITY(1, 1) CONSTRAINT PK_Cart PRIMARY KEY,
        UserId          INT NOT NULL,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Cart_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Cart_UpdatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_Cart_User UNIQUE (UserId),
        CONSTRAINT FK_Cart_User FOREIGN KEY (UserId) REFERENCES dbo.[User](UserId)
    );
END;
GO

IF OBJECT_ID(N'dbo.CartItem', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CartItem
    (
        CartItemId      INT IDENTITY(1, 1) CONSTRAINT PK_CartItem PRIMARY KEY,
        CartId          INT NOT NULL,
        ProductId       INT NOT NULL,
        Quantity        INT NOT NULL,
        AddedAt         DATETIME2(0) NOT NULL CONSTRAINT DF_CartItem_AddedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_CartItem_Product UNIQUE (CartId, ProductId),
        CONSTRAINT FK_CartItem_Cart FOREIGN KEY (CartId) REFERENCES dbo.Cart(CartId),
        CONSTRAINT FK_CartItem_Product FOREIGN KEY (ProductId) REFERENCES dbo.Product(ProductId),
        CONSTRAINT CK_CartItem_Quantity CHECK (Quantity > 0)
    );
END;
GO

-- 4. Orders, order lines, and payments
IF OBJECT_ID(N'dbo.[Order]', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.[Order]
    (
        OrderId         BIGINT IDENTITY(1, 1) CONSTRAINT PK_Order PRIMARY KEY,
        UserId          INT NOT NULL,
        ShippingAddressId INT NOT NULL,
        OrderStatus     VARCHAR(30) NOT NULL CONSTRAINT DF_Order_Status DEFAULT 'Pending',
        Subtotal        DECIMAL(12, 2) NOT NULL,
        ShippingFee     DECIMAL(12, 2) NOT NULL CONSTRAINT DF_Order_ShippingFee DEFAULT 0,
        DiscountAmount  DECIMAL(12, 2) NOT NULL CONSTRAINT DF_Order_Discount DEFAULT 0,
        TotalAmount     DECIMAL(12, 2) NOT NULL,
        PlacedAt        DATETIME2(0) NOT NULL CONSTRAINT DF_Order_PlacedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Order_UpdatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_Order_User FOREIGN KEY (UserId) REFERENCES dbo.[User](UserId),
        CONSTRAINT FK_Order_Address FOREIGN KEY (ShippingAddressId) REFERENCES dbo.Address(AddressId),
        CONSTRAINT CK_Order_Status CHECK (OrderStatus IN ('Pending', 'Confirmed', 'Packed', 'Shipped', 'Delivered', 'Cancelled', 'Returned')),
        CONSTRAINT CK_Order_Amounts CHECK (Subtotal >= 0 AND ShippingFee >= 0 AND DiscountAmount >= 0 AND TotalAmount >= 0)
    );
END;
GO

IF OBJECT_ID(N'dbo.OrderItem', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.OrderItem
    (
        OrderItemId     BIGINT IDENTITY(1, 1) CONSTRAINT PK_OrderItem PRIMARY KEY,
        OrderId         BIGINT NOT NULL,
        ProductId       INT NOT NULL,
        ProductName     NVARCHAR(255) NOT NULL,
        UnitPrice       DECIMAL(12, 2) NOT NULL,
        Quantity        INT NOT NULL,
        LineTotal       AS (UnitPrice * Quantity) PERSISTED,
        CONSTRAINT FK_OrderItem_Order FOREIGN KEY (OrderId) REFERENCES dbo.[Order](OrderId),
        CONSTRAINT FK_OrderItem_Product FOREIGN KEY (ProductId) REFERENCES dbo.Product(ProductId),
        CONSTRAINT CK_OrderItem_Price CHECK (UnitPrice >= 0),
        CONSTRAINT CK_OrderItem_Quantity CHECK (Quantity > 0)
    );
END;
GO

IF OBJECT_ID(N'dbo.Payment', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Payment
    (
        PaymentId       BIGINT IDENTITY(1, 1) CONSTRAINT PK_Payment PRIMARY KEY,
        OrderId         BIGINT NOT NULL,
        PaymentMethod   VARCHAR(30) NOT NULL,
        PaymentStatus   VARCHAR(30) NOT NULL CONSTRAINT DF_Payment_Status DEFAULT 'Pending',
        TransactionId   VARCHAR(150) NULL,
        Amount          DECIMAL(12, 2) NOT NULL,
        PaidAt          DATETIME2(0) NULL,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Payment_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_Payment_Order FOREIGN KEY (OrderId) REFERENCES dbo.[Order](OrderId),
        CONSTRAINT CK_Payment_Method CHECK (PaymentMethod IN ('Card', 'UPI', 'NetBanking', 'Wallet', 'COD')),
        CONSTRAINT CK_Payment_Status CHECK (PaymentStatus IN ('Pending', 'Paid', 'Failed', 'Refunded')),
        CONSTRAINT CK_Payment_Amount CHECK (Amount >= 0)
    );
END;
GO

-- 5. Product ratings and reviews
IF OBJECT_ID(N'dbo.Review', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Review
    (
        ReviewId        BIGINT IDENTITY(1, 1) CONSTRAINT PK_Review PRIMARY KEY,
        ProductId       INT NOT NULL,
        UserId          INT NOT NULL,
        Rating          TINYINT NOT NULL,
        ReviewTitle     NVARCHAR(200) NULL,
        ReviewText      NVARCHAR(MAX) NULL,
        IsApproved      BIT NOT NULL CONSTRAINT DF_Review_IsApproved DEFAULT 1,
        CreatedAt       DATETIME2(0) NOT NULL CONSTRAINT DF_Review_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_Review_User_Product UNIQUE (ProductId, UserId),
        CONSTRAINT FK_Review_Product FOREIGN KEY (ProductId) REFERENCES dbo.Product(ProductId),
        CONSTRAINT FK_Review_User FOREIGN KEY (UserId) REFERENCES dbo.[User](UserId),
        CONSTRAINT CK_Review_Rating CHECK (Rating BETWEEN 1 AND 5)
    );
END;
GO

-- Common lookup indexes
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Product_CategoryId' AND object_id = OBJECT_ID(N'dbo.Product'))
    CREATE INDEX IX_Product_CategoryId ON dbo.Product(CategoryId);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Order_UserId_Status' AND object_id = OBJECT_ID(N'dbo.Order'))
    CREATE INDEX IX_Order_UserId_Status ON dbo.[Order](UserId, OrderStatus);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_OrderItem_OrderId' AND object_id = OBJECT_ID(N'dbo.OrderItem'))
    CREATE INDEX IX_OrderItem_OrderId ON dbo.OrderItem(OrderId);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Review_ProductId' AND object_id = OBJECT_ID(N'dbo.Review'))
    CREATE INDEX IX_Review_ProductId ON dbo.Review(ProductId);
GO
