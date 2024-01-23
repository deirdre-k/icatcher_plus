from connexion import FlaskApp

import app

REACT_BUILD_FOLDER = str(
    Path(Path(__file__).parent.parent, "frontend", "build").absolute()
)
REACT_APP_FILE = "index.html"

app = FlaskApp(__name__, static_folder=REACT_BUILD_FOLDER)
app.add_api("audited_labels_api.yaml")

def run_app(port=5001, debug=False):
    app.run(port=port, debug=debug)

if __name__ == "__main__":
    app.run(debug=True)