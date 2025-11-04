import connexion

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.product import Product  # noqa: E501
from swagger_server.models.pagination import Pagination  # noqa: E501
from swagger_server.models.hateoas import HATEOAS  # noqa: E501
from swagger_server.database import db_connection  # noqa: E501
from swagger_server import util


def _ensure_db_connection():
    """Ensure database connection is established"""
    if db_connection.collection is None:
        db_connection.connect()


def _product_from_dict(doc: dict) -> Product:
    """Convert MongoDB document to Product model"""
    return Product(
        id=doc.get('id'),
        product_name=doc.get('product_name'),
        product_code=doc.get('product_code'),
        quantity=doc.get('quantity')
    )


def _product_to_dict(product: Product) -> dict:
    doc = {}
    if product.id is not None:
        doc['id'] = product.id
    if product.product_name is not None:
        doc['product_name'] = product.product_name
    if product.product_code is not None:
        doc['product_code'] = product.product_code
    if product.quantity is not None:
        doc['quantity'] = product.quantity
    return doc


def create_product(body):  # noqa: E501
    """Add a new product

    Create a new product in the database # noqa: E501

    :param body: Add a new product in the store
    :type body: dict | bytes

    :rtype: Product
    """
    try:
        _ensure_db_connection()
        
        if connexion.request.is_json:
            body = Product.from_dict(connexion.request.get_json())  # noqa: E501
        
        if body.product_name is None or body.product_code is None:
            return Error(code=400, message="product_name and product_code are required"), 400
        
        # If id is not provided, generate a new one
        if body.id is None:
            max_doc = db_connection.collection.find_one(sort=[("id", -1)])
            body.id = (max_doc['id'] + 1) if max_doc else 1
        
        product_dict = _product_to_dict(body)
        
        existing = db_connection.collection.find_one({'id': body.id})
        if existing:
            return Error(code=409, message=f"Product with id {body.id} already exists"), 409
        
        db_connection.collection.insert_one(product_dict)
        
        created_product = db_connection.collection.find_one({'id': body.id})
        product = _product_from_dict(created_product)
        links = HATEOAS(links=[
            {"rel": "self", "href": f"/product/{product.id}"},
            {"rel": "update", "href": f"/product/{product.id}"},
            {"rel": "delete", "href": f"/product/{product.id}"},
            {"rel": "list", "href": "/product"}
        ])

        response = InlineResponse2001(product=product, links=links)
        return response, 201

    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500


def delete_product_by_id(product_id):  # noqa: E501
    """Delete a product by id

    Remove a product permanently # noqa: E501

    :param product_id: The product&#x27;s id
    :type product_id: int

    :rtype: InlineResponse2002
    """
    try:
        _ensure_db_connection()
        
        result = db_connection.collection.delete_one({'id': product_id})
        
        if result.deleted_count == 0:
            return Error(code=404, message=f"Product with id {product_id} not found"), 404
        
        response = InlineResponse2002(message=f"Product with id {product_id} deleted successfully")
        return response, 200
        
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500


def get_product(page=None, per_page=None):  # noqa: E501
    """Get a list of products

    Return a list of products # noqa: E501

    :param page: 
    :type page: int
    :param per_page: 
    :type per_page: int

    :rtype: InlineResponse200
    """
    try:
        _ensure_db_connection()
        
        page = page if page is not None and page > 0 else 1
        per_page = per_page if per_page is not None and per_page > 0 else 10
        
        skip = (page - 1) * per_page
        
        total_items = db_connection.collection.count_documents({})
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 0
        
        cursor = db_connection.collection.find({}).skip(skip).limit(per_page)
        products = [_product_from_dict(doc) for doc in cursor]
        
        pagination = Pagination(
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_items=total_items
        )
        
        links_list = [
            {"rel": "self",  "href": "/product?page={}&per_page={}".format(page, per_page)},
        ]

        if page < total_pages:
            links_list.append({"rel": "next", "href": "/product?page={}&per_page={}".format(page+1, per_page)})

        if page > 1:
            links_list.append({"rel": "prev", "href": "/product?page={}&per_page={}".format(page-1, per_page)})

        links = HATEOAS(links=links_list)

        
        response = InlineResponse200(
            products=products,
            pagination=pagination,
            links=links
        )
        return response, 200
        
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500


def get_product_by_id(product_id):  # noqa: E501
    """Get a product by id

    Request a product by id # noqa: E501

    :param product_id: The product&#x27;s id
    :type product_id: int

    :rtype: InlineResponse2001
    """
    try:
        _ensure_db_connection()
        
        product_doc = db_connection.collection.find_one({'id': product_id})
        
        if not product_doc:
            return Error(code=404, message=f"Product with id {product_id} not found"), 404
        
        product = _product_from_dict(product_doc)
        
        links = HATEOAS(links=[
            {"rel": "self", "href": f"/product/{product_id}"},
            {"rel": "update", "href": f"/product/{product_id}"},
            {"rel": "delete", "href": f"/product/{product_id}"},
            {"rel": "list", "href": "/product"}
        ])

        response = InlineResponse2001(product=product, links=links)
        return response, 200
        
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500


def product_product_id_put(product_id, body=None):  # noqa: E501
    """Update a product values by id

    Update a product&#x27;s quantity, name # noqa: E501

    :param product_id: The product&#x27;s id
    :type product_id: int
    :param body: Update a product&#x27;s attribute by product_id
    :type body: dict | bytes

    :rtype: Product
    """
    try:
        _ensure_db_connection()
        
        existing_product = db_connection.collection.find_one({'id': product_id})
        if not existing_product:
            return Error(code=404, message=f"Product with id {product_id} not found"), 404
        
        if connexion.request.is_json:
            body = Product.from_dict(connexion.request.get_json())  # noqa: E501
        
        update_dict = {}
        if body.product_name is not None:
            update_dict['product_name'] = body.product_name
        if body.product_code is not None:
            update_dict['product_code'] = body.product_code
        if body.quantity is not None:
            update_dict['quantity'] = body.quantity
        
        if not update_dict:
            return Error(code=400, message="At least one field must be provided for update"), 400
        
        db_connection.collection.update_one(
            {'id': product_id},
            {'$set': update_dict}
        )
        
        updated_product_doc = db_connection.collection.find_one({'id': product_id})
        updated_product = _product_from_dict(updated_product_doc)
        
        links = HATEOAS(links=[
            {"rel": "self", "href": f"/product/{product_id}"},
            {"rel": "delete", "href": f"/product/{product_id}"},
            {"rel": "list", "href": "/product"}
        ])

        response = InlineResponse2001(product=updated_product, links=links)
        return response, 200

        
    except Exception as e:
        return Error(code=500, message=f"Internal server error: {str(e)}"), 500
