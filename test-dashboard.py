from flask import Flask, render_template

app = Flask(__name__)

@app.route('/test')
def test_dashboard():
    """Test the dashboard template rendering"""
    try:
        return render_template('index.html', 
                             current_week=1, 
                             current_year=2024,
                             username='TestUser')
    except Exception as e:
        return f"Template error: {e}"

if __name__ == '__main__':
    print("Testing dashboard template...")
    app.run(debug=True, host='127.0.0.1', port=5001)
