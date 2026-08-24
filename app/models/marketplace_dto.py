from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryResponse(BaseModel):
    category_id: int
    parent_category_id: int | None = None
    category_name: str
    category_slug: str


class CategoryCreate(BaseModel):
    parent_category_id: int | None = None
    category_name: str = Field(min_length=2, max_length=150)
    category_slug: str = Field(min_length=2, max_length=160)


class ProductResponse(BaseModel):
    product_id: int
    category_id: int
    product_name: str
    product_slug: str
    description: str | None = None
    brand_name: str | None = None
    selling_price: Decimal
    mrp: Decimal
    available_quantity: int = 0
    is_active: bool = True
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminProductResponse(ProductResponse):
    pass


class ProductCreate(BaseModel):
    category_id: int
    product_name: str = Field(min_length=2, max_length=255)
    product_slug: str = Field(min_length=2, max_length=280)
    description: str | None = None
    brand_name: str | None = None
    selling_price: Decimal = Field(ge=0)
    mrp: Decimal = Field(ge=0)
    available_quantity: int = Field(default=0, ge=0)
    is_active: bool = True
    image_url: str | None = None
    image_url: str | None = Field(default=None, max_length=1000)


class AddressCreate(BaseModel):
    address_type: str = "Home"
    recipient_name: str = Field(min_length=2, max_length=200)
    phone_number: str = Field(min_length=7, max_length=20)
    address_line1: str = Field(min_length=2, max_length=255)
    address_line2: str | None = None
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=3, max_length=20)
    country: str = "India"
    is_default: bool = False


class AddressResponse(AddressCreate):
    address_id: int


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    cart_item_id: int
    product_id: int
    product_name: str
    selling_price: Decimal
    quantity: int
    line_total: Decimal


class CartResponse(BaseModel):
    cart_id: int
    items: list[CartItemResponse]
    total_amount: Decimal


class OrderCreate(BaseModel):
    shipping_address_id: int


class OrderStatusUpdate(BaseModel):
    order_status: str


class OrderResponse(BaseModel):
    order_id: int
    order_status: str
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal


class AdminOrderResponse(OrderResponse):
    customer_name: str
    email: str
    phone_number: str | None = None


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: Decimal = Field(ge=0)


class PaymentStatusUpdate(BaseModel):
    payment_status: str
    transaction_id: str | None = None


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    payment_method: str
    payment_status: str
    amount: Decimal
    transaction_id: str | None = None


class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    rating: int = Field(ge=1, le=5)
    review_title: str | None = Field(default=None, max_length=200)
    review_text: str | None = None


class ReviewResponse(ReviewCreate):
    review_id: int
    product_name: str
    user_name: str