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

    def test_books_get_returns_200_with_pagination(self):
        """Test that GET /books returns 200 with proper pagination structure"""
        query_string = [('offset', 0),
                        ('limit', 10),
                        ('page', 1),
                        ('per_page', 10)]
        response = self.client.open(
            '/books',
            method='GET',
            query_string=query_string)
        
        self.assert200(response, 'GET /books should return 200')
        
        # Verify response is valid JSON
        data = json.loads(response.data.decode('utf-8'))
        
        # Verify response structure contains required pagination fields
        self.assertIn('pagination', data, 'Response should contain pagination object')
        self.assertIn('items', data, 'Response should contain items array')
        self.assertIn('total', data, 'Response should contain total count')
        
        # Verify pagination fields are correct
        pagination = data['pagination']
        self.assertEqual(pagination['page'], 1, 'Page should be 1')
        self.assertEqual(pagination['per_page'], 10, 'Per page should be 10')
        self.assertGreaterEqual(pagination['total_items'], 0, 'Total items should be >= 0')

    def test_books_get_pagination_limits_per_page(self):
        """Test that per_page is capped at 50 (max allowed)"""
        # Request more than max (50)
        query_string = [('page', 1), ('per_page', 100)]
        response = self.client.open(
            '/books',
            method='GET',
            query_string=query_string)
        
        self.assert200(response)
        data = json.loads(response.data.decode('utf-8'))
        
        # Verify per_page was capped at 50
        self.assertEqual(data['pagination']['per_page'], 50,
                         'per_page should be capped at 50 even if requested higher')

    def test_books_post_creates_book_successfully(self):
        """Test that POST /books creates a new book and returns it"""
        test_isbn = f'test-isbn-{id(self)}'  # Unique ISBN per test run
        body = BooksBody(isbn=test_isbn, book_name='The Great Test', author='Test Author')
        
        response = self.client.open(
            '/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        
        self.assertIn(response.status_code, [200, 201],
                      'POST /books should return 200 or 201')
        
        # Verify created book data
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['isbn'], test_isbn, 'ISBN should match request')
        self.assertEqual(data['book_name'], 'The Great Test', 'Book name should match')
        self.assertEqual(data['author'], 'Test Author', 'Author should match')

    def test_books_post_rejects_missing_required_fields(self):
        """Test that POST /books rejects request without required fields"""
        # Missing author field
        body = BooksBody(isbn='test-isbn-missing', book_name='Missing Author')
        
        response = self.client.open(
            '/books',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        
        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, 400,
                         'POST without required author field should return 400')
        
        error_data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(error_data['status'], 400, 'Error status should be 400')

    def test_books_isbn_get_returns_book_if_exists(self):
        """Test that GET /books/{isbn} returns 200 if book exists"""
        # First create a book
        test_isbn = f'isbn-get-{id(self)}'
        create_body = BooksBody(isbn=test_isbn, book_name='Test Get Book', author='Get Author')
        create_response = self.client.open(
            '/books',
            method='POST',
            data=json.dumps(create_body),
            content_type='application/json')
        
        # Now retrieve it
        get_response = self.client.open(
            f'/books/{test_isbn}',
            method='GET')
        
        self.assert200(get_response, 'GET by existing ISBN should return 200')
        
        data = json.loads(get_response.data.decode('utf-8'))
        self.assertEqual(data['isbn'], test_isbn, 'Retrieved book should have correct ISBN')
        self.assertEqual(data['book_name'], 'Test Get Book', 'Retrieved book should have correct name')

    def test_books_isbn_get_returns_404_for_nonexistent_book(self):
        """Test that GET /books/{isbn} returns 404 if book does not exist"""
        nonexistent_isbn = 'nonexistent-isbn-xyz-999'
        
        response = self.client.open(
            f'/books/{nonexistent_isbn}',
            method='GET')
        
        self.assertEqual(response.status_code, 404,
                         'GET non-existent ISBN should return 404')
        
        error_data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(error_data['status'], 404)

    def test_books_isbn_put_updates_existing_book(self):
        """Test that PUT /books/{isbn} updates book fields"""
        # Create a book
        test_isbn = f'isbn-put-{id(self)}'
        create_body = BooksBody(isbn=test_isbn, book_name='Original Name', author='Original Author')
        self.client.open(
            '/books',
            method='POST',
            data=json.dumps(create_body),
            content_type='application/json')
        
        # Update it
        update_body = BooksIsbnBody(book_name='Updated Name', author='Updated Author')
        response = self.client.open(
            f'/books/{test_isbn}',
            method='PUT',
            data=json.dumps(update_body),
            content_type='application/json')
        
        self.assertEqual(response.status_code, 200,
                         'PUT existing book should return 200')
        
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['book_name'], 'Updated Name', 'Book name should be updated')
        self.assertEqual(data['author'], 'Updated Author', 'Author should be updated')

    def test_books_isbn_put_returns_404_for_nonexistent_book(self):
        """Test that PUT /books/{isbn} returns 404 if book does not exist"""
        nonexistent_isbn = 'nonexistent-put-xyz'
        update_body = BooksIsbnBody(book_name='Updated', author='Updated')
        
        response = self.client.open(
            f'/books/{nonexistent_isbn}',
            method='PUT',
            data=json.dumps(update_body),
            content_type='application/json')
        
        self.assertEqual(response.status_code, 404,
                         'PUT non-existent ISBN should return 404')

    def test_books_isbn_delete_removes_book(self):
        """Test that DELETE /books/{isbn} removes the book"""
        # Create a book
        test_isbn = f'isbn-delete-{id(self)}'
        create_body = BooksBody(isbn=test_isbn, book_name='To Delete', author='Delete Author')
        self.client.open(
            '/books',
            method='POST',
            data=json.dumps(create_body),
            content_type='application/json')
        
        # Delete it
        delete_response = self.client.open(
            f'/books/{test_isbn}',
            method='DELETE')
        
        self.assertEqual(delete_response.status_code, 200,
                         'DELETE existing book should return 200')
        
        # Verify book is gone
        get_response = self.client.open(
            f'/books/{test_isbn}',
            method='GET')
        
        self.assertEqual(get_response.status_code, 404,
                         'Book should not exist after delete')

    def test_books_isbn_delete_returns_404_for_nonexistent_book(self):
        """Test that DELETE /books/{isbn} returns 404 if book does not exist"""
        nonexistent_isbn = 'nonexistent-delete-xyz'
        
        response = self.client.open(
            f'/books/{nonexistent_isbn}',
            method='DELETE')
        
        self.assertEqual(response.status_code, 404,
                         'DELETE non-existent ISBN should return 404')


if __name__ == '__main__':
    import unittest
    unittest.main()
