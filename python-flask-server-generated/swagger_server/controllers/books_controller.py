import connexion
import six

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.books_body import BooksBody  # noqa: E501
from swagger_server.models.books_isbn_body import BooksIsbnBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server import util


def books_get(offset=None, limit=None, page=None, per_page=None):  # noqa: E501
    """List books with pagination

     # noqa: E501

    :param offset: Offset for pagination (starting from 0)
    :type offset: int
    :param limit: Number of items per page
    :type limit: int
    :param page: Page number for pagination
    :type page: int
    :param per_page: Number of items per page
    :type per_page: int

    :rtype: InlineResponse200
    """
    return 'do some magic!'


def books_isbn_delete(isbn):  # noqa: E501
    """Delete a book by ISBN

     # noqa: E501

    :param isbn: 
    :type isbn: str

    :rtype: None
    """
    return 'do some magic!'


def books_isbn_get(isbn):  # noqa: E501
    """Get a book by ISBN

     # noqa: E501

    :param isbn: 
    :type isbn: str

    :rtype: Book
    """
    return 'do some magic!'


def books_isbn_put(body, isbn):  # noqa: E501
    """Update a book by ISBN

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param isbn: 
    :type isbn: str

    :rtype: Book
    """
    if connexion.request.is_json:
        body = BooksIsbnBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def books_post(body):  # noqa: E501
    """Create a new book

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Book
    """
    if connexion.request.is_json:
        body = BooksBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
