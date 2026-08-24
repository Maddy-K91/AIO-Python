# Python FastAPI with Angular Integration Guide

## 🚀 Setup & Installation

### Backend (Python)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables** (`.env` file)
   ```
   DB_SERVER=localhost
   DB_NAME=YourDatabase
   DB_USERNAME=sa
   DB_PASSWORD=YourStrongPassword123
   DB_DRIVER=ODBC Driver 17 for SQL Server
   ```

3. **Start the API server**
   ```bash
   python main.py
   ```
   Server runs at: `http://localhost:8000`

### Project structure

```text
main.py                 # Compatibility server launcher
app/main.py             # FastAPI application setup
app/core/config.py      # Environment-based settings
app/models/             # Domain models and request/response DTOs
app/services/           # Business logic
app/repositories/       # Database queries
app/external/           # External service clients
app/routes/              # HTTP endpoints
tests/                  # Automated tests
```

Database credentials must be provided through `.env`; the application does not
use a real password as a fallback:

```env
DB_SERVER=localhost
DB_NAME=YourDatabase
DB_USERNAME=sa
DB_PASSWORD=YourStrongPassword123
DB_DRIVER=ODBC Driver 17 for SQL Server
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
```

4. **Access API Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### 1. User Registration
- **URL:** `/api/register`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "email": "new.customer@example.com",
    "password": "StrongPassword123",
    "first_name": "New",
    "last_name": "Customer",
    "phone_number": "9876543210"
  }
  ```
- **Success Response (201):**
  ```json
  {
    "success": true,
    "message": "Registration successful",
    "user": {
      "username": "new.customer@example.com"
    }
  }
  ```
- **Duplicate Email Response (409):**
  ```json
  {
    "detail": "A user with this email already exists or registration failed"
  }
  ```

### 2. Admin Login
- **URL:** `/api/admin/login`
- **Method:** `POST`
- **Configuration:** Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`.
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "your-admin-password"
  }
  ```
- **Success Response (200):**
  ```json
  {
    "success": true,
    "message": "Admin login successful",
    "user": {
      "username": "admin",
      "role": "admin"
    }
  }
  ```

### 3. Health Check
- **URL:** `/api/health`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "status": "ok",
    "message": "API is running"
  }
  ```

### 4. Login
- **URL:** `/api/login`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Success Response (200):**
  ```json
  {
    "success": true,
    "message": "Login successful",
    "user": {
      "username": "admin"
    }
  }
  ```
- **Error Response (401):**
  ```json
  {
    "detail": "Invalid username or password"
  }
  ```

---

## 🔄 Angular Integration

### Step 1: Add HttpClientModule

Update `app.config.ts`:
```typescript
import { provideHttpClient } from '@angular/common/http';
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient()
  ]
};
```

### Step 2: Create Auth Service

File: `src/app/services/auth.service.ts`
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  user: { username: string } | null;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  login(username: string, password: string): Observable<LoginResponse> {
    const request: LoginRequest = { username, password };
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, request);
  }

  checkHealth(): Observable<{ status: string; message: string }> {
    return this.http.get<{ status: string; message: string }>(`${this.apiUrl}/health`);
  }
}
```

### Step 3: Use Service in Component

File: `src/app/components/common/header/header.ts`
```typescript
import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './header.html',
  styleUrls: ['./header.css']
})
export class HeaderComponent implements OnInit {
  username = '';
  password = '';
  loading = false;
  message = '';

  constructor(private authService: AuthService) { }

  ngOnInit() {
    // Check API health
    this.authService.checkHealth().subscribe({
      next: (response) => console.log('API Health:', response),
      error: (error) => console.error('API Error:', error)
    });
  }

  login() {
    if (!this.username || !this.password) {
      this.message = 'Please enter credentials';
      return;
    }

    this.loading = true;
    this.authService.login(this.username, this.password).subscribe({
      next: (response) => {
        this.loading = false;
        this.message = response.message;
        console.log('Login successful:', response.user);
      },
      error: (error) => {
        this.loading = false;
        this.message = error.error?.detail || 'Login failed';
      }
    });
  }
}
```

### Step 4: Template Example

File: `src/app/components/common/header/header.html`
```html
<div class="login-container">
  <h2>Login</h2>
  <form>
    <input 
      type="text" 
      [(ngModel)]="username" 
      name="username" 
      placeholder="Username"
    />
    <input 
      type="password" 
      [(ngModel)]="password" 
      name="password" 
      placeholder="Password"
    />
    <button 
      type="button" 
      (click)="login()" 
      [disabled]="loading"
    >
      {{ loading ? 'Logging in...' : 'Login' }}
    </button>
  </form>
  
  <div *ngIf="message" class="message">
    {{ message }}
  </div>
</div>
```

---

## 🔐 CORS Configuration

The API is configured to accept requests from:
- `http://localhost:4200` (Angular dev server)
- `http://localhost:3000` (Alternative frontend)

To add more origins, update `CORS_ORIGINS` in `.env` as a comma-separated list:
```python
CORS_ORIGINS=http://localhost:4200,http://your-domain.com
```

---

## 🧪 Testing with cURL

```bash
# Health check
curl -X GET http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📝 Database Note

The login endpoint currently checks credentials against an MSSQL database table `Users` with:
- `Username` column
- `Password` column (currently plain text - **use hashed passwords in production!**)

## 🛒 Marketplace Database

The complete SQL Server schema is in `database_schema.sql`. Run it after selecting
the database configured by `DB_NAME`:

```sql
USE YourDatabase;
GO

