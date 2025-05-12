
from flask import Flask, request, render_template_string
import requests
import pandas as pd
import os

# Configuration
BEARER_TOKEN = "4QwVfmPiGf4NMpAIEWp6phks307DZ41UdsvguBOKOeJMCBs8"  # Replace with your actual HOBOlink API token
LOGGER_SN = "20777720"                 # Replace with your actual logger serial number
BASE_URL = "https://api.hobolink.licor.cloud/v1/data"

app = Flask(__name__)

# Function to fetch data from HOBOlink API
def fetch_data(start_date, end_date):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "loggers": LOGGER_SN,
        "start_date_time": f"{start_date} 00:00:00",
        "end_date_time": f"{end_date} 23:59:59"
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        return pd.DataFrame(data) if data else pd.DataFrame()
    else:
        return f"Error {response.status_code}: {response.text}"

# HTML template
HTML = """
<!doctype html>
<title>HOBOlink Weather</title>
<h2>HOBOlink Weather Data Viewer</h2>
<form method="POST">
  Start Date: <input type="date" name="start_date" required>
  End Date: <input type="date" name="end_date" required>
  <input type="submit" value="Fetch">
</form>
{% if table %}
  <h3>Data Results</h3>
  {{ table|safe }}
{% elif error %}
  <p style="color: red;">{{ error }}</p>
{% endif %}
"""

# Flask routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        result = fetch_data(start, end)
        if isinstance(result, pd.DataFrame):
            if result.empty:
                return render_template_string(HTML, table=None, error="No data found for this period.")
            return render_template_string(HTML, table=result.to_html(classes="table table-striped", index=False))
        else:
            return render_template_string(HTML, table=None, error=result)
    return render_template_string(HTML)

# Run on Render-compatible port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
