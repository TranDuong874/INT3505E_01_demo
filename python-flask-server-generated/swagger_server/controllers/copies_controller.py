import connexion
import six

from swagger_server.models.copies_copy_id_body import CopiesCopyIdBody  # noqa: E501
from swagger_server.models.copy import Copy  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.isbn_copies_body import IsbnCopiesBody  # noqa: E501
from swagger_server import util


def books_isbn_copies_copy_id_delete(isbn, copy_id):  # noqa: E501
    """Delete a copy by copy ID for a book

     # noqa: E501

    :param isbn: 
    :type isbn: str
    :param copy_id: 
    :type copy_id: str

    :rtype: None
    """
    return 'do some magic!'


def books_isbn_copies_copy_id_get(isbn, copy_id):  # noqa: E501
    """Get a copy by copy ID for a book

     # noqa: E501

    :param isbn: 
    :type isbn: str
    :param copy_id: 
    :type copy_id: str

    :rtype: Copy
    """
    return 'do some magic!'


def books_isbn_copies_copy_id_put(body, isbn, copy_id):  # noqa: E501
    """Update a copy by copy ID for a book

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param isbn: 
    :type isbn: str
    :param copy_id: 
    :type copy_id: str

    :rtype: Copy
    """
    if connexion.request.is_json:
        body = CopiesCopyIdBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def books_isbn_copies_get(isbn):  # noqa: E501
    """List copies of a book by ISBN

     # noqa: E501

    :param isbn: 
    :type isbn: str

    :rtype: List[Copy]
    """
    return 'do some magic!'


def books_isbn_copies_post(body, isbn):  # noqa: E501
    """Create a new copy for a book

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param isbn: 
    :type isbn: str

    :rtype: Copy
    """
    if connexion.request.is_json:
        body = IsbnCopiesBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
