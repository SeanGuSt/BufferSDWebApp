"""
Routes and views for the flask application.
"""
from flask import render_template, request
from BufferSDWebApp import app
@app.route('/')
@app.route('/form', methods = ['POST', 'GET'])
def form():
    return render_template('BreidtForm.html')
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return f"The URL /signup is accessed directly. Try going to '/login' then clicking the Sign Up button"
    if request.method == 'POST':
        return render_template('signup.html')



if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449, debug=True)
