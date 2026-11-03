from app import app 
from io import BytesIO
import pandas as pd 
import pytest


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_valid_main_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<p>Upload a CSV or XLSX file to inspect your dataset.</p>" in response.data

def test_upload_valid_csv(client):
    data = {
        "file": (
            BytesIO(b"name,age\nAlice,25\nBob,30"),
            "people.csv",
        )
    }
    
    response = client.post("/upload", data=data)

    assert response.status_code == 200
    assert b"<h1>Dataset overview</h1>" in response.data
    assert b"Alice" in response.data
    #For future reference no hardcoding like below
    assert b"<p>Rows: 2</p>" in response.data
    assert b"<p>Columns: 2</p>" in response.data

def test_upload_empty_csv(client):
    data = {
        "file": (
            BytesIO(b""),
            "people.csv",
        )
    }

    response = client.post("/upload", data=data)

    assert response.status_code == 400 
    assert b"The uploaded file is empty or contains no readable data." in response.data
    
def test_upload_malformed_csv(client):
    data = {
        "file": (
            BytesIO(b"name,age\nAlice,25\nBob,30,extra1"),
            "people.csv",
        )
    }
    
    response = client.post("/upload", data=data)

    assert response.status_code == 400
    assert b"The CSV could not be parsed. Check its structure and delimiters." in response.data

def test_unsupported_extension(client):
    data = {
        "file": (
            BytesIO(b"name,age\nAlice,25\nBob,30"),
            "people.json",
        )
    }

    response = client.post("/upload", data=data)

    assert response.status_code == 400
    assert b"Unsupported file format. Please upload a CSV or XLSX file." in response.data 

def test_upload_valid_xlsx(client):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [25, 30],
        }).to_excel(writer, index=False)

    buffer.seek(0)

    data = {
        "file": (
            buffer,
            "people.xlsx"
        )
    }

    response = client.post("/upload", data=data)

    assert response.status_code == 200
    assert b"<h1>Dataset overview</h1>" in response.data
    assert b"Alice" in response.data
    assert b"<p>Rows: 2</p>" in response.data
    assert b"<p>Columns: 2</p>" in response.data

def test_upload_csv_displays_profiling_results(client):
    csv_content = (
        "name,age,salary\n"
        "Alice,25,50000\n"
        "Bob,,60000\n"
        "Cara,35,\n"
    )

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "people.csv")
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "Dataset overview" in html
    assert "Rows: 3" in html
    assert "Columns: 3" in html

    assert "Missing-value summary" in html
    assert "Missing cells:" in html
    assert "Total cells:" in html

    assert "Column Profile" in html
    assert "name" in html
    assert "age" in html
    assert "salary" in html

    assert "Descriptive statistics" in html
    assert "mean" in html

    assert "Alice" in html
    assert "Bob" in html

def test_upload_csv_without_numeric_columns(client):
    csv_content = (
        "name,department\n"
        "Alice,Sales\n"
        "Bob,IT\n"
    )

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "employees.csv")
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "No numeric columns available for descriptive statistics." in html
    assert "Alice" in html

def test_upload_xlsx_displays_profiling_results(client):
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Cara"],
        "age": [25, None, 35],
        "salary": [50000, 60000, None]
    })

    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    response = client.post(
        "/upload",
        data={
            "file": (excel_file, "employees.xlsx")
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "Dataset overview" in html
    assert "Rows: 3" in html
    assert "Columns: 3" in html
    assert "Missing-value summary" in html
    assert "Descriptive statistics" in html
    assert "Alice" in html

def test_upload_csv_with_zero_rows(client):
    csv_content = "name,age,salary\n"

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "empty.csv")
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "Rows: 0" in html
    assert "Columns: 3" in html
    assert "Missing percentage: N/A" in html
    assert "The file was read successfully, but no records were found." in html

def test_upload_csv_displays_duplicate_profile(client):
    csv_content = (
        "name,age\n"
        "Alice,25\n"
        "Bob,30\n"
        "Alice,25\n"
        "Charlie,35\n"
        "Bob,30\n"
    )

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "people.csv")
        },
        content_type="multipart/form-data"
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Duplicate Records" in html
    assert "5" in html
    assert "2" in html
    assert "40.0%" in html

def test_upload_csv_without_duplicates(client):
    csv_content = (
        "name,age\n"
        "Alice,25\n"
        "Bob,30\n"
        "Charlie,35\n"
    )

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "people.csv")
        },
        content_type="multipart/form-data"
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Duplicate Records" in html
    assert "0" in html
    assert "0.0%" in html

def test_upload_csv_with_missing_value_duplicates(client):
    csv_content = (
        "name,age\n"
        "Alice,\n"
        "Alice,\n"
        "Bob,30\n"
    )

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "people.csv")
        },
        content_type="multipart/form-data"
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Duplicate Records" in html
    assert "1" in html
    assert "33.33333333333333%" in html

def test_upload_xlsx_displays_duplicate_profile(client):
    excel_content = BytesIO()

    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Alice"],
        "age": [25, 30, 25]
    })

    df.to_excel(excel_content, index=False)
    excel_content.seek(0)

    response = client.post(
        "/upload",
        data={
            "file": (excel_content, "people.xlsx")
        },
        content_type="multipart/form-data"
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Duplicate Records" in html
    assert "3" in html
    assert "1" in html
    assert "33.33333333333333%" in html

def test_upload_csv_with_zero_rows_displays_duplicate_profile(client):
    csv_content = "name,age\n"

    response = client.post(
        "/upload",
        data={
            "file": (BytesIO(csv_content.encode("utf-8")), "people.csv")
        },
        content_type="multipart/form-data"
    )

    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Duplicate Records" in html
    assert "0" in html
    assert "N/A" in html