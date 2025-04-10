import sqlite3 as sql3


connection = sql3.connect('my_DB.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL,
position TEXT NOT NULL,
firstname TEXT NOT NULL,
secondname TEXT NOT NULL,
middlename TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Patients(
id INTEGER PRIMARY KEY AUTOINCREMENT,
firstname TEXT NOT NULL,
secondname TEXT NOT NULL,
middlename TEXT,
birthday DATE NOT NULL,
passport TEXT NOT NULL UNIQUE,
polis TEXT NOT NULL,
doctor_id INTEGER,
FOREIGN KEY (doctor_id) REFERENCES Users (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Photos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
path_mat TEXT NOT NULL,
path_photo TEXT NOT NULL,
name TEXT NOT NULL,
resultML BOOLEAN NOT NULL,
percent TEXT NOT NULL,
date DATE,
patient_id INTEGER,
FOREIGN KEY (patient_id) REFERENCES Patients (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Diagnosis(
id INTEGER PRIMARY KEY AUTOINCREMENT,
diagnosis TEXT,
patient_id INTEGER,
FOREIGN KEY (patient_id) REFERENCES Patients (id)
)
''')



connection.commit()
connection.close()