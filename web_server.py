from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # You need to expose this server to the internet for Telegram to access it.
    # For testing, you can use a service like ngrok.
    # On Termux, you can use ngrok by installing it and running:
    # ngrok http 5000
    # Then copy the HTTPS URL and use it in your bot.py file.
    app.run(host='0.0.0.0', port=5000, debug=True)
    