from app.models.marketplace_dto import (
    AddressCreate,
    CategoryCreate,
    CartItemCreate,
    CartItemUpdate,
    OrderCreate,
    OrderStatusUpdate,
    PaymentCreate,
    PaymentStatusUpdate,
    ProductCreate,
)
from app.repositories.marketplace_repository import MarketplaceRepository


class MarketplaceService:
    def __init__(self, repository: MarketplaceRepository | None = None) -> None:
        self.repository = repository or MarketplaceRepository()

    def list_categories(self):
        return self.repository.list_categories()

    def create_category(self, data: CategoryCreate):
        return self.repository.create_category(data.model_dump())

    def list_products(self, category_id: int | None, search: str | None):
        return self.repository.list_products(category_id, search)

    def list_products_for_admin(self):
        return self.repository.list_products_for_admin()

    def get_product(self, product_id: int):
        return self.repository.get_product(product_id)
    def create_product(self, data: ProductCreate):
        if data.mrp < data.selling_price:
            raise ValueError("MRP must be greater than or equal to selling price")
        return self.repository.create_product(data.model_dump())
    def list_addresses(self, user_id: int):
        return self.repository.list_addresses(user_id)

    def create_address(self, user_id: int, data: AddressCreate):
        return self.repository.create_address(user_id, data.model_dump())

    def get_cart(self, user_id: int):
        return self.repository.get_cart(user_id)

    def add_cart_item(self, user_id: int, data: CartItemCreate):
        return self.repository.add_cart_item(user_id, data.product_id, data.quantity)

    def update_cart_item(self, user_id: int, item_id: int, data: CartItemUpdate):
        return self.repository.update_cart_item(user_id, item_id, data.quantity)

    def delete_cart_item(self, user_id: int, item_id: int):
        return self.repository.delete_cart_item(user_id, item_id)

    def list_orders(self, user_id: int):
        return self.repository.list_orders(user_id)

    def list_orders_for_admin(self):
        return self.repository.list_orders_for_admin()

    def create_order(self, user_id: int, data: OrderCreate):
        return self.repository.create_order(user_id, data.shipping_address_id)

    def update_order_status(self, user_id: int, order_id: int, data: OrderStatusUpdate):
        return self.repository.update_order_status(user_id, order_id, data.order_status)

    def create_payment(self, data: PaymentCreate):
        return self.repository.create_payment(data.model_dump())

    def update_payment_status(self, payment_id: int, data: PaymentStatusUpdate):
        return self.repository.update_payment_status(payment_id, data.model_dump())

    def list_payments(self):
        return self.repository.list_payments()

    def list_reviews(self):
        return self.repository.list_reviews()

    def create_review(self, data):
        return self.repository.create_review(data.model_dump())


marketplace_service = MarketplaceService()