from flask import Flask, request, jsonify
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Retrieve environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'exampledb')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

# Configure Redis
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

# Configure PostgreSQL
conn = psycopg2.connect(
    dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST
)
conn.autocommit = True
cursor = conn.cursor(cursor_factory=RealDictCursor)

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = data.get('id')
    user_info = data.get('info')

    # Write to Redis
    redis_client.set(user_id, user_info)

    # Write to PostgreSQL
    cursor.execute("INSERT INTO users (id, info) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET info = EXCLUDED.info;", (user_id, user_info))

    return jsonify({'status': 'success', 'message': 'User created/updated successfully.'}), 200

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    # Try to read from Redis
    user_info = redis_client.get(user_id)
    if user_info is not None:
        app.logger.info("Retrieved from Redis: %s", user_info.decode())
        return jsonify({'id': user_id, 'info': user_info.decode(), 'source': 'redis'}), 200

    # Fallback to PostgreSQL if not found in Redis
    cursor.execute("SELECT info FROM users WHERE id = %s;", (user_id,))
    result = cursor.fetchone()
    if result:
        # Update Redis with the value from the database
        redis_client.set(user_id, result['info'])
        app.logger.info("Retrieved from PostgreSQL: %s", result['info'])
        return jsonify({'id': user_id, 'info': result['info'], 'source': 'psql'}), 200

    app.logger.warning("User not found")
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)