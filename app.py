from flask import Flask
from flask import render_template, request, redirect, url_for, flash, send_file
from flask_cors import CORS
import os
import pandas as pd

# from flask_restful import 
app = Flask(__name__)
app.secret_key="supersecretkey"

os.makedirs("uploads", exist_ok=True)
app.config["UPLOAD_FOLDER"] = "uploads"

saved_files= []

@app.route('/', methods=["GET", "POST"])
def upload_files():
    excel_ready = False
    if request.method == 'POST':
        if "files" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        files = request.files.getlist("files")

        global saved_files
        saved_files.clear()

        for file in files:
            filename = file.filename
            print(f"Processing {filename}")
            if file.filename and not file.filename.startswith("."):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                try:
                    file.save(file_path)
                    saved_files.append(file.filename)
                except FileNotFoundError:
                    flash(f"Error saving file: {file.filename}. Skipping.")
                    continue

        if saved_files:
            excel_path = os.path.join(app.config["UPLOAD_FOLDER"], "file_list.xlsx")
            df = pd.DataFrame(saved_files, columns=["Uploaded Files"])
            df.to_excel(excel_path, index=False)


            flash("Files uploaded successfully! Click below to download the Excel file.")
            excel_ready = True
            return render_template("LandingPage.html", excel_ready=excel_ready)

    return render_template("LandingPage.html", excel_ready=excel_ready)

@app.route("/download")
def download_file():
    excel_path = os.path.join(app.config["UPLOAD_FOLDER"], "file_list.xlsx")
    if os.path.exists(excel_path):
        response = send_file(excel_path, as_attachment=True)
        os.remove(excel_path)
        global saved_files
        saved_files.clear()
        
        return response
    else:
        return redirect(url_for("upload_files"))

if __name__ == "__main__":
    app.run(debug=True)
