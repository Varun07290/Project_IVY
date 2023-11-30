from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import bcrypt
from mysql.connector.errors import IntegrityError, DataError, DatabaseError



# POST, GET, PUT, and DELETE (API Methods that we need to implement)
app = Flask(__name__)
app.secret_key = 'team_ivy'


config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
  'database': 'final_project_testing_1',
  'raise_on_warnings': True
}

db = mysql.connector.connect(**config)


@app.route('/')
def login_start():
    return render_template('login.html')


# Login Page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate credentials
        if validate_credentials(username, password):
            return redirect(url_for('index'))  # Redirect to the index page if valid
        else:
            flash('Invalid username or password')  # Show error message

    return render_template('login.html')

# Index
@app.route('/index')
def index():
    return render_template('index.html')

def validate_credentials(username, password):
    try:
        cursor = db.cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if user and user[1] == password:
            return True
        else:
            return False
    finally:
        cursor.close()





#  Officer Methods Start Here

def find_officer_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Officers')
    officer_raw = cursor.fetchall()
    officer_info = [{'Officer_ID': row[0], 'Last': row[1], 'First': row[2], 'Precinct': row[3], 'Badge': row[4], 'Phone': row[5], 'Status': row[6]} for row in officer_raw]
    return officer_info

@app.route('/GET_officer_info', methods = ['GET']) # Get is the default btw
def GET_officer_info():
    officer_info = find_officer_info()
    return render_template('Police_Information_Page.html', officer_info = officer_info)


@app.route('/POST_officer', methods = ['POST'])
def POST_officer():
    try:
        Officer_ID = request.form['Officer_ID']
        Last = request.form['Last']
        First = request.form['First']
        Precinct = request.form['Precinct']
        Badge = request.form['Badge']
        Phone = request.form['Phone']
        Status = request.form['Status']
        cursor = db.cursor()
        query = 'INSERT INTO Officers (Officer_ID, Last, First, Precinct, Badge, Phone, Status) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(Officer_ID, Last, First, Precinct, Badge, Phone, Status))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_officer_info'))
    except IntegrityError as e:
        error_message = "A police officer with this badge number already exists."
        officer_info = find_officer_info()
        return render_template('Police_Information_Page.html', officer_info = officer_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        officer_info = find_officer_info()
        return render_template('Police_Information_Page.html', officer_info = officer_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        officer_info = find_officer_info()
        return render_template('Police_Information_Page.html', officer_info = officer_info, error=error_message)

@app.route('/delete_officer', methods=['POST'])
def delete_officer():
    officer_id = request.form['officer_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Officers WHERE Officer_ID = %s', (officer_id,))
        db.commit()
        cursor.close()
        flash('Officer deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the officer.')
        print(e)
    return redirect(url_for('GET_officer_info'))
 


@app.route('/edit_officer', methods=['POST'])
def edit_officer():
    officer_id = request.form['Officer_ID']
    last_name = request.form['Last']
    first_name = request.form['First']
    precinct = request.form['Precinct']
    badge_number = request.form['Badge']
    phone_number = request.form['Phone']
    status = request.form['Status']

    try:
        cursor = db.cursor()

        # SQL query to update officer details
        query = """
        UPDATE Officers 
        SET Last = %s, First = %s, Precinct = %s, Badge = %s, Phone = %s, Status = %s
        WHERE Officer_ID = %s
        """
        cursor.execute(query, (last_name, first_name, precinct, badge_number, phone_number, status, officer_id))
        
        db.commit()
        cursor.close()
        flash('Officer updated successfully.')
        return redirect(url_for('GET_officer_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the officer.')
        print(e)
        return redirect(url_for('GET_officer_info'))




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