-- Execute database_schema.sql in SQL Server Management Studio or Azure Data Studio.
```

The main tables are:

| Table | Purpose |
| --- | --- |
| `User` | Customer account and login information |
| `Address` | Saved customer delivery addresses |
| `Category` | Product categories and optional parent categories |
| `Product` | Product catalog, prices, and descriptions |
| `ProductImage` | Product image URLs and display order |
| `Inventory` | Available and reserved product quantity |
| `Cart`, `CartItem` | Customer shopping carts |
| `Order`, `OrderItem` | Placed orders and price snapshots |
| `Payment` | Payment method, status, and transaction information |
| `Review` | Product ratings and customer reviews |

The script is safe to run repeatedly: it creates missing tables and indexes but
does not delete existing tables or data. The current login code uses the existing
`User.Email` and `User.Password` columns. Replace `Password` with a password hash
flow before using this application in production.

### Insert demo data

After creating the tables, run `database_seed.sql` in SQL Server Management
Studio or Azure Data Studio. It inserts sample data into every table and prints
a row-count summary at the end:

```sql
USE YourDatabase;
GO

-- Execute database_seed.sql
```

Use these development-only credentials with the login API:

```json
{
  "username": "demo.customer@example.com",
  "password": "Demo@12345"
}
```

The sample catalog contains `Demo Smartphone 5G` and `Demo Wireless Headphones`.
The demo customer already has a saved address, cart items, a delivered order,
and a successful payment record for UI testing.

## 📡 Marketplace APIs for the UI

The API currently provides **16 marketplace operations across 14 URL paths**.
The `user_id` path value is temporary until JWT authentication is added; the UI
should send the logged-in user's ID there.

| Area | Method and URL | UI use |
| --- | --- | --- |
| Categories | `GET /api/categories` | Show category menu |
| Categories | `POST /api/categories` | Admin creates a category |
| Products | `GET /api/products?category_id=1&search=phone` | Product listing and search |
| Products | `GET /api/products/{product_id}` | Product details page |
| Products | `POST /api/products` | Admin adds a product |
| Products | `POST /api/products/upload` | Admin adds a product with a local image file |
| Addresses | `GET /api/users/{user_id}/addresses` | Show saved addresses |
| Addresses | `POST /api/users/{user_id}/addresses` | Add delivery address |
| Cart | `GET /api/users/{user_id}/cart` | Show cart and total |
| Cart items | `POST /api/users/{user_id}/cart/items` | Add product to cart |
| Cart items | `PATCH /api/users/{user_id}/cart/items/{item_id}` | Change quantity |
| Cart items | `DELETE /api/users/{user_id}/cart/items/{item_id}` | Remove item |
| Orders | `GET /api/users/{user_id}/orders` | Order history |
| Orders | `POST /api/users/{user_id}/orders` | Checkout cart |
| Orders | `PATCH /api/users/{user_id}/orders/{order_id}` | Update order status |
| Payments | `POST /api/payments` | Create payment record |
| Payments | `PATCH /api/payments/{payment_id}` | Update payment result |

### Example requests

Add a product to the cart:

```json
POST /api/users/1/cart/items
{
  "product_id": 10,
  "quantity": 2
}
```

Checkout the current cart:

```json
POST /api/users/1/orders
{
  "shipping_address_id": 5
}
```

Upload a product image:

```text
POST /api/products/upload
Content-Type: multipart/form-data

category_id=1
product_name=Demo Camera
product_slug=demo-camera
selling_price=19999
mrp=24999
description=Compact digital camera
brand_name=DemoTech
available_quantity=10
is_active=true
image=<camera.jpg>
```

The image is saved in `media/products` with a generated filename and served at
`/media/products/<generated-filename>`. The response is the same product shape
as `POST /api/products`, for example:

```json
{
  "product_id": 12,
  "category_id": 1,
  "product_name": "Demo Camera",
  "product_slug": "demo-camera",
  "description": "Compact digital camera",
  "brand_name": "DemoTech",
  "selling_price": "19999.00",
  "mrp": "24999.00",
  "available_quantity": 10,
  "is_active": true,
  "image_url": "/media/products/7f2c1a9b3d4e5f67890123456789abcd.jpg"
}
```

Product search returns product price and stock together, so a product card can
show the price, MRP, discount calculation, and availability without another
request. The cart response returns each line total and the complete cart total.

---

## 🚨 Production Checklist

- [ ] Use hashed passwords (bcrypt, argon2)
- [ ] Add JWT token authentication
- [ ] Use HTTPS/SSL
- [ ] Add rate limiting
- [ ] Add input validation & sanitization
- [ ] Set CORS origins to production domain only
- [ ] Use environment-specific configs
- [ ] Add logging & monitoring
- [ ] Add database connection pooling
- [ ] Add API versioning

---

## 🐛 Troubleshooting

**CORS Error?**
- Check that Angular dev server (port 4200) is in CORS allowed origins
- Browser console will show the specific error

**Connection refused?**
- Ensure API is running: `python main.py`
- Check port 8000 is not in use

**Database connection error?**
- Verify `.env` file has correct DB credentials
- Check MSSQL Server is running
- Verify ODBC Driver 17 is installed

---

## 📚 API Documentation

Automatically generated and available at:
- Interactive Docs: `http://localhost:8000/docs`
- Alternative: `http://localhost:8000/redoc`
