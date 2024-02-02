from connexion import FlaskApp
from connexion.options import SwaggerUIOptions

options = SwaggerUIOptions(swagger_ui_path="/docs")

app = FlaskApp(__name__, specification_dir = ".", swagger_ui_options=options)
app.add_api("audited_labels_api.yaml", swagger_ui_options=options)

if __name__ == "__main__":
    app.run(port=5001)