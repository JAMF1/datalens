from app import app 
from io import BytesIO

app.testing = True
client = app.test_client()


def test_valid_main_page():
    response = client.get("/")
    assert response.status_code == 200
    assert b"<p>Upload a CSV file to inspect your dataset.</p>" in response.data

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
            "people.xlsx",
        )
    }

    response = client.post("/upload", data=data)

    assert response.status_code == 400
    assert b"Unsupported file format. Please upload a CSV file." in response.data 

    