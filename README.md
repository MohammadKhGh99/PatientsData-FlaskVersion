# PatientsData-FlaskVersion

A software for storing patients data for therapists

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Features

- Adding new patient
- Search for patient using:
  - first name
  - first + middle name
  - first + last name
  - last name
  - full name
  - id number
- Save database in google drive
- Restore from google drive
- Convert database to csv file

## Installation

1. Clone the repository:

   ```sh
      git clone https://github.com/MohammadKhGh99/PatientsData-FlaskVersion.git
   ```

2. Install dependencies:

   ```sh
      pip install -r requirments.txt
   ```

## Usage

1. Start the server:

   ```sh
      python app.py
   ```

2. It should open a new browser page for you, if not Open the website in your browser: [127.0.0.1:5000](http://127.0.0.1:5000)
3. Add patient, click on the first button "إضافة مريض جديد":
   1. Fill the data of the patient.
   2. You MUST enter a unique number in input box "الرقم التسلسلي".
   3. Submit the form with clicking on the green button "حفظ".
   4. Discard changes with clicking on the red button "تجاهل".
4. Search for patient, click on the second button "ابحث عن مريض":
   1. If you don't enter any thing to search on, it will show you all the patients in databse.
   2. Choose the method of search, for example using first name
   3. Click on the left button "البحث" and you will be forwarded to the results page (if there is any result, or not found message will appear).
   4. Choose which patient you want to show his data from the drop menu and click on the button "تم" to show the data in new page.
   5. Now you can see the data of the patient and change them as you like, don't forget to click on the save button.
5. Save the data in Google Drive:
   1. Click on the third button "حفظ في جوجل درايف"
   2. A page will open asks you to give permission to the app to enter tp your Google Drive to save the data in it.
6. Restore data from Google Drive:
   1. Click on the fourth button "استعادة من جوجل درايف"
   2. if it's your first time you will be forwarded to a new page asks for your permission to enter Google Drive, if not it will restore directly.
7. Convert database to csv file (like excel):
   1. Click on the fifth button "تحويل إلى ملف اكسل".
8. To close the app click on the top right red button "إغلاق", if you don't click it, the app will keep running in the background and you can enter it by going to the browser to the address [127.0.0.1:5000](http://127.0.0.1:5000).

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
