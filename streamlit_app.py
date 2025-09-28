from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key-for-streamlit'

@app.route('/')
def home():
    return """
    <h1>✅ Flask App Working on Streamlit Cloud!</h1>
    <p>Your basic Flask installation is successful.</p>
    <p>You can now gradually add more features.</p>
    """

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)