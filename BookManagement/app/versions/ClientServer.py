from flask import Flask, request, jsonify

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

# Version 1: ClientServer
# Code statisfy client-server architecture principle, but doesn't have uniform interface
@app.route('/getBooks', methods=['GET'])
def get_all_books():
    try:
        return jsonify({
            "response" : {
                "books" : list(dummy_data.get('books'))
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/getBooks/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    try: 
        for book in dummy_data.get('books'):
            if book.get('isbn') == isbn:
                return jsonify({
                    'response' : {
                        "book" : book
                    }
                }), 200
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/getBooks/<isbn>/copies', methods=['GET'])
def get_book_copies(isbn):
    try:
        copies_list = [copy for copy in dummy_data.get('copies') if copy.get('isbn') == isbn]
        return jsonify({
            "response" : {
                "copies" : copies_list
            }
        }), 200
    except Exception as e:  
        return jsonify({
            'error' : str(e)
        }), 400

if __name__ == '__main__':
        app.run(host="0.0.0.0", port=1234)
