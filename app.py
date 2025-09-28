from run import app

# This file serves as an entry point for Streamlit Cloud
# It imports the Flask app from run.py

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)