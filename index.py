from app import create_app
import webbrowser
import threading
import sys

app = create_app()

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # Open browser in a separate thread when running as an EXE
        threading.Timer(1.5, open_browser).start()
        app.run(debug=False, port=5000)
    else:
        app.run(debug=True, port=5000)
