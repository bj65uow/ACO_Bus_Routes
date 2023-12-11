from plot_nodes import plot, generate_map
from flask import Flask

figure = generate_map(plot())

app = Flask(__name__)

# Show map with bus stop info full screen web server
@app.route("/")
def fullscreen():
    return figure.get_root().render()

if __name__ == "__main__":
    app.run(debug=True)