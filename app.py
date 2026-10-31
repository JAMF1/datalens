from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage
from datalens.ingestion import load_data
from datalens.profiling import (get_missing_value_profile, get_descriptive_statistics, get_column_profile, get_dataset_overview)

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
    dataset_overview = get_dataset_overview(dataframe=df)
    column_profile = get_column_profile(dataframe=df)
    descriptive_statistics = get_descriptive_statistics(dataframe=df)
    missing_value_profile = get_missing_value_profile(dataframe=df)

    return render_template("results.html", 
                           dataset_overview = dataset_overview,
                           column_profile = column_profile,
                           descriptive_statistics = descriptive_statistics,
                           missing_value_profile = missing_value_profile,
                           columns=preview.columns.tolist(),
                           rows=list(preview.itertuples(index=False, name=None)),
                           )

if __name__ == "__main__":
    app.run(debug=True)