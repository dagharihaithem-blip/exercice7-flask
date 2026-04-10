from flask import Flask, request, render_template_string
import psycopg2
import os
import logging

# Crée le dossier logs si nécessaire
os.makedirs("logs", exist_ok=True)

# Configure le log
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Démarrage de l'application Flask")

app = Flask(__name__)

# Config PostgreSQL
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "flaskdb")
DB_USER = os.getenv("DB_USER", "flaskuser")
DB_PASS = os.getenv("DB_PASS", "flaskpassword")

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        return conn
    except Exception as e:
        logging.error(f"Erreur connexion DB: {e}")
        return None

# Route principale - affichage de tous les utilisateurs
@app.route('/')
def index():
    logging.info("Requête reçue dans Flask")
    conn = connect_db()
    if not conn:
        return "Connexion à la base de données échouée !"

    cur = conn.cursor()
    # Crée la table si elle n'existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE
        );
    """)
    conn.commit()

    # Lire toutes les données
    cur.execute("SELECT * FROM users ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Affichage HTML simple
    html = """
    <h1>Liste des utilisateurs</h1>
    <ul>
        {% for id, name in users %}
            <li>{{ id }} - {{ name }}</li>
        {% endfor %}
    </ul>
    <p>Pour ajouter un utilisateur, utilisez l'URL : /add_user?name=VotreNom</p>
    """
    return render_template_string(html, users=rows)

# Route pour ajouter un utilisateur via URL
@app.route('/reset_users')
def reset_users():
    logging.info("Réinitialisation de la table users")
    try:
        conn = connect_db()
        if not conn:
            return "Connexion à la base de données échouée !"

        cur = conn.cursor()
        # Supprimer tous les utilisateurs
        cur.execute("DELETE FROM users;")
        # Réinitialiser la séquence pour que les IDs repartent de 1
        cur.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1;")
        # Ajouter Alice, Bob et Haithem
        cur.execute("INSERT INTO users (name) VALUES ('Alice');")
        cur.execute("INSERT INTO users (name) VALUES ('Bob');")
        cur.execute("INSERT INTO users (name) VALUES ('Haithem');")

        conn.commit()
        cur.close()
        conn.close()

        logging.info("Table users réinitialisée avec Alice, Bob et Haithem")
        return "Table users réinitialisée : Alice, Bob et Haithem uniquement."
    except Exception as e:
        logging.error(f"Erreur reset_users: {e}")
        return f"Erreur : {e}"
# Lancer l'application
if __name__ == '__main__':
    logging.info("Démarrage de l'application Flask")
    app.run(host="0.0.0.0", port=5000)