from flask import Flask, flash, request, render_template, redirect, url_for, jsonify
from flask_login import LoginManager, current_user, login_required
from datetime import datetime
from model import db, Book, Borrower, Transaction, User
from config import Config
from login import auth  # Import the auth blueprint from login.py
from flask import Flask
from config import Config
# Initialize the Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(Config)

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Set the login view for Flask-Login

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register the auth blueprint with the app
app.register_blueprint(auth, url_prefix='/auth')  # All auth routes will be prefixed with /auth

# Create the database and tables if they don't already exist
with app.app_context():
    db.create_all()

# Home route: Redirect to books list if authenticated, or to login if not
@app.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect to the list of books page if the user is authenticated
        return redirect(url_for('get_books'))
    else:
        # Redirect to the login page if the user is not authenticated
        return redirect(url_for('auth.login'))

# Route to display the list of books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return render_template('list_book.html', books=books)

# Route to add a new book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Create a new book instance using form data
        new_book = Book(
            title=request.form.get('title'),
            author=request.form.get('author'),
            isbn=request.form.get('isbn')
        )
        # Add the new book to the database and commit the changes
        db.session.add(new_book)
        db.session.commit()
        # Redirect to the list of books
        return redirect(url_for('get_books'))
    # Render the add book form
    return render_template('add_book.html')

# Route to update a book's information
@app.route('/update_book/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    # Fetch the book by ID
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        # Update book information from form data
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.isbn = request.form.get('isbn')
        # Commit the changes to the database
        db.session.commit()
        # Redirect to the list of books
        return redirect(url_for('get_books'))
    # Render the update book form with the current book's data
    return render_template('update_book.html', book=book)

# Route to borrow a book
@app.route('/borrow_book/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        # Fetch borrower's name and email from the form
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Try to find the borrower by email
        borrower = Borrower.query.filter_by(email=email).first()
        
        # If the borrower doesn't exist, create a new borrower
        if not borrower:
            borrower = Borrower(name=name, email=email)
            db.session.add(borrower)
            db.session.commit()
        
        # Check if the book is available for borrowing
        if not book.available:
            # Return an error if the book is not available
            flash('The book is currently unavailable.', 'error')
            return redirect(url_for('get_books'))

        # Create a new transaction for the borrowed book
        transaction = Transaction(book_id=book.id, borrower_id=borrower.id)
        db.session.add(transaction)
        
        # Update the book's availability status
        book.available = False
        db.session.commit()
        
        # Redirect to the list of books
        return redirect(url_for('get_books'))

    # Render the borrow book form with the selected book
    return render_template('borrow_book.html', book=book)

# Route to return a borrowed book
@app.route('/return_book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    try:
        # Fetch the ongoing transaction for the book that is being returned
        transaction = Transaction.query.filter_by(book_id=book_id, return_date=None).first_or_404()
        
        # Set the return date to the current date and time
        transaction.return_date = datetime.utcnow()
        
        # Find the book and mark it as available
        book = Book.query.get_or_404(book_id)
        book.available = True
        
        # Commit the changes to the database
        db.session.commit()
        
        # Redirect to the list of books
        return redirect(url_for('get_books'))
    except Exception as e:
        # Log the error and return a generic error response
        flash('An error occurred while processing the return request.', 'error')
        print(f"Error occurred: {e}")
        return redirect(url_for('get_books'))
    
# Route to delete a book
@app.route('/delete_book/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('get_books'))


# Entry point for running the Flask application
if __name__ == '__main__':
    app.run(debug=True)
