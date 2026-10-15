"""Start the SkillSight Flask application for local development."""

import os
import sys

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.app import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n========================================================")
    print(f"SkillSight AI Backend starting on http://127.0.0.1:{port}")
    print(f"API endpoints available under http://127.0.0.1:{port}/api/v1")
    print(f"========================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
