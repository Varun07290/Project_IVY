from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector.errors import IntegrityError



# POST, GET, PUT, and DELETE (API Methods that we need to implement)
app = Flask(__name__)

config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
  'database': 'Project_IVY',
  'raise_on_warnings': True
}

db = mysql.connector.connect(**config)

@app.route('/')
def index():
    return render_template('index.html')


# Police Officer Methods Start Here

def find_police_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Police_officer')
    Police_officer_raw = cursor.fetchall()
    Police_officer_info = [{'Badge_number': row[0], 'Name': row[1], 'Precinct': row[2], 'Phone_contact': row[3], 'officer_Status': row[4]} for row in Police_officer_raw]
    return Police_officer_info

@app.route('/GET_police_info', methods = ['GET']) # Get is the default btw
def GET_police_info():
    Police_officer_info = find_police_info()
    return render_template('Police_Information_Page.html',Police_officer_info = Police_officer_info)


@app.route('/POST_police_officer', methods = ['POST'])
def POST_police_officer():
    try:
        badge_num = request.form['Badge_number']
        name = request.form['Name']
        precinct = request.form['Precinct']
        phone_num = request.form['Phone_contact']
        status = request.form['officer_Status']
        cursor = db.cursor()
        query = 'INSERT INTO Police_officer (Badge_number,Name,Precinct,Phone_contact,officer_Status) VALUES (%s,%s,%s,%s,%s)'
        cursor.execute(query,(badge_num,name,precinct,phone_num,status))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_police_info'))
    except IntegrityError as e:
        error_message = "A police officer with this badge number already exists."
        Police_officer_info = find_police_info()
        return render_template('Police_Information_Page.html',Police_officer_info = Police_officer_info, error=error_message)


@app.route('/DELETE_police_officer/<badge_number>', methods = ['DELETE'])
def DELETE_police_officer(badge_number):
    try:
        cursor = db.cursor
        query = 'DELETE FROM Police_officer WHERE Badge_num = %s'
        cursor.execute(query,(badge_number,))
        db.commit()
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return redirect(url_for('index'))     


# Criminal Methods
def find_criminal_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Criminals')
    criminal_raw = cursor.fetchall()
    criminal_info = [{'Criminals_last_name': row[0], 'Criminals_first_name': row[1], 'PhoneNumber': row[2], 'Criminals_address': row[3], 'ViolentOffenderStatus': row[4], 'ProbationStatus' : row[5]} for row in criminal_raw]
    return criminal_info

@app.route('/GET_criminal_info', methods = ['GET']) # Get is the default btw
def GET_criminal_info():
    criminal_info = find_criminal_info()
    return render_template('Criminal_Information_Page.html',criminal_info = criminal_info)


@app.route('/POST_criminal', methods = ['POST'])
def POST_criminal():
    try:
        last_name = request.form['Criminals_last_name']
        first_name = request.form['Criminals_first_name']
        phone_num = request.form['PhoneNumber']
        address = request.form['Criminals_address']
        violent_status = request.form['ViolentOffenderStatus']
        probation_status = request.form['ProbationStatus']
        cursor = db.cursor()
        query = 'INSERT INTO Criminals (Criminals_last_name,Criminals_first_name,PhoneNumber,Criminals_address,ViolentOffenderStatus,ProbationStatus) VALUES (%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(last_name,first_name,phone_num,address,violent_status,probation_status))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_criminal_info'))
    except IntegrityError as e:
        error_message = "This criminal is already in the database."
        criminal_info = find_criminal_info()
        return render_template('Criminal_Information_Page.html',criminal_info = criminal_info, error=error_message)

"""
@app.route('/edit_criminal/<int:criminal_id>', methods=['GET'])
def edit_criminal(criminal_id):
    # Retrieve the criminal's data from the database
    # Render an editing form page for the criminal
    pass

@app.route('/delete_criminal/<int:criminal_id>', methods=['POST'])
def delete_criminal(criminal_id):
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Criminals WHERE id = %s', (criminal_id,))
        db.commit()
        cursor.close()
        flash('Criminal deleted successfully!')
    except Exception as e:
        flash('An error occurred while deleting the criminal.')
        # Log the error for debugging
        print(e)
    return redirect(url_for('GET_criminal_info'))

"""





if __name__ == '__main__':
    app.run(debug=True)





"""
# In no order
1. finish the front-end HTML/CSS pages
2. create the rest of the API methods for each table
3. error handling, and sending error messages to the front-end GUI
"""