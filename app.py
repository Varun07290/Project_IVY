from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import bcrypt
from mysql.connector.errors import IntegrityError, DataError, DatabaseError



# POST, GET, PUT, and DELETE (API Methods that we need to implement)
app = Flask(__name__)
app.secret_key = 'team_ivy'


# config = {
#   'user': 'root',
#   'password': 'root',
#   'host': 'localhost',
#   #'unix_socket': '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
#   'database': 'proj',
#   #'raise_on_warnings': True
# }

# db = mysql.connector.connect(**config)
db = mysql.connector.connect(host = 'localhost', user = 'root', password = '', database = 'proj')



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
    criminal_info = [{'Criminal_ID': row[0], 'Last': row[1], 'First': row[2], 'Street': row[3], 'City': row[4], 'State' : row[5],'Zip' : row[6],'Phone' : row[7],'V_status' : row[8],'P_status' : row[9]} for row in criminal_raw]
    return criminal_info

@app.route('/GET_criminal_info', methods = ['GET']) # Get is the default btw
def GET_criminal_info():
    criminal_info = find_criminal_info()
    return render_template('Criminal_Information_Page.html',criminal_info = criminal_info)


@app.route('/POST_criminal', methods = ['POST'])
def POST_criminal():
    try:
        Criminal_ID = request.form['Criminal_ID']
        last_name = request.form['Last']
        first_name = request.form['First']
        phone_num = request.form['Phone']
        Street = request.form['Street']
        City = request.form['City']
        State = request.form['State']
        Zip = request.form['Zip']
        violent_status = request.form['V_status']
        probation_status = request.form['P_status']
        cursor = db.cursor()
        query = 'INSERT INTO Criminals (Criminal_ID,Last,First,Phone,Street,City,State,Zip,V_status,P_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(Criminal_ID,last_name,first_name,phone_num,Street,City,State,Zip,violent_status,probation_status))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_criminal_info'))
    except IntegrityError as e:
        error_message = "This criminal is already in the database."
        criminal_info = find_criminal_info()
        return render_template('Criminal_Information_Page.html',criminal_info = criminal_info, error=error_message)




#Crime Code Methods


def find_crimecode_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Crime_codes')
    crimecode_raw = cursor.fetchall()
    crimecode_info = [{'Crime_code': row[0], 'Code_description': row[1]} for row in crimecode_raw]
    return crimecode_info

@app.route('/GET_crimecode_info', methods = ['GET']) # Get is the default btw
def GET_crimecode_info():
    crimecode_info = find_crimecode_info()
    return render_template('Crime_Code_Information_Page.html',crimecode_info = crimecode_info)

@app.route('/POST_crimecode', methods = ['POST'])
def POST_crimecode():
    try:
        Crimecode = request.form['Crime_code']
        codedes = request.form['Code_description']
        cursor = db.cursor()
        query = 'INSERT INTO Crime_codes (Crime_code,Code_description) VALUES (%s,%s)'
        cursor.execute(query,(Crimecode, codedes))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_crimecode_info'))
    except IntegrityError as e:
        error_message = "This crime code is already in the database."
        crimecode_info = find_crimecode_info()
        return render_template('Crime_Code_Information_Page.html',crimecode_info = crimecode_info, error=error_message)

#Crime method


def find_crime_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Crimes')
    crime_raw = cursor.fetchall()
    crime_info = [{'Crime_ID': row[0], 'Criminal_ID': row[1], 'Classification': row[2], 'Date_charged': row[3], 'Status': row[4], 'Hearing_date': row[5], 'Appeal_cut_date': row[6]} for row in crime_raw]
    return crime_info

@app.route('/GET_crime_info', methods = ['GET']) # Get is the default btw
def GET_crime_info():
    crime_info = find_crime_info()
    return render_template('Crime_Information_Page.html',crime_info = crime_info)

@app.route('/POST_crime', methods = ['POST'])
def POST_crime():
    try:
        crimeid = request.form['Crime_ID']
        criminalid = request.form['Criminal_ID']
        Classification = request.form['Classification']
        Date_charged = request.form['Date_charged']
        Status = request.form['Status']
        Hearing_date = request.form['Hearing_date']
        Appeal_cut_date = request.form['Appeal_cut_date']
        cursor = db.cursor()
        query = 'INSERT INTO Crimes (Crime_ID, Criminal_ID, Classification, Date_charged, Status, Hearing_date, Appeal_cut_date) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(crimeid, criminalid, Classification, Date_charged, Status, Hearing_date, Appeal_cut_date))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_crime_info'))
    except IntegrityError as e:
        error_message = "This crime is already in the database."
        crime_info = find_crime_info()
        return render_template('Crime_Information_Page.html',crime_info = crime_info, error=error_message)




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