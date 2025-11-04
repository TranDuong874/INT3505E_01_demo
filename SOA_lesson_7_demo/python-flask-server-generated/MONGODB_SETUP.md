# MongoDB Setup Instructions

## Installation

1. Install MongoDB dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure MongoDB is running on your system:
   - Default connection: `mongodb://localhost:27017/`
   - Default database: `product_db`

## Configuration

The application loads configuration from a `.env` file in the project root. Create a `.env` file with the following variables:

- `DATABASE`: MongoDB connection string (required)
- `MONGODB_DATABASE`: Database name (optional, default: `product_db`)

Example `.env` file:
```env
DATABASE=mongodb://localhost:27017/
MONGODB_DATABASE=product_db
```

For MongoDB Atlas (cloud):
```env
DATABASE=mongodb+srv://username:password@cluster.mongodb.net/?appName=AppName
MONGODB_DATABASE=product_db
```

**Note**: The application will also check environment variables if `.env` file is not found, and will fall back to default values if neither is set.

## Running the Application

```bash
python -m swagger_server
```

The application will:
- Connect to MongoDB on startup
- Create a `products` collection automatically
- Create an index on the `id` field for faster lookups

## API Endpoints

All endpoints are now fully implemented with MongoDB:

- `POST /product` - Create a new product
- `GET /product` - Get a list of products (with pagination)
- `GET /product/{product_id}` - Get a product by ID
- `PUT /product/{product_id}` - Update a product
- `DELETE /product/{product_id}` - Delete a product

## MongoDB Structure

Products are stored in the `products` collection with the following structure:
```json
{
  "id": 1,
  "product_name": "Product Name",
  "product_code": 12345,
  "quantity": 10
}
```

The `id` field is unique and indexed for fast lookups.
