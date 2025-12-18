from flask import Flask, render_template, request
import logging
from service.camundaService import CamundaService

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, # Set the desired log level
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()] # Output logs to console
)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        camunda_service = CamundaService(animal="fox")

        camunda_service.setup()

        app.logger.info(f"{camunda_service.base_url}")
        camunda_service.get_token()
        camunda_service.search_process_definitions()

        return render_template('index.html', started=True)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

