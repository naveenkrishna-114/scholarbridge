import os
from dotenv import load_dotenv

# Load production environment variables if .env is present
load_dotenv()

from app import create_app

# Set production environment as default for WSGI servers unless explicitly overridden
config_env = os.environ.get("FLASK_ENV", "production")
application = create_app(config_env)
app = application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
