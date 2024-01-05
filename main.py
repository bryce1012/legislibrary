# import os.path
from pathlib import Path
import re
import requests
import datetime


def get_session(year):
    print("Getting Sessions")
    session_list = requests.get("https://sdlegislature.gov/api/Sessions").json()
    for session in session_list:
        if session['Year'] == year:
            return session['SessionId']
    return ""


def get_bills(session):
    print("Getting Bills for Session " + str(session))
    bill_list = requests.get("https://sdlegislature.gov/api/Bills/Session/Light/" + str(session)).json()
    for bill in bill_list:
        get_bill_versions(bill)


def get_bill_versions(bill):
    bill_number = bill['BillType'] + str(bill['BillNumberOnly'])
    print("Getting Versions for " + bill_number + " (id: " + str(bill['BillId']) + ")")
    bill_versions = requests.get("https://sdlegislature.gov/api/Bills/Versions/" + str(bill['BillId'])).json()
    for document in bill_versions:
        get_doc(bill_number, document)


def get_doc(bill_number, document):
    timestamp = re.sub(r"\.\d{0,3}-\d{2}:\d{2}", "", document['DocumentDate'])
    file_name = bill_number + "_" + timestamp.replace(":", "-") + ".pdf"
    file_path = Path.home().joinpath("LegisLibrary").joinpath(file_name)
    if not Path.exists(file_path):
        print("Downloading " + file_name)
        file_url = "https://mylrc.sdlegislature.gov/api/Documents/" + str(document['DocumentId']) + ".pdf"
        file_data = requests.get(file_url).content
        with open(file_path, "wb") as file:
            file.write(file_data)
    else:
        print("Already downloaded " + file_name)


if __name__ == '__main__':
    session = input("Enter session, or 'y' to specify by year [y]: ").strip().lower() or "y"
    if session == 'y':
        today = datetime.date.today()
        current_year = str(today.year)
        year = input("Enter a year to download bill documents [" + current_year + "]: ").strip() or current_year
        session = get_session(year)
    get_bills(session)

