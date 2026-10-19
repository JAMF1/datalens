from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage
from datalens.ingestion import load_data

#My app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file: FileStorage | None = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return render_template("index.html", error="Please Select a File to Upload"), 400

    filename = uploaded_file.filename

    if not filename.lower().endswith((".csv", ".xlsx")):
        return render_template("index.html", error="Unsupported file format. Please upload a CSV or XLSX file."), 400

    try:
        file_type = filename.lower().rsplit(".",1)[-1]
        df = load_data(uploaded_file.stream, file_type)

    except ValueError as exc:
        return render_template("index.html", error=str(exc)), 400

    preview = df.head(10)

    return render_template("results.html", 
                           columns=preview.columns.tolist(),
                           rows=list(preview.itertuples(index=False, name=None)),
                           total_rows=len(df),
                           total_columns=len(df.columns)
                           )

if __name__ == "__main__":
    app.run(debug=True)