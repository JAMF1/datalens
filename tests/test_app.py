from app import app 
from io import BytesIO
import pandas as pd 

app.testing = True
client = app.test_client()

def test_valid_main_page():
    response = client.get("/")
    assert response.status_code == 200
    assert b"<p>Upload a CSV or XLSX file to inspect your dataset.</p>" in response.data

def test_upload_valid_csv():
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

def test_upload_empty_csv():
    data = {
        "file": (
            BytesIO(b""),
            "people.csv",
        )
    }

    response = client.post("/upload", data=data)

    assert response.status_code == 400 
    assert b"The uploaded file is empty or contains no readable data." in response.data

    
def test_upload_malformed_csv():
    data = {
        "file": (
            BytesIO(b"name,age\nAlice,25\nBob,30,extra1"),
            "people.csv",
        )
    }
    
    response = client.post("/upload", data=data)

    assert response.status_code == 400
    assert b"The CSV could not be parsed. Check its structure and delimiters." in response.data

def test_unsupported_extension():
    data = {
        "file": (
            BytesIO(b"name,age\nAlice,25\nBob,30"),
            "people.json",
        )
    }

    response = client.post("/upload", data=data)

    assert response.status_code == 400
    assert b"Unsupported file format. Please upload a CSV or XLSX file." in response.data 

def test_upload_valid_xlsx():
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