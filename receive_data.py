from flask import Flask
app = Flask(__name__)
from flask import request

@app.route('/post', methods=['GET', 'POST'])
def send_data():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()