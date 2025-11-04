import connexion
import six

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.product import Product  # noqa: E501
from swagger_server import util


def create_product(body):  # noqa: E501
    """Add a new product

    Create a new product in the database # noqa: E501

    :param body: Add a new product in the store
    :type body: dict | bytes

    :rtype: Product
    """
    if connexion.request.is_json:
        body = Product.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_product_by_id(product_id):  # noqa: E501
    """Delete a product by id

    Remove a product permanently # noqa: E501

    :param product_id: The product&#x27;s id
    :type product_id: int

    :rtype: InlineResponse2002
    """
    return 'do some magic!'


def get_product(page=None, per_page=None):  # noqa: E501
    """Get a list of products

    Return a list of products # noqa: E501

    :param page: 
    :type page: int
    :param per_page: 
    :type per_page: int

    :rtype: InlineResponse200
    """
    return 'do some magic!'


def get_product_by_id(product_id):  # noqa: E501
    """Get a product by id

    Request a product by id # noqa: E501

    :param product_id: The product&#x27;s id
    :type product_id: int

    :rtype: InlineResponse2001
    """
    return 'do some magic!'


def product_product_id_put(product_id, body=None):  # noqa: E501
    """Update a product values by id

    Update a product&#x27;s quantity, name # noqa: E501

    :param product_id: The product&#x27;s id
    :type product_id: int
    :param body: Update a product&#x27;s attribute by product_id
    :type body: dict | bytes

    :rtype: Product
    """
    if connexion.request.is_json:
        body = Product.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
