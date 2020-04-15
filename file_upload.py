from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('up_home.html')

@app.route('/upload_it', methods=['POST','GET'])
def upload_it():
    # if request.method == "POST":
    #     file = request.files['inputFile']
    #     return file.filename
    return str(request.form.get("image"))

if __name__ == '__main__':
    app.run(debug=True)