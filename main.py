from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"The operation is {operation} and the filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newfilename = f"static/{filename}"
            cv2.imwrite(newfilename, imgProcessed)
            return newfilename
        case "cwebp":
            newfilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newfilename, img)
            return newfilename
        case "cjpg":
            newfilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newfilename, img)
            return newfilename
        case "cpng":
            newfilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newfilename, img)
            return newfilename
        case "cartoon":
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(img_gray, 5)
            color = cv2.bilateralFilter(img, 9, 250, 250)
            edges = cv2.adaptiveThreshold(gray, 255, 
                                          cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 9, 9)
            imgCartoon = cv2.bitwise_and(color, color, mask=edges)
            newfilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newfilename, imgCartoon)
            return newfilename
    pass

@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/about")
# def about():
#     return render_template("about.html")

# @app.route("/contact")
# def contact():
#     return render_template("contact.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new  = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a> ")
            return render_template("index.html")
    
    return render_template("index.html")

app.run(debug=True, port=5001)