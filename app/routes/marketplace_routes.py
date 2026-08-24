from pathlib import Path
from uuid import uuid4
from decimal import Decimal

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.models.marketplace_dto import (
    AddressCreate,
    AddressResponse,
    AdminProductResponse,
    AdminOrderResponse,
    CategoryCreate,
    CategoryResponse,
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    PaymentCreate,
    PaymentResponse,
    PaymentStatusUpdate,
    ProductCreate,
    ProductResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.core.config import settings
from app.services.marketplace_service import marketplace_service

router = APIRouter(prefix="/api", tags=["Marketplace"])


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories():
    return marketplace_service.list_categories()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(request: CategoryCreate): return marketplace_service.create_category(request)


@router.get("/products", response_model=list[ProductResponse])
async def list_products(category_id: int | None = None, search: str | None = Query(default=None, max_length=100)):
    return marketplace_service.list_products(category_id, search)


@router.get("/admin/products", response_model=list[AdminProductResponse])
async def list_products_for_admin():
    return marketplace_service.list_products_for_admin()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    product = marketplace_service.get_product(product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(request: ProductCreate):
    try:
        return marketplace_service.create_product(request)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error


@router.post("/products/upload", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_with_image(
    category_id: int = Form(...),
    product_name: str = Form(..., min_length=2, max_length=255),
    product_slug: str = Form(..., min_length=2, max_length=280),
    selling_price: Decimal = Form(..., ge=0),
    mrp: Decimal = Form(..., ge=0),
    description: str | None = Form(None),
    brand_name: str | None = Form(None),
    available_quantity: int = Form(0, ge=0),
    is_active: bool = Form(True),
    image: UploadFile = File(...),
):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    extension = Path(image.filename or "").suffix.lower()
    if image.content_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"} or extension not in allowed_extensions:
        raise HTTPException(415, "Only JPG, PNG, WEBP, and GIF images are supported")

    image_directory = settings.media_directory / "products"
    image_directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    image_path = image_directory / filename
    image_path.write_bytes(await image.read())

    request = ProductCreate(
        category_id=category_id,
        product_name=product_name,
        product_slug=product_slug,
        description=description,
        brand_name=brand_name,
        selling_price=selling_price,
        mrp=mrp,
        available_quantity=available_quantity,
        is_active=is_active,
        image_url=f"/media/products/{filename}",
    )
    try:
        return marketplace_service.create_product(request)
    except ValueError as error:
        image_path.unlink(missing_ok=True)
        raise HTTPException(400, str(error)) from error


@router.get("/users/{user_id}/addresses", response_model=list[AddressResponse])
async def list_addresses(user_id: int): return marketplace_service.list_addresses(user_id)


@router.post("/users/{user_id}/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(user_id: int, request: AddressCreate): return marketplace_service.create_address(user_id, request)


@router.get("/users/{user_id}/cart", response_model=CartResponse)
async def get_cart(user_id: int): return marketplace_service.get_cart(user_id)


@router.post("/users/{user_id}/cart/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(user_id: int, request: CartItemCreate): return marketplace_service.add_cart_item(user_id, request)


@router.patch("/users/{user_id}/cart/items/{item_id}", response_model=CartResponse)
async def update_cart_item(user_id: int, item_id: int, request: CartItemUpdate): return marketplace_service.update_cart_item(user_id, item_id, request)


@router.delete("/users/{user_id}/cart/items/{item_id}", response_model=CartResponse)
async def delete_cart_item(user_id: int, item_id: int): return marketplace_service.delete_cart_item(user_id, item_id)


@router.get("/users/{user_id}/orders", response_model=list[OrderResponse])
async def list_orders(user_id: int): return marketplace_service.list_orders(user_id)


@router.get("/admin/orders", response_model=list[AdminOrderResponse])
async def list_orders_for_admin():
    return marketplace_service.list_orders_for_admin()


@router.post("/users/{user_id}/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(user_id: int, request: OrderCreate):
    try: return marketplace_service.create_order(user_id, request)
    except ValueError as error: raise HTTPException(400, str(error)) from error


@router.patch("/users/{user_id}/orders/{order_id}", response_model=OrderResponse)
async def update_order_status(user_id: int, order_id: int, request: OrderStatusUpdate):
    order = marketplace_service.update_order_status(user_id, order_id, request)
    if order is None: raise HTTPException(404, "Order not found")
    return order


@router.get("/admin/payments", response_model=list[PaymentResponse])
async def list_payments_for_admin():
    return marketplace_service.list_payments()


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(request: PaymentCreate): return marketplace_service.create_payment(request)


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment_status(payment_id: int, request: PaymentStatusUpdate):
    payment = marketplace_service.update_payment_status(payment_id, request)
    if payment is None: raise HTTPException(404, "Payment not found")
    return payment


@router.get("/reviews", response_model=list[ReviewResponse])
async def list_reviews():
    return marketplace_service.list_reviews()


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(request: ReviewCreate):
    try:
        return marketplace_service.create_review(request)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error