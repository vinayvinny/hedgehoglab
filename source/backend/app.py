import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection parameters from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/app_db')


def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True  # Automatically commit transactions
    return conn


def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the items table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'items'
                );
            """)
            table_exists = cur.fetchone()[0]
            
            # Create table if it doesn't exist
            if not table_exists:
                cur.execute("""
                    CREATE TABLE items (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                print("Items table created successfully")
                
                # Add some sample data
                cur.execute("""
                    INSERT INTO items (name) VALUES 
                    ('Sample Item 1'),
                    ('Sample Item 2'),
                    ('Sample Item 3');
                """)
                print("Sample data inserted")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({"status": "healthy"})


@app.route('/api/items', methods=['GET'])
def get_items():
    """Retrieve all items from the database"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM items ORDER BY created_at DESC")
            items = cur.fetchall()
            
            # Format the results as a list of dictionaries
            formatted_items = []
            for item in items:
                formatted_items.append({
                    "id": item[0],
                    "name": item[1],
                    "created_at": item[2].isoformat() if item[2] else None
                })
            
            return jsonify(formatted_items)
    except Exception as e:
        print(f"Error fetching items: {e}")
        return jsonify({"error": "Failed to fetch items"}), 500
    finally:
        conn.close()


@app.route('/api/items', methods=['POST'])
def add_item():
    """Add a new item to the database"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    name = data['name']
    if not name.strip():
        return jsonify({"error": "Name cannot be empty"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO items (name) VALUES (%s) RETURNING id, name, created_at",
                (name,)
            )
            new_item = cur.fetchone()
            
            return jsonify({
                "id": new_item[0],
                "name": new_item[1],
                "created_at": new_item[2].isoformat() if new_item[2] else None
            }), 201
    except Exception as e:
        print(f"Error adding item: {e}")
        return jsonify({"error": "Failed to add item"}), 500
    finally:
        conn.close()


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item from the database"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))
            deleted = cur.fetchone()
            
            if deleted:
                return jsonify({"message": f"Item {item_id} deleted successfully"}), 200
            else:
                return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        print(f"Error deleting item: {e}")
        return jsonify({"error": "Failed to delete item"}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    # Initialize the database on startup
    init_db()
    
    # Run the Flask application
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)