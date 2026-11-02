from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # flashed messages ke liye zaroori hai

@app.route('/user')
def home():
    return render_template('index.html')

@app.route('/')
def user():
    # Abhi ke liye dummy customer bhej rahe hain taaki screen clean dikhe
    dummy_customer = {'name': 'Bhaskar', 'phone_number': 9876543210}
    return render_template('user.html', customer=dummy_customer)

if __name__ == '__main__':
    app.run(debug=True, port=5000)