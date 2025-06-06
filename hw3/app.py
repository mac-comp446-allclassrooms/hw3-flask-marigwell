from flask import Flask, redirect, render_template_string, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Initialize Flask App
app = Flask(__name__)

# Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///thereviews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with Declarative Base
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define the Review model using `Mapped` and `mapped_column`
class Review(db.Model):
    __tablename__ = "thereviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    def __init__(self, title: str, text: str, rating: int):
        self.title = title
        self.text = text
        self.rating = rating

# DATABASE UTILITY CLASS
class Database:
    def __init__(self):
        pass

    def get(self, review_id: int = None):
        """Retrieve all reviews or a specific review by ID."""
        if review_id:
            return db.session.get(Review, review_id)
        return db.session.query(Review).all()

    def create(self, title: str, text: str, rating: int):
        """Create a new review."""
        new_review = Review(title=title, text=text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

    def update(self, review_id: int, title: str, text: str, rating: int):
        """Update an existing review."""
        review = self.get(review_id)
        if review:
            review.title = title
            review.text = text
            review.rating = rating
            db.session.commit()

    def delete(self, review_id: int):
        """Delete a review."""
        review = self.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()

db_manager = Database()  # Create a database manager instance

# Initialize database with sample data
@app.before_request
def setup():
    with app.app_context():
        db.create_all()
        if not db_manager.get():  # If database is empty, add a sample entry
            db_manager.create("Mr. Pumpkin Man", "This is a pretty bad movie", 4)
            print("Database initialized with sample data!")

# Reset the database
@app.route('/reset-db', methods=['GET', 'POST'])
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset: success!")
    return "Database has been reset!", 200


# ROUTES
"""You will add all of your routes below, there is a sample one which you can use for testing"""

@app.route('/')
def show_all_reviews():
    reviews = db_manager.get()
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Movie Reviews</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: url('{{ url_for('static', filename='ghibli.png') }}') no-repeat center fixed;
                background-size: cover;
                font-family: sans-serif;
                padding: 2rem;
                color: #333;
            }
            .review-table {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                padding: 1rem;
            }
            .stars {
                color: gold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center text-white mb-4"> Ghibli Movie Theater Reviews</h1>
            <div class="text-center mb-3">
                <a href="{{ url_for('new_review') }}" class="btn btn-success">Add New Review</a>
            </div>
            <div class="review-table">
                <table class="table table-hover text-center align-middle">  
                    <thead class="table-dark">
                        <tr>
                            <th>Title</th>
                            <th>Rating</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for review in reviews %}
                        <tr>
                            <td><a href="{{ url_for('view_review', review_id=review.id) }}">{{ review.title }}</a></td>
                            <td class="stars">{{ '★' * review.rating }}{{ '☆' * (5 - review.rating) }}</td>
                            <td>
                                <a href="{{ url_for('edit_review', review_id=review.id) }}" class="btn btn-sm btn-primary">Edit</a>
                                <button onclick="deleteReview({{ review.id }}, this)" class="btn btn-sm btn-danger">Delete</button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        <script>
            function deleteReview(id, el) {
                fetch(`/delete/${id}`, { method: 'POST' })
                .then(res => {
                    if (res.ok) {
                        el.closest('tr').remove();
                    } else {
                        alert('Error deleting review.');
                    }
                });
            }
        </script>
    </body>
    </html>
    ''', reviews=reviews)

@app.route('/new', methods=['GET', 'POST'])
def new_review():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        rating = int(request.form['rating'])
        db_manager.create(title, text, rating)
        return redirect(url_for('show_all_reviews'))

    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Create Review</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: url('{{ url_for('static', filename='ghibli.png') }}') no-repeat center fixed;
                background-size: cover;
                font-family: sans-serif;
                padding: 2rem;
            }
            .form-card {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                max-width: 600px;
                margin: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="form-card mt-5">
                <h2 class="text-center mb-4"> Create New Review</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Title</label>
                        <input type="text" class="form-control" name="title">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Review</label>
                        <textarea class="form-control" name="text" rows="5"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Rating (1-5)</label>
                        <input type="number" class="form-control" name="rating" min="1" max="5">
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-success">Submit Review</button>
                    </div>
                </form>
                <div class="text-center mt-3">
                    <a href="{{ url_for('show_all_reviews') }}" class="btn btn-link">← Back to Reviews</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/edit/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    review = db_manager.get(review_id)
    if not review:
        return "Review not found", 404

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        rating = int(request.form['rating'])
        db_manager.update(review_id, title, text, rating)
        return redirect(url_for('show_all_reviews'))

    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Edit Review</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: url('{{ url_for('static', filename='ghibli.png') }}') no-repeat center fixed;
                background-size: cover;
                font-family: sans-serif;
                padding: 2rem;
            }
            .form-card {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                max-width: 600px;
                margin: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="form-card mt-5">
                <h2 class="text-center mb-4">Edit Review</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Title</label>
                        <input type="text" class="form-control" name="title" value="{{ review.title }}" >
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Review</label>
                        <textarea class="form-control" name="text" rows="5" >{{ review.text }}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Rating (1-5)</label>
                        <input type="number" class="form-control" name="rating" min="1" max="5" value="{{ review.rating }}" >
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">Update Review</button>
                    </div>
                </form>
                <div class="text-center mt-3">
                    <a href="{{ url_for('show_all_reviews') }}" class="btn btn-link">← Back to Reviews</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', review=review)

@app.route('/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    db_manager.delete(review_id)
    return '', 204

@app.route('/review/<int:review_id>')
def view_review(review_id):
    review = db_manager.get(review_id)
    if not review:
        return "Review not found", 404

    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <title>{{ review.title }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: url('{{ url_for('static', filename='ghibli.png') }}') no-repeat center fixed;
                background-size: cover;
                font-family: sans-serif;
                padding: 2rem;
                color: #333;
            }
            .review-card {
                background-color: rgba(255, 255, 255, 0.85);
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                padding: 2rem;
                max-width: 600px;
                margin: auto;
            }
            .stars {
                color: gold;
                font-size: 1.5rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center text-white mb-4">Review Details</h1>
            <div class="review-card text-center">
                <h2>{{ review.title }}</h2>
                <p class="stars">{{ '★' * review.rating }}{{ '☆' * (5 - review.rating) }}</p>
                <p>{{ review.text }}</p>
                <a href="{{ url_for('show_all_reviews') }}" class="btn btn-primary mt-3">← Back to reviews</a>
            </div>
        </div>
    </body>
    </html>
    ''', review=review)


  
# RUN THE FLASK APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure DB is created before running the app
    app.run(debug=True)
