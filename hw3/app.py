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
        <html>
        <head><title>Movie Reviews</title></head>
        <body>
            <h1>Movie Reviews</h1>
            <a href="{{ url_for('new_review') }}">Add New Review</a>
            <table border="1">
                <tr>
                    <th>Title</th>
                    <th>Rating</th>
                    <th>Actions</th>
                </tr>
                {% for review in reviews %}
                <tr>
                    <td><a href="{{ url_for('view_review', review_id=review.id) }}">{{ review.title }}</a></td>
                    <td>{{ '★' * review.rating }}{{ '☆' * (5 - review.rating) }}</td>
                    <td>
                        <a href="{{ url_for('edit_review', review_id=review.id) }}">Edit</a>
                        <form action="{{ url_for('delete_review', review_id=review.id) }}" method="post" style="display:inline;">
                            <button type="submit">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
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
        <h1>Create New Review</h1>
        <form method="POST">
            Title: <input type="text" name="title" required><br>
            Review: <br><textarea name="text" rows="5" cols="40" required></textarea><br>
            Rating (1-5): <input type="number" name="rating" min="1" max="5" required><br>
            <button type="submit">Submit</button>
        </form>
        <a href="{{ url_for('show_all_reviews') }}">← Back to reviews</a>
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
        <h1>Edit Review</h1>
        <form method="POST">
            Title: <input type="text" name="title" value="{{ review.title }}" required><br>
            Review: <br><textarea name="text" rows="5" cols="40" required>{{ review.text }}</textarea><br>
            Rating (1-5): <input type="number" name="rating" min="1" max="5" value="{{ review.rating }}" required><br>
            <button type="submit">Update</button>
        </form>
        <a href="{{ url_for('show_all_reviews') }}">← Back to reviews</a>
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
        <h1>{{ review.title }}</h1>
        <p class="stars">{{ '★' * review.rating }}{{ '☆' * (5 - review.rating) }}</p>
        <p>{{ review.text }}</p>
        <a href="{{ url_for('show_all_reviews') }}">← Back to reviews</a>
        <style>.stars { color: gold; }</style>
    ''', review=review)


  
# RUN THE FLASK APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure DB is created before running the app
    app.run(debug=True)
