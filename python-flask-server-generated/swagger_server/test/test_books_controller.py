# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.book import Book  # noqa: E501
from swagger_server.models.books_body import BooksBody  # noqa: E501
from swagger_server.models.books_isbn_body import BooksIsbnBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_books_get(self):
        """Test case for books_get

        List books with pagination
        """
        query_string = [('offset', 1),
                        ('limit', 100),
                        ('page', 2),
                        ('per_page', 50)]
        response = self.client.open(
            '/books',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_delete(self):
        """Test case for books_isbn_delete

        Delete a book by ISBN
        """
        response = self.client.open(
            '/books/{isbn}'.format(isbn='isbn_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_get(self):
        """Test case for books_isbn_get

        Get a book by ISBN
        """
        response = self.client.open(
            '/books/{isbn}'.format(isbn='isbn_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_isbn_put(self):
        """Test case for books_isbn_put

        Update a book by ISBN
        """
        body = BooksIsbnBody()
        response = self.client.open(
            '/books/{isbn}'.format(isbn='isbn_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_post(self):
        """Test case for books_post

        Create a new book
        """
        body = BooksBody()
        response = self.client.open(
            '/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
