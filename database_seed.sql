/*
    Development/demo data for the marketplace schema.
    Run database_schema.sql first, then run this file.
    The sample password is plain text only because the current demo login query
    reads User.Password directly. Never use these credentials in production.
*/

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET ARITHABORT ON;
SET XACT_ABORT ON;
BEGIN TRANSACTION;

DECLARE @UserId INT;
DECLARE @SecondUserId INT;
DECLARE @CategoryId INT;
DECLARE @ChildCategoryId INT;
DECLARE @ProductId INT;
DECLARE @SecondProductId INT;
DECLARE @AddressId INT;
DECLARE @CartId INT;
DECLARE @OrderId BIGINT;
DECLARE @PaymentId BIGINT;

-- Users: one customer for UI testing and one second customer for reviews.
IF NOT EXISTS (SELECT 1 FROM dbo.[User] WHERE Email = 'demo.customer@example.com')
BEGIN
    INSERT INTO dbo.[User] (Email, Password, FirstName, LastName, PhoneNumber)
    VALUES ('demo.customer@example.com', 'Demo@12345', 'Demo', 'Customer', '9876543210');
END;

IF NOT EXISTS (SELECT 1 FROM dbo.[User] WHERE Email = 'test.customer@example.com')
BEGIN
    INSERT INTO dbo.[User] (Email, Password, FirstName, LastName, PhoneNumber)
    VALUES ('test.customer@example.com', 'Test@12345', 'Test', 'Customer', '9876501234');
END;

SELECT @UserId = UserId FROM dbo.[User] WHERE Email = 'demo.customer@example.com';
SELECT @SecondUserId = UserId FROM dbo.[User] WHERE Email = 'test.customer@example.com';

-- Categories: an Electronics parent and a Mobiles child category.
IF NOT EXISTS (SELECT 1 FROM dbo.Category WHERE CategorySlug = 'electronics')
BEGIN
    INSERT INTO dbo.Category (CategoryName, CategorySlug)
    VALUES ('Electronics', 'electronics');
END;
SELECT @CategoryId = CategoryId FROM dbo.Category WHERE CategorySlug = 'electronics';

IF NOT EXISTS (SELECT 1 FROM dbo.Category WHERE CategorySlug = 'mobiles')
BEGIN
    INSERT INTO dbo.Category (ParentCategoryId, CategoryName, CategorySlug)
    VALUES (@CategoryId, 'Mobiles', 'mobiles');
END;
SELECT @ChildCategoryId = CategoryId FROM dbo.Category WHERE CategorySlug = 'mobiles';

-- Products: two products for listing, search, details, and cart screens.
IF NOT EXISTS (SELECT 1 FROM dbo.Product WHERE ProductSlug = 'demo-smartphone-5g')
BEGIN
    INSERT INTO dbo.Product
        (CategoryId, ProductName, ProductSlug, Description, BrandName, SellingPrice, MRP)
    VALUES
        (@ChildCategoryId, 'Demo Smartphone 5G', 'demo-smartphone-5g',
         'A demo 5G smartphone with a bright display and long battery life.',
         'DemoTech', 24999.00, 29999.00);
END;
SELECT @ProductId = ProductId FROM dbo.Product WHERE ProductSlug = 'demo-smartphone-5g';

IF NOT EXISTS (SELECT 1 FROM dbo.Product WHERE ProductSlug = 'demo-wireless-headphones')
BEGIN
    INSERT INTO dbo.Product
        (CategoryId, ProductName, ProductSlug, Description, BrandName, SellingPrice, MRP)
    VALUES
        (@CategoryId, 'Demo Wireless Headphones', 'demo-wireless-headphones',
         'Comfortable wireless headphones for everyday listening.',
         'SoundDemo', 1999.00, 3499.00);
END;
SELECT @SecondProductId = ProductId FROM dbo.Product WHERE ProductSlug = 'demo-wireless-headphones';

-- Product images: used by product cards and the product details page.
IF NOT EXISTS (SELECT 1 FROM dbo.ProductImage WHERE ProductId = @ProductId AND IsPrimary = 1)
BEGIN
    INSERT INTO dbo.ProductImage (ProductId, ImageUrl, DisplayOrder, IsPrimary)
    VALUES (@ProductId, 'https://placehold.co/600x600?text=Demo+Smartphone', 1, 1);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.ProductImage WHERE ProductId = @SecondProductId AND IsPrimary = 1)
BEGIN
    INSERT INTO dbo.ProductImage (ProductId, ImageUrl, DisplayOrder, IsPrimary)
    VALUES (@SecondProductId, 'https://placehold.co/600x600?text=Demo+Headphones', 1, 1);
END;

-- Inventory: stock numbers for product cards and cart validation.
IF NOT EXISTS (SELECT 1 FROM dbo.Inventory WHERE ProductId = @ProductId)
BEGIN
    INSERT INTO dbo.Inventory (ProductId, AvailableQty, ReservedQty)
    VALUES (@ProductId, 25, 0);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.Inventory WHERE ProductId = @SecondProductId)
BEGIN
    INSERT INTO dbo.Inventory (ProductId, AvailableQty, ReservedQty)
    VALUES (@SecondProductId, 50, 0);
END;

