from flask import Flask, render_template
from flask_cors import CORS
# Main application entry point
from blueprints.chat import chat_bp

app = Flask(__name__)

# Configurar CORS para permitir requisições do frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "https://portfolio-frontend-green-zeta.vercel.app", "https://portfolio-backend-iota-rose.vercel.app"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Registrar o blueprint com o prefixo /api
app.register_blueprint(chat_bp, url_prefix='/api')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Rodar em debug mode para desenvolvimento setup
    app.run(debug=True, host='0.0.0.0', port=5000)
