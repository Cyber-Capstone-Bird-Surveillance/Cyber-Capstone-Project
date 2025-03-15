from flask import Flask
from flask import render_template, request, redirect, url_for, flash, send_file
import os
import shutil
import pandas as pd
import model

app = Flask(__name__)
app.secret_key="supersecretkey"

#make uploads file
os.makedirs("uploads", exist_ok=True)
app.config["UPLOAD_FOLDER"] = "uploads"

saved_files= []

#main page
@app.route('/', methods=["GET", "POST"])
def upload_files():

    #set to false so when you reload, the excel file link goes away
    excel_ready = False

    if request.method == 'POST':
        if "files" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        #gets files
        files = request.files.getlist("files")

        global saved_files
        saved_files.clear()

        #creates excel sheet from files
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
            # Call model.predictions for each file and store the results
            predictions = []
            for file in saved_files:
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file)
                prediction = model.predictions(file_path)
                predictions.append(prediction)
            
            # Add predictions to the DataFrame
            df["Predictions"] = predictions
            
            # Save the updated DataFrame to the Excel file
            df.to_excel(excel_path, index=False)
            
            flash("Files uploaded successfully! Click below to download the Excel file.")
            excel_ready = True
            return render_template("LandingPage.html", excel_ready=excel_ready)
    return render_template("LandingPage.html", excel_ready=excel_ready)

@app.route("/download")
def download_file():

    #sends excel file
    excel_path = os.path.join(app.config["UPLOAD_FOLDER"], "file_list.xlsx")
    if os.path.exists(excel_path):
        response = send_file(excel_path, as_attachment=True)

        #clears upload folder
        for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) 
                elif os.path.isdir(file_path):
                     shutil.rmtree(file_path) 
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        global saved_files
        saved_files.clear()

        return response    
    else:
        return redirect(url_for("upload_files"))

if __name__ == "__main__":
    app.run(debug=True)



#Increase size of uploads (if in gigabyte range, will probably need to set it up with AWS or whatever we use to deploy)
#Figure out the API