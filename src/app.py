from flask import Flask, render_template
import webbrowser

app = Flask(__name__)

# Default page
@app.route("/")
def hello():
	return render_template('home.html')

if __name__ == "__main__":
    webbrowser.open_new('http://127.0.0.1:5000/')
    app.run(port=5000, debug=True, use_reloader=False)