-- Addresses: one default delivery address for checkout testing.
IF NOT EXISTS (SELECT 1 FROM dbo.Address WHERE UserId = @UserId AND PostalCode = '560001')
BEGIN
    INSERT INTO dbo.Address
        (UserId, AddressType, RecipientName, PhoneNumber, AddressLine1, AddressLine2,
         City, State, PostalCode, Country, IsDefault)
    VALUES
        (@UserId, 'Home', 'Demo Customer', '9876543210', '10 Demo Street', 'Near Demo Mall',
         'Bengaluru', 'Karnataka', '560001', 'India', 1);
END;
SELECT @AddressId = AddressId
FROM dbo.Address
WHERE UserId = @UserId AND PostalCode = '560001';

-- Cart and cart items: data for the shopping-cart screen.
IF NOT EXISTS (SELECT 1 FROM dbo.Cart WHERE UserId = @UserId)
BEGIN
    INSERT INTO dbo.Cart (UserId) VALUES (@UserId);
END;
SELECT @CartId = CartId FROM dbo.Cart WHERE UserId = @UserId;

IF NOT EXISTS (SELECT 1 FROM dbo.CartItem WHERE CartId = @CartId AND ProductId = @ProductId)
BEGIN
    INSERT INTO dbo.CartItem (CartId, ProductId, Quantity)
    VALUES (@CartId, @ProductId, 1);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.CartItem WHERE CartId = @CartId AND ProductId = @SecondProductId)
BEGIN
    INSERT INTO dbo.CartItem (CartId, ProductId, Quantity)
    VALUES (@CartId, @SecondProductId, 2);
END;

-- Order and order item: data for order history and order details screens.
IF NOT EXISTS (SELECT 1 FROM dbo.[Order] WHERE UserId = @UserId AND ShippingAddressId = @AddressId)
BEGIN
    INSERT INTO dbo.[Order]
        (UserId, ShippingAddressId, OrderStatus, Subtotal, ShippingFee, DiscountAmount, TotalAmount)
    VALUES
        (@UserId, @AddressId, 'Delivered', 26998.00, 0.00, 1000.00, 25998.00);
END;
SELECT TOP 1 @OrderId = OrderId
FROM dbo.[Order]
WHERE UserId = @UserId AND ShippingAddressId = @AddressId
ORDER BY OrderId DESC;

IF NOT EXISTS (SELECT 1 FROM dbo.OrderItem WHERE OrderId = @OrderId AND ProductId = @ProductId)
BEGIN
    INSERT INTO dbo.OrderItem (OrderId, ProductId, ProductName, UnitPrice, Quantity)
    VALUES (@OrderId, @ProductId, 'Demo Smartphone 5G', 24999.00, 1);
END;

IF NOT EXISTS (SELECT 1 FROM dbo.OrderItem WHERE OrderId = @OrderId AND ProductId = @SecondProductId)
BEGIN
    INSERT INTO dbo.OrderItem (OrderId, ProductId, ProductName, UnitPrice, Quantity)
    VALUES (@OrderId, @SecondProductId, 'Demo Wireless Headphones', 1999.00, 1);
END;

-- Payment: a successful UPI payment for the demo order.
IF NOT EXISTS (SELECT 1 FROM dbo.Payment WHERE OrderId = @OrderId)
BEGIN
    INSERT INTO dbo.Payment
        (OrderId, PaymentMethod, PaymentStatus, TransactionId, Amount, PaidAt)
    VALUES
        (@OrderId, 'UPI', 'Paid', 'DEMO-TXN-10001', 25998.00, SYSUTCDATETIME());
END;
SELECT @PaymentId = PaymentId FROM dbo.Payment WHERE OrderId = @OrderId;

-- Review: customer feedback for the product details page.
IF NOT EXISTS (SELECT 1 FROM dbo.Review WHERE ProductId = @ProductId AND UserId = @SecondUserId)
BEGIN
    INSERT INTO dbo.Review
        (ProductId, UserId, Rating, ReviewTitle, ReviewText)
    VALUES
        (@ProductId, @SecondUserId, 5, 'Great demo product',
         'The phone looks excellent and the battery lasts all day.');
END;

COMMIT TRANSACTION;

-- Quick verification for the UI developer.
SELECT 'User' AS TableName, COUNT(*) AS TestRowCount FROM dbo.[User]
UNION ALL SELECT 'Address', COUNT(*) FROM dbo.Address
UNION ALL SELECT 'Category', COUNT(*) FROM dbo.Category
UNION ALL SELECT 'Product', COUNT(*) FROM dbo.Product
UNION ALL SELECT 'ProductImage', COUNT(*) FROM dbo.ProductImage
UNION ALL SELECT 'Inventory', COUNT(*) FROM dbo.Inventory
UNION ALL SELECT 'Cart', COUNT(*) FROM dbo.Cart
UNION ALL SELECT 'CartItem', COUNT(*) FROM dbo.CartItem
UNION ALL SELECT 'Order', COUNT(*) FROM dbo.[Order]
UNION ALL SELECT 'OrderItem', COUNT(*) FROM dbo.OrderItem
UNION ALL SELECT 'Payment', COUNT(*) FROM dbo.Payment
UNION ALL SELECT 'Review', COUNT(*) FROM dbo.Review;
