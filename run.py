from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Get the PORT variable from Render, otherwise 5000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)