from flask import Flask, request, jsonify, make_response

dummy_data = {
    "books" : [
        {
            'isbn' : 'abcde',
            'name' : 'Python book'
        },
        {
            'isbn' : 'defs',
            'name' : 'C++ book'
        }
    ],
    "copies" : [
        {
            'id' : 1,
            'isbn' : 'abcde',
            'is_rented' : False
        },
        {
            'id' : 2,
            'isbn' : 'abcde',
            'is_rented' : True
        },
        {
            'id' : 3,
            'isbn' : 'defs',
            'is_rented' : False
        }
    ]
}

app = Flask(__name__)

API_TOKEN = "my-secret-token"

def with_cache(response, max_age=60):
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    return response

# Stateless
def require_token(func): 
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/books', methods=['GET'])
@require_token
def get_all_books():
    try:
        resp = make_response(jsonify({
            "response" : {
                "books" : dummy_data.get('books')
            }
        }), 200)
        return with_cache(resp)
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/books/<isbn>', methods=['GET'])
@require_token
def get_book_by_isbn(isbn):
    try:
        for book in dummy_data.get('books'):
            if book.get('isbn') == isbn:
                resp = make_response(jsonify({
                    "response" : {
                        "book" : book
                    }
                }), 200)
                return with_cache(resp)
        return jsonify({'error' : 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/copies', methods=['GET'])
@require_token
def get_all_copies():
    try:
        resp = make_response(jsonify({
            "response" : {
                "copies" : dummy_data.get('copies')
            }
        }), 200)
        return with_cache(resp)
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/copies/<int:copy_id>', methods=['GET'])
@require_token
def get_copy_by_id(copy_id):
    try:
        for copy in dummy_data.get('copies'):
            if copy.get('id') == copy_id:
                resp = make_response(jsonify({
                    "response" : {
                        "copy" : copy
                    }
                }), 200)
                return with_cache(resp)
        return jsonify({'error' : 'Copy not found'}), 404
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/copies/<isbn>', methods=['GET'])
@require_token
def get_copies_by_book(isbn):
    try:
        copies_list = [copy for copy in dummy_data.get('copies') if copy.get('isbn') == isbn]
        resp = make_response(jsonify({
            "response" : {
                "copies" : copies_list
            }
        }), 200)
        return with_cache(resp)
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1234)
