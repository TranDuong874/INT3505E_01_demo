# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.copies_copy_id_body import CopiesCopyIdBody  # noqa: E501
from swagger_server.models.copy import Copy  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.isbn_copies_body import IsbnCopiesBody  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCopiesController(BaseTestCase):
    """CopiesController integration test stubs"""

    def test_books_isbn_copies_copy_id_delete(self):
        """Test case for books_isbn_copies_copy_id_delete

        Delete a copy by copy ID for a book
        """
        response = self.client.open(
            '/books/{isbn}/copies/{copy_id}'.format(isbn='isbn_example', copy_id='copy_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_copies_copy_id_get(self):
        """Test case for books_isbn_copies_copy_id_get

        Get a copy by copy ID for a book
        """
        response = self.client.open(
            '/books/{isbn}/copies/{copy_id}'.format(isbn='isbn_example', copy_id='copy_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_copies_copy_id_put(self):
        """Test case for books_isbn_copies_copy_id_put

        Update a copy by copy ID for a book
        """
        body = CopiesCopyIdBody()
        response = self.client.open(
            '/books/{isbn}/copies/{copy_id}'.format(isbn='isbn_example', copy_id='copy_id_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_copies_get(self):
        """Test case for books_isbn_copies_get

        List copies of a book by ISBN
        """
        response = self.client.open(
            '/books/{isbn}/copies'.format(isbn='isbn_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_copies_post(self):
        """Test case for books_isbn_copies_post

        Create a new copy for a book
        """
        body = IsbnCopiesBody()
        response = self.client.open(
            '/books/{isbn}/copies'.format(isbn='isbn_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
