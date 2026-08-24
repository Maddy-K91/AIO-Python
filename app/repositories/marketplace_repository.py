from collections.abc import Generator
from contextlib import contextmanager
from decimal import Decimal

import pyodbc

from app.core.config import settings


class MarketplaceRepository:
    @contextmanager
    def connection(self) -> Generator[pyodbc.Connection, None, None]:
        connection = pyodbc.connect(settings.connection_string)
        try:
            yield connection
        finally:
            connection.close()

    def _rows(self, cursor: pyodbc.Cursor) -> list[dict]:
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def list_categories(self) -> list[dict]:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                SELECT CategoryId AS category_id, ParentCategoryId AS parent_category_id,
                       CategoryName AS category_name, CategorySlug AS category_slug
                FROM dbo.Category
                WHERE IsActive = 1
                ORDER BY CategoryName
            """)
            return self._rows(cursor)

    def create_category(self, data: dict) -> dict:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                INSERT INTO dbo.Category (ParentCategoryId, CategoryName, CategorySlug)
                OUTPUT INSERTED.CategoryId AS category_id,
                       INSERTED.ParentCategoryId AS parent_category_id,
                       INSERTED.CategoryName AS category_name,
                       INSERTED.CategorySlug AS category_slug
                VALUES (?, ?, ?)
            """, data["parent_category_id"], data["category_name"], data["category_slug"])
            result = self._rows(cursor)[0]
            connection.commit()
            return result

    def list_products(self, category_id: int | None, search: str | None) -> list[dict]:
        query = """
            SELECT p.ProductId AS product_id, p.CategoryId AS category_id,
                   p.ProductName AS product_name, p.ProductSlug AS product_slug,
                   p.Description AS description, p.BrandName AS brand_name,
                   p.SellingPrice AS selling_price, p.MRP AS mrp,
                     p.IsActive AS is_active,
                     image.ImageUrl AS image_url,
                   ISNULL(i.AvailableQty, 0) AS available_quantity
            FROM dbo.Product AS p
            LEFT JOIN dbo.Inventory AS i ON i.ProductId = p.ProductId
                 OUTER APPLY (SELECT TOP 1 ImageUrl FROM dbo.ProductImage
                        WHERE ProductId = p.ProductId ORDER BY IsPrimary DESC, DisplayOrder) AS image
            WHERE p.IsActive = 1
        """
        parameters: list[object] = []
        if category_id is not None:
            query += " AND p.CategoryId = ?"
            parameters.append(category_id)
        if search:
            query += " AND (p.ProductName LIKE ? OR p.BrandName LIKE ?)"
            parameters.extend([f"%{search}%", f"%{search}%"])
        query += " ORDER BY p.CreatedAt DESC"
        with self.connection() as connection:
            return self._rows(connection.cursor().execute(query, *parameters))

    def get_product(self, product_id: int) -> dict | None:
        products = self.list_products(None, None)
        return next((product for product in products if product["product_id"] == product_id), None)

    def list_products_for_admin(self) -> list[dict]:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                SELECT p.ProductId AS product_id, p.CategoryId AS category_id,
                       p.ProductName AS product_name, p.ProductSlug AS product_slug,
                       p.Description AS description, p.BrandName AS brand_name,
                       p.SellingPrice AS selling_price, p.MRP AS mrp,
                       p.IsActive AS is_active,
                      image.ImageUrl AS image_url,
                       ISNULL(i.AvailableQty, 0) AS available_quantity
                FROM dbo.Product AS p
                LEFT JOIN dbo.Inventory AS i ON i.ProductId = p.ProductId
                  OUTER APPLY (SELECT TOP 1 ImageUrl FROM dbo.ProductImage
                         WHERE ProductId = p.ProductId ORDER BY IsPrimary DESC, DisplayOrder) AS image
                ORDER BY p.CreatedAt DESC
            """)
            return self._rows(cursor)

    def create_product(self, data: dict) -> dict:
        with self.connection() as connection:
            cursor = connection.cursor()
            product = self._rows(cursor.execute("""
                INSERT INTO dbo.Product
                    (CategoryId, ProductName, ProductSlug, Description, BrandName, SellingPrice, MRP, IsActive)
                OUTPUT INSERTED.ProductId AS product_id, INSERTED.CategoryId AS category_id,
                       INSERTED.ProductName AS product_name, INSERTED.ProductSlug AS product_slug,
                       INSERTED.Description AS description, INSERTED.BrandName AS brand_name,
                       INSERTED.SellingPrice AS selling_price, INSERTED.MRP AS mrp,
                       INSERTED.IsActive AS is_active
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, data["category_id"], data["product_name"], data["product_slug"],
                       data["description"], data["brand_name"], data["selling_price"],
                       data["mrp"], data["is_active"]))[0]
            cursor.execute("INSERT INTO dbo.Inventory (ProductId, AvailableQty) VALUES (?, ?)",
                           product["product_id"], data["available_quantity"])
            if data["image_url"]:
                cursor.execute("""
                    INSERT INTO dbo.ProductImage (ProductId, ImageUrl, IsPrimary)
                    VALUES (?, ?, 1)
                """, product["product_id"], data["image_url"])
            connection.commit()
            product["available_quantity"] = data["available_quantity"]
            product["image_url"] = data["image_url"]
            return product

    def list_addresses(self, user_id: int) -> list[dict]:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                SELECT AddressId AS address_id, AddressType AS address_type,
                       RecipientName AS recipient_name, PhoneNumber AS phone_number,
                       AddressLine1 AS address_line1, AddressLine2 AS address_line2,
                       City AS city, State AS state, PostalCode AS postal_code,
                       Country AS country, IsDefault AS is_default
                FROM dbo.Address WHERE UserId = ? ORDER BY IsDefault DESC, AddressId DESC
            """, user_id)
            return self._rows(cursor)

    def create_address(self, user_id: int, data: dict) -> dict:
        with self.connection() as connection:
            cursor = connection.cursor()
            if data["is_default"]:
                cursor.execute("UPDATE dbo.Address SET IsDefault = 0 WHERE UserId = ?", user_id)
            result = self._rows(cursor.execute("""
                INSERT INTO dbo.Address
                    (UserId, AddressType, RecipientName, PhoneNumber, AddressLine1, AddressLine2,
                     City, State, PostalCode, Country, IsDefault)
                OUTPUT INSERTED.AddressId AS address_id, INSERTED.AddressType AS address_type,
                       INSERTED.RecipientName AS recipient_name, INSERTED.PhoneNumber AS phone_number,
                       INSERTED.AddressLine1 AS address_line1, INSERTED.AddressLine2 AS address_line2,
                       INSERTED.City AS city, INSERTED.State AS state, INSERTED.PostalCode AS postal_code,
                       INSERTED.Country AS country, INSERTED.IsDefault AS is_default
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, user_id, data["address_type"], data["recipient_name"], data["phone_number"],
                       data["address_line1"], data["address_line2"], data["city"], data["state"],
                       data["postal_code"], data["country"], data["is_default"]))[0]
            connection.commit()
            return result

    def get_or_create_cart(self, user_id: int) -> int:
        with self.connection() as connection:
            cursor = connection.cursor()
            row = cursor.execute("SELECT CartId FROM dbo.Cart WHERE UserId = ?", user_id).fetchone()
            if row:
                return row[0]
            row = cursor.execute("""
                INSERT INTO dbo.Cart (UserId) OUTPUT INSERTED.CartId VALUES (?)
            """, user_id).fetchone()
            connection.commit()
            return row[0]

    def get_cart(self, user_id: int) -> dict:
        cart_id = self.get_or_create_cart(user_id)
        with self.connection() as connection:
            rows = self._rows(connection.cursor().execute("""
                SELECT ci.CartItemId AS cart_item_id, ci.ProductId AS product_id,
                       p.ProductName AS product_name, p.SellingPrice AS selling_price,
                       ci.Quantity AS quantity, (p.SellingPrice * ci.Quantity) AS line_total
                FROM dbo.CartItem AS ci
                JOIN dbo.Product AS p ON p.ProductId = ci.ProductId
                WHERE ci.CartId = ? ORDER BY ci.AddedAt DESC
            """, cart_id))
        return {"cart_id": cart_id, "items": rows,
                "total_amount": sum((row["line_total"] for row in rows), Decimal("0"))}

    def add_cart_item(self, user_id: int, product_id: int, quantity: int) -> dict:
        cart_id = self.get_or_create_cart(user_id)
        with self.connection() as connection:
            connection.cursor().execute("""
                MERGE dbo.CartItem AS target
                USING (SELECT ? AS CartId, ? AS ProductId) AS source
                ON target.CartId = source.CartId AND target.ProductId = source.ProductId
                WHEN MATCHED THEN UPDATE SET Quantity = target.Quantity + ?
                WHEN NOT MATCHED THEN INSERT (CartId, ProductId, Quantity)
                    VALUES (source.CartId, source.ProductId, ?);
            """, cart_id, product_id, quantity, quantity)
            connection.commit()
        return self.get_cart(user_id)

    def update_cart_item(self, user_id: int, item_id: int, quantity: int) -> dict:
        with self.connection() as connection:
            connection.cursor().execute("""
                UPDATE ci SET Quantity = ?
                FROM dbo.CartItem AS ci JOIN dbo.Cart AS c ON c.CartId = ci.CartId
                WHERE ci.CartItemId = ? AND c.UserId = ?
            """, quantity, item_id, user_id)
            connection.commit()
        return self.get_cart(user_id)

    def delete_cart_item(self, user_id: int, item_id: int) -> dict:
        with self.connection() as connection:
            connection.cursor().execute("""
                DELETE ci FROM dbo.CartItem AS ci
                JOIN dbo.Cart AS c ON c.CartId = ci.CartId
                WHERE ci.CartItemId = ? AND c.UserId = ?
            """, item_id, user_id)
            connection.commit()
        return self.get_cart(user_id)

    def list_orders(self, user_id: int) -> list[dict]:
        with self.connection() as connection:
            return self._rows(connection.cursor().execute("""
                SELECT OrderId AS order_id, OrderStatus AS order_status, Subtotal AS subtotal,
                       ShippingFee AS shipping_fee, DiscountAmount AS discount_amount,
                       TotalAmount AS total_amount
                FROM dbo.[Order] WHERE UserId = ? ORDER BY PlacedAt DESC
            """, user_id))

    def list_orders_for_admin(self) -> list[dict]:
        with self.connection() as connection:
            return self._rows(connection.cursor().execute("""
                SELECT o.OrderId AS order_id, o.OrderStatus AS order_status,
                       o.Subtotal AS subtotal, o.ShippingFee AS shipping_fee,
                       o.DiscountAmount AS discount_amount, o.TotalAmount AS total_amount,
                       CONCAT(u.FirstName, CASE WHEN u.LastName IS NULL THEN ''
                           ELSE CONCAT(' ', u.LastName) END) AS customer_name,
                       u.Email AS email, u.PhoneNumber AS phone_number
                FROM dbo.[Order] AS o
                JOIN dbo.[User] AS u ON u.UserId = o.UserId
                ORDER BY o.PlacedAt DESC
            """))

    def create_order(self, user_id: int, address_id: int) -> dict:
        with self.connection() as connection:
            cursor = connection.cursor()
            cart = cursor.execute("""
                SELECT p.ProductId, p.ProductName, p.SellingPrice, ci.Quantity
                FROM dbo.CartItem AS ci JOIN dbo.Cart AS c ON c.CartId = ci.CartId
                JOIN dbo.Product AS p ON p.ProductId = ci.ProductId
                WHERE c.UserId = ?
            """, user_id).fetchall()
            if not cart:
                raise ValueError("Cart is empty")
            subtotal = sum((row.SellingPrice * row.Quantity for row in cart), Decimal("0"))
            order = self._rows(cursor.execute("""
                INSERT INTO dbo.[Order]
                    (UserId, ShippingAddressId, Subtotal, ShippingFee, DiscountAmount, TotalAmount)
                OUTPUT INSERTED.OrderId AS order_id, INSERTED.OrderStatus AS order_status,
                       INSERTED.Subtotal AS subtotal, INSERTED.ShippingFee AS shipping_fee,
                       INSERTED.DiscountAmount AS discount_amount, INSERTED.TotalAmount AS total_amount
                VALUES (?, ?, ?, 0, 0, ?)
            """, user_id, address_id, subtotal, subtotal))[0]
            for item in cart:
                cursor.execute("""
                    INSERT INTO dbo.OrderItem (OrderId, ProductId, ProductName, UnitPrice, Quantity)
                    VALUES (?, ?, ?, ?, ?)
                """, order["order_id"], item.ProductId, item.ProductName, item.SellingPrice, item.Quantity)
            cursor.execute("DELETE ci FROM dbo.CartItem AS ci JOIN dbo.Cart AS c ON c.CartId = ci.CartId WHERE c.UserId = ?", user_id)
            connection.commit()
            return order

    def update_order_status(self, user_id: int, order_id: int, order_status: str) -> dict | None:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                UPDATE dbo.[Order] SET OrderStatus = ?, UpdatedAt = SYSUTCDATETIME()
                OUTPUT INSERTED.OrderId AS order_id, INSERTED.OrderStatus AS order_status,
                       INSERTED.Subtotal AS subtotal, INSERTED.ShippingFee AS shipping_fee,
                       INSERTED.DiscountAmount AS discount_amount, INSERTED.TotalAmount AS total_amount
                WHERE OrderId = ? AND UserId = ?
            """, order_status, order_id, user_id)
            rows = self._rows(cursor)
            connection.commit()
            return rows[0] if rows else None

    def create_payment(self, data: dict) -> dict:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                INSERT INTO dbo.Payment (OrderId, PaymentMethod, Amount)
                OUTPUT INSERTED.PaymentId AS payment_id, INSERTED.OrderId AS order_id,
                       INSERTED.PaymentMethod AS payment_method, INSERTED.PaymentStatus AS payment_status,
                       INSERTED.Amount AS amount
                VALUES (?, ?, ?)
            """, data["order_id"], data["payment_method"], data["amount"])
            result = self._rows(cursor)[0]
            connection.commit()
            return result

    def list_payments(self) -> list[dict]:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                SELECT PaymentId AS payment_id, OrderId AS order_id,
                       PaymentMethod AS payment_method, PaymentStatus AS payment_status,
                       Amount AS amount, TransactionId AS transaction_id
                FROM dbo.Payment
                ORDER BY CreatedAt DESC
            """)
            return self._rows(cursor)

    def update_payment_status(self, payment_id: int, data: dict) -> dict | None:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                UPDATE dbo.Payment SET PaymentStatus = ?, TransactionId = ?,
                    PaidAt = CASE WHEN ? = 'Paid' THEN SYSUTCDATETIME() ELSE PaidAt END
                OUTPUT INSERTED.PaymentId AS payment_id, INSERTED.OrderId AS order_id,
                       INSERTED.PaymentMethod AS payment_method, INSERTED.PaymentStatus AS payment_status,
                       INSERTED.Amount AS amount, INSERTED.TransactionId AS transaction_id
                WHERE PaymentId = ?
            """, data["payment_status"], data["transaction_id"], data["payment_status"], payment_id)
            rows = self._rows(cursor)
            connection.commit()
            return rows[0] if rows else None

    def list_reviews(self) -> list[dict]:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                  SELECT r.ReviewId AS review_id, r.ProductId AS product_id,
                      r.UserId AS user_id, p.ProductName AS product_name,
                      u.Email AS user_name, r.Rating AS rating,
                      r.ReviewTitle AS review_title, r.ReviewText AS review_text
                FROM dbo.Review AS r
                JOIN dbo.Product AS p ON p.ProductId = r.ProductId
                JOIN dbo.[User] AS u ON u.UserId = r.UserId
                ORDER BY r.CreatedAt DESC
            """)
            return self._rows(cursor)

    def create_review(self, data: dict) -> dict:
        with self.connection() as connection:
            cursor = connection.cursor().execute("""
                INSERT INTO dbo.Review
                    (ProductId, UserId, Rating, ReviewTitle, ReviewText)
                OUTPUT INSERTED.ReviewId
                VALUES (?, ?, ?, ?, ?)
            """, data["product_id"], data["user_id"], data["rating"],
                       data["review_title"], data["review_text"])
            review_id = cursor.fetchone()[0]
            result = self._rows(connection.cursor().execute("""
                SELECT r.ReviewId AS review_id, r.ProductId AS product_id,
                       r.UserId AS user_id, p.ProductName AS product_name,
                       u.Email AS user_name, r.Rating AS rating,
                       r.ReviewTitle AS review_title, r.ReviewText AS review_text
                FROM dbo.Review AS r
                JOIN dbo.Product AS p ON p.ProductId = r.ProductId
                JOIN dbo.[User] AS u ON u.UserId = r.UserId
                WHERE r.ReviewId = ?
            """, review_id))[0]
            connection.commit()
            return result