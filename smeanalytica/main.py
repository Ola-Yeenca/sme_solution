"""Main entry point for the SME Analytica application."""

import os
from api.app import init_app

app = init_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
