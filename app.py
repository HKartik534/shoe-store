from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "shoe_store_secret_key"

DATABASE = "database.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    # Add products only if database is empty
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    if count == 0:

        products = [
            (
                "Air Runner",
                "Running",
                2499,
                "shoe1.jpg",
                "Lightweight running shoes designed for everyday comfort."
            ),
            (
                "Street Flex",
                "Casual",
                1999,
                "shoe2.jpg",
                "Stylish casual shoes perfect for everyday use."
            ),
            (
                "Urban Sport",
                "Sports",
                2999,
                "shoe3.jpg",
                "Comfortable sports shoes for active lifestyles."
            ),
            (
                "Classic White",
                "Sneakers",
                1799,
                "shoe4.jpg",
                "Clean and simple white sneakers for a modern look."
            )
        ]

        conn.executemany("""
            INSERT INTO products
            (name, category, price, image, description)
            VALUES (?, ?, ?, ?, ?)
        """, products)

    conn.commit()
    conn.close()


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    conn = get_db()
    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products
    )


# ---------------- PRODUCT PAGE ----------------

@app.route("/product/<int:product_id>")
def product(product_id):

    conn = get_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "product.html",
        product=product
    )


# ---------------- ADD TO CART ----------------

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", [])

    cart.append(product_id)

    session["cart"] = cart

    return redirect(url_for("cart"))


# ---------------- CART ----------------

@app.route("/cart")
def cart():

    cart = session.get("cart", [])

    products = []

    if cart:

        conn = get_db()

        for product_id in cart:

            product = conn.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,)
            ).fetchone()

            if product:
                products.append(product)

        conn.close()

    total = sum(product["price"] for product in products)

    return render_template(
        "cart.html",
        products=products,
        total=total
    )


# ---------------- CHECKOUT ----------------

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart = session.get("cart", [])

    if not cart:
        return redirect(url_for("home"))

    conn = get_db()

    products = []

    for product_id in cart:

        product = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product:
            products.append(product)

    total = sum(product["price"] for product in products)

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        address = request.form["address"]

        conn.execute("""
            INSERT INTO orders
            (customer_name, email, address, total)
            VALUES (?, ?, ?, ?)
        """, (name, email, address, total))

        conn.commit()
        conn.close()

        session["cart"] = []

        return """
        <div style="font-family: Arial; text-align:center; padding:100px;">
            <h1>🎉 Order Placed Successfully!</h1>
            <p>Thank you for shopping with us.</p>
            <a href="/" style="color:#111;">Continue Shopping</a>
        </div>
        """

    conn.close()

    return render_template(
        "checkout.html",
        products=products,
        total=total
    )


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)