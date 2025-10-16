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

@app.route('/books', methods=['GET'])
def get_all_books():
    try:
        return jsonify({
            "response" : {
                "books" : dummy_data.get('books')
            }
        }), 200
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/books/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    try:
        for book in dummy_data.get('books'):
            if book.get('isbn') == isbn:
                return jsonify({
                    "response" : {
                        "book" : book
                    }
                }), 200
        return jsonify({'error' : 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

# Copies endpoints
@app.route('/copies', methods=['GET'])
def get_all_copies():
    try:
        return jsonify({
            "response" : {
                "copies" : dummy_data.get('copies')
            }
        }), 200
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/copies/<int:copy_id>', methods=['GET'])
def get_copy_by_id(copy_id):
    try:
        for copy in dummy_data.get('copies'):
            if copy.get('id') == copy_id:
                return jsonify({
                    "response" : {
                        "copy" : copy
                    }
                }), 200
        return jsonify({'error' : 'Copy not found'}), 404
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

@app.route('/copies/<isbn>', methods=['GET'])
def get_copies_by_book(isbn):
    try:
        copies_list = [copy for copy in dummy_data.get('copies') if copy.get('isbn') == isbn]
        return jsonify({
            "response" : {
                "copies" : copies_list
            }
        }), 200
    except Exception as e:
        return jsonify({'error' : str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1234)
