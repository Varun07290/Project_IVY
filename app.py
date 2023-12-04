from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import bcrypt
from mysql.connector.errors import IntegrityError, DataError, DatabaseError
import os
import openai
from openai import OpenAI

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
cursor = db.cursor()

"""
# Fetch all users
cursor.execute("SELECT id, password FROM Users")
users = cursor.fetchall()

for user_id, plain_text_password in users:
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("UPDATE Users SET password = %s WHERE id = %s", (hashed_password, user_id))

"""

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
            session['username'] = username  # Store username in session
            return redirect(url_for('index'))  # Redirect to the index page if valid
        else:
            flash('Invalid username or password')  # Show error message

    return render_template('Login.html')

# Index
@app.route('/index')
def index():
    username = session.get('username', 'User')  # Get username from session, default to 'User'
    user_has_access_control = 'username' in session and has_access_control(session['username'])

    return render_template('index.html', username=username, user_has_access_control = user_has_access_control)

def validate_credentials(username, password):
    try:
        cursor = db.cursor()
        sql = "SELECT * FROM Users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if user:
            hashed_password = user[2].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return True
            else:
                return False
    finally:
        cursor.close()


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Encode the password
        access_control = request.form.get('access_control')  # Get the admin control value

        if access_control == 'true':
            access_control = 0
        else:
            access_control= 1

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Connect to the database
        db = mysql.connector.connect(**config)
        cursor = db.cursor()

        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists. Choose a different one.')
            return render_template('create_account.html', error='Username already exists')


        # Insert the new user into the database
        insert_query = 'INSERT INTO users (username, password, access_control) VALUES (%s, %s, %s)'
        cursor.execute(insert_query, (username, hashed_password,access_control))
        db.commit()
        cursor.close()
        db.close()

        flash('Account created successfully. Please login.')
        return redirect(url_for('login'))

    return render_template('create_account.html')




## DB Security Methods:

def has_access_control(username):
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    cursor.execute('SELECT access_control FROM users WHERE username = %s', (username,))
    result = cursor.fetchone()

    cursor.close()
    db.close()

    if result and result[0]:  # Check if access_control is True
        return True
    else:
        return False
    
@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if 'username' not in session:
        return redirect(url_for('login_start'))

    username = session['username']
    
    if not has_access_control(username):
        flash('You do not have access control to perform this action.')
        return redirect(url_for('index'))

    # Handle form submissions and execute SQL statements here for database modifications
    # ...

    return render_template('admin_panel.html')


def grant_access_control(username):
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    try:
        cursor.execute('UPDATE users SET access_control = 1 WHERE username = %s', (username,))
        db.commit()
        flash(f'Access control granted to user: {username}')
    except Exception as e:
        db.rollback()
        flash(f'Error granting access control: {str(e)}')
    finally:
        cursor.close()
        db.close()

# Function to revoke access control from a user using SQL REVOKE statement
def revoke_access_control(username):
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    try:
        cursor.execute('UPDATE users SET access_control = 0 WHERE username = %s', (username,))
        db.commit()
        flash(f'Access control revoked from user: {username}')
    except Exception as e:
        db.rollback()
        flash(f'Error revoking access control: {str(e)}')
    finally:
        cursor.close()
        db.close()

# Your existing Flask routes here...

# Route to handle granting access control
@app.route('/grant_access_control', methods=['POST'])
def grant_access_control_route():
    if 'username' not in session:
        return redirect(url_for('login_start'))

    username = session['username']

    if not has_access_control(username):
        flash('You do not have access control to perform this action.')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        grant_username = request.form.get('grant_username')
        if grant_username:
            grant_access_control(grant_username)

    return redirect(url_for('admin_panel'))

# Route to handle revoking access control
@app.route('/revoke_access_control', methods=['POST'])
def revoke_access_control_route():
    if 'username' not in session:
        return redirect(url_for('login_start'))

    username = session['username']

    if not has_access_control(username):
        flash('You do not have access control to perform this action.')
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        revoke_username = request.form.get('revoke_username')
        if revoke_username:
            revoke_access_control(revoke_username)

    return redirect(url_for('admin_panel'))



#  Officer Methods Start Here

def find_officer_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Officers')
    column_names = cursor.column_names
    officer_raw = cursor.fetchall()
    # officer_info = [{'Officer_ID': row[0], 'Last': row[1], 'First': row[2], 'Precinct': row[3], 'Badge': row[4], 'Phone': row[5], 'Status': row[6]} for row in officer_raw]
    officer_info = [dict(zip(column_names,row)) for row in officer_raw]

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
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        criminal_info = find_criminal_info()
        return render_template('Criminal_Information_Page.html',criminal_info = criminal_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        criminal_info = find_criminal_info()
        return render_template('Criminal_Information_Page.html',criminal_info = criminal_info, error=error_message)


@app.route('/delete_criminal', methods=['POST'])
def delete_criminal():
    criminal_id = request.form['criminal_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Criminals WHERE Criminal_ID = %s', (criminal_id,))
        db.commit()
        cursor.close()
        flash('Criminal deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the criminal.')
        print(e)
    return redirect(url_for('GET_criminal_info'))
 


@app.route('/edit_criminal', methods=['POST'])
def edit_criminal():
    criminal_ID = request.form['Criminal_ID']
    last_name = request.form['Last']
    first_name = request.form['First']
    phone_num = request.form['Phone']
    street = request.form['Street']
    city = request.form['City']
    state = request.form['State']
    zip = request.form['Zip']
    violent_status = request.form['V_status']
    probation_status = request.form['P_status']

    try:
        cursor = db.cursor()

        # SQL query to update criminal details
        query = """
        UPDATE Criminals 
        SET Last= %s,First= %s,Phone= %s,Street= %s,City= %s,State= %s,Zip= %s,V_status= %s,P_status= %s
        WHERE Criminal_ID= %s
        """
        cursor.execute(query, (last_name,first_name,phone_num,street,city,state,zip,violent_status,probation_status,criminal_ID))
        
        db.commit()
        cursor.close()
        flash('Criminal updated successfully.')
        return redirect(url_for('GET_criminal_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the criminal.')
        print(e)
        return redirect(url_for('GET_criminal_info'))




#Crime Methods


def find_crimecode_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Crime_codes')
    crimecode_raw = cursor.fetchall()
    crimecode_info = [{'Crime_code': row[0], 'Code_description': row[1]} for row in crimecode_raw]
    return crimecode_info

@app.route('/GET_crimecode_info', methods = ['GET']) # Get is the default btw
def GET_crimecode_info():
    crimecode_info = find_crimecode_info()
    user_has_access_control = 'username' in session and has_access_control(session['username'])
    return render_template('Crime_Code_Information_Page.html',crimecode_info = crimecode_info, user_has_access_control = user_has_access_control)

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
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        crimecode_info = find_crimecode_info()
        return render_template('Crime_Code_Information_Page.html',crimecode_info = crimecode_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        crimecode_info = find_crimecode_info()
        return render_template('Crime_Code_Information_Page.html',crimecode_info = crimecode_info, error=error_message)


@app.route('/delete_crimecode', methods=['POST'])
def delete_crimecode():
    crimecode = request.form['crimecode']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Crime_Codes WHERE Crime_code = %s', (crimecode,))
        db.commit()
        cursor.close()
        flash('Crimecode deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the crimecode.')
        print(e)
    return redirect(url_for('GET_crimecode_info'))
 


@app.route('/edit_crimecode', methods=['POST'])
def edit_crimecode():
    Crimecode = request.form['Crime_code']
    codedes = request.form['Code_description']

    try:
        cursor = db.cursor()

        # SQL query to update crime code details
        query = """
        UPDATE Crime_Codes 
        SET Code_description = %s
        WHERE Crime_code= %s
        """
        cursor.execute(query, (codedes,Crimecode))
        
        db.commit()
        cursor.close()
        flash('Crime Code updated successfully.')
        return redirect(url_for('GET_crimecode_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the crime code.')
        print(e)
        return redirect(url_for('GET_crimecode_info'))



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
        crime_id = request.form['Crime_ID']
        criminal_id = request.form['Criminal_ID']
        Classification = request.form['Classification']
        Date_charged = request.form['Date_charged']
        Status = request.form['Status']
        Hearing_date = request.form['Hearing_date']
        Appeal_cut_date = request.form['Appeal_cut_date']
        cursor = db.cursor()
        query = 'INSERT INTO Crimes (Crime_ID, Criminal_ID, Classification, Date_charged, Status, Hearing_date, Appeal_cut_date) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(crime_id, criminal_id, Classification, Date_charged, Status, Hearing_date, Appeal_cut_date))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_crime_info'))
    except IntegrityError as e:
        error_message = "This crime is already in the database."
        crime_info = find_crime_info()
        return render_template('Crime_Information_Page.html',crime_info = crime_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        crime_info = find_crime_info()
        return render_template('Crime_Information_Page.html',crime_info = crime_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        crime_info = find_crime_info()
        return render_template('Crime_Information_Page.html',crime_info = crime_info, error=error_message)


@app.route('/delete_crime', methods=['POST'])
def delete_crime():
    crime_id = request.form['crime_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Crimes WHERE Crime_ID = %s', (crime_id,))
        db.commit()
        cursor.close()
        flash('Crime deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the crime.')
        print(e)
    return redirect(url_for('GET_crime_info'))
 
# cannot edit 
@app.route('/edit_crime', methods=['POST'])
def edit_crime():
    crimeid = request.form['Crime_ID']
    criminalid = request.form['Criminal_ID']
    classification = request.form['Classification']
    date_charged = request.form['Date_charged']
    status = request.form['Status']
    hearing_date = request.form['Hearing_date']
    appeal_cut_date = request.form['Appeal_cut_date']

    try:
        cursor = db.cursor()

        # SQL query to update crime details
        query = """
        UPDATE Crimes
        SET Classification= %s, Date_charged= %s, Status= %s, Hearing_date= %s, Appeal_cut_date= %s
        WHERE Crime_ID= %s AND Criminal_ID= %s
        """
        cursor.execute(query, (classification, date_charged, status, hearing_date, appeal_cut_date, crimeid,criminalid))
        
        db.commit()
        cursor.close()
        flash('Crime updated successfully.')
        return redirect(url_for('GET_crime_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the crime.')
        print(e)
        return redirect(url_for('GET_crime_info'))



#  Alias Methods Start Here

def find_alias_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Alias')
    alias_raw = cursor.fetchall()
    alias_info = [{'Alias_ID': row[0], 'Criminal_ID': row[1], 'Alias': row[2]} for row in alias_raw]
    return alias_info

@app.route('/GET_alias_info', methods = ['GET']) # Get is the default btw
def GET_alias_info():
    alias_info = find_alias_info()
    return render_template('Alias_Information_Page.html', alias_info = alias_info)


@app.route('/POST_alias', methods = ['POST'])
def POST_alias():
    try:
        Alias_ID = request.form['Alias_ID']
        Criminal_ID = request.form['Criminal_ID']
        Alias = request.form['Alias']
        cursor = db.cursor()
        query = 'INSERT INTO Alias (Alias_ID, Criminal_ID, Alias) VALUES (%s,%s,%s)'
        cursor.execute(query,(Alias_ID, Criminal_ID, Alias))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_alias_info'))
    except IntegrityError as e:
        error_message = "This Alias already exists."
        alias_info = find_alias_info()
        return render_template('Alias_Information_Page.html', alias_info = alias_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        alias_info = find_alias_info()
        return render_template('Alias_Information_Page.html', alias_info = alias_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        alias_info = find_alias_info()
        return render_template('Alias_Information_Page.html', alias_info = alias_info, error=error_message)

@app.route('/delete_alias', methods=['POST'])
def delete_alias():
    alias_id = request.form['alias_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Alias WHERE Alias_ID = %s', (alias_id,))
        db.commit()
        cursor.close()
        flash('Alias deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the alias.')
        print(e)
    return redirect(url_for('GET_alias_info'))
 


@app.route('/edit_alias', methods=['POST'])
def edit_alias():
    AliasID = request.form['Alias_ID']
    CriminalID = request.form['Criminal_ID']
    alias = request.form['Alias']

    try:
        cursor = db.cursor()

        # SQL query to update officer details
        query = """
        UPDATE Alias 
        SET Alias=%s
        WHERE Alias_ID = %s AND Criminal_ID =%s
        """
        cursor.execute(query, (alias,AliasID,CriminalID))
        
        db.commit()
        cursor.close()
        flash('Alias updated successfully.')
        return redirect(url_for('GET_alias_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the alias.')
        print(e)
        return redirect(url_for('GET_alias_info'))





#  Prob_officer Methods Start Here

def find_prob_officer_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Prob_officer')
    prob_officer_raw = cursor.fetchall()
    prob_officer_info = [{'Prob_ID': row[0], 'Last': row[1], 'First': row[2], 'Street': row[3], 'City': row[4], 'State': row[5], 'Zip': row[6], 'Phone' : row[7],'Email' : row[8],'Status' : row[9]} for row in prob_officer_raw]
    return prob_officer_info

@app.route('/GET_prob_officer_info', methods = ['GET']) # Get is the default btw
def GET_prob_officer_info():
    prob_officer_info = find_prob_officer_info()
    return render_template('Prob_officer_Information_Page.html',prob_officer_info = prob_officer_info)


@app.route('/POST_prob_officer', methods = ['POST'])
def POST_prob_officer():
    try:
        prob_officer_ID = request.form['Prob_ID']
        last_name = request.form['Last']
        first_name = request.form['First']
        Street = request.form['Street']
        City = request.form['City']
        State = request.form['State']
        Zip = request.form['Zip']
        phone_num = request.form['Phone']
        Email = request.form['Email']
        Status = request.form['Status']
        cursor = db.cursor()
        query = 'INSERT INTO Prob_officer (Prob_ID,Last,First,Street,City,State,Zip,Phone,Email,Status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query,(prob_officer_ID,last_name,first_name,Street,City,State,Zip,phone_num,Email,Status))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_prob_officer_info'))
    except IntegrityError as e:
        error_message = "This prob_officer is already in the database."
        prob_officer_info = find_criminal_info()
        return render_template('Prob_officer_Information_Page.html',prob_officer_info = prob_officer_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        prob_officer_info = find_criminal_info()
        return render_template('Prob_officer_Information_Page.html',prob_officer_info = prob_officer_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        prob_officer_info = find_criminal_info()
        return render_template('Prob_officer_Information_Page.html',prob_officer_info = prob_officer_info, error=error_message)


@app.route('/delete_prob_officer', methods=['POST'])
def delete_prob_officer():
    prob_officer_id = request.form['prob_officer_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Prob_officer WHERE Prob_ID = %s', (prob_officer_id,))
        db.commit()
        cursor.close()
        flash('Prob_officer deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the prob_officer.')
        print(e)
    return redirect(url_for('GET_prob_officer_info'))
 


@app.route('/edit_prob_officer', methods=['POST'])
def edit_prob_officer():
    prob_officer_ID = request.form['Prob_ID']
    last_name = request.form['Last']
    first_name = request.form['First']
    Street = request.form['Street']
    City = request.form['City']
    State = request.form['State']
    Zip = request.form['Zip']
    phone_num = request.form['Phone']
    Email = request.form['Email']
    Status = request.form['Status']

    try:
        cursor = db.cursor()

        # SQL query to update criminal details
        query = """
        UPDATE Prob_officer 
        SET Last= %s,First= %s,Street= %s,City= %s,State= %s,Zip= %s,Phone= %s,Email= %s,Status= %s
        WHERE Prob_ID= %s
        """
        cursor.execute(query, (last_name,first_name,Street,City,State,Zip,phone_num,Email,Status,prob_officer_ID))
        
        db.commit()
        cursor.close()
        flash('Prob_officer updated successfully.')
        return redirect(url_for('GET_prob_officer_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the prob_officer.')
        print(e)
        return redirect(url_for('GET_cprob_officer_info'))








#  Sentences Methods Start Here

def find_sentence_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Sentences')
    sentence_raw = cursor.fetchall()
    sentence_info = [ { 'Sentence_ID': row[0], 'Criminal_ID': row[1], 'Type': row[2], 'Prob_ID': row[3], 'Start_date': row[4], 'End_date': row[5], 'Violations': row[6] } for row in sentence_raw ]
    return sentence_info

@app.route('/GET_sentence_info', methods = ['GET']) # Get is the default btw
def GET_sentence_info():
    sentence_info = find_sentence_info()
    return render_template('Sentences_Information_Page.html', sentence_info = sentence_info)


@app.route('/POST_sentence', methods = ['POST'])
def POST_sentence():
    try:
        Sentence_ID = request.form['Sentence_ID']
        Criminal_ID = request.form['Criminal_ID']
        Type = request.form['Type']
        Prob_ID = request.form['Prob_ID']
        Start_date = request.form['Start_date']
        End_date = request.form['End_date']
        Violations = request.form['Violations']

        cursor = db.cursor()
        query = 'INSERT INTO Sentences (Sentence_ID, Criminal_ID, Type, Prob_ID, Start_date, End_date, Violations) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (Sentence_ID, Criminal_ID, Type, Prob_ID, Start_date, End_date, Violations))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_sentence_info'))
    except IntegrityError as e:
        error_message = "A Sentence already exists."
        sentence_info = find_sentence_info()
        return render_template('Sentences_Information_Page.html', sentence_info = sentence_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        sentence_info = find_sentence_info()
        return render_template('Sentences_Information_Page.html', sentence_info = sentence_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        sentence_info = find_sentence_info()
        return render_template('Sentences_Information_Page.html', sentence_info = sentence_info, error=error_message)
    
@app.route('/delete_sentence', methods=['POST'])
def delete_sentence():
    sentence_id = request.form['sentence_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Sentences WHERE Sentence_ID = %s', (sentence_id,))
        db.commit()
        cursor.close()
        flash('Sentences deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the sentence.')
        print(e)
    return redirect(url_for('GET_sentence_info'))
 


@app.route('/edit_sentence', methods=['POST'])
def edit_sentence():
    sentence_id = request.form['Sentence_ID']
    criminal_id = request.form['Criminal_ID']
    type = request.form['Type']
    prob_id = request.form['Prob_ID']
    start_date = request.form['Start_date']
    end_date = request.form['End_date']
    violations = request.form['Violations']

    try:
        cursor = db.cursor()

        # SQL query to update sentence details
        query = """
        UPDATE Sentences 
        SET Type = %s, Start_date = %s, End_date = %s, Violations = %s
        WHERE Sentence_ID = %s AND Criminal_ID = %s AND Prob_ID = %s
        """
        cursor.execute(query, (type, start_date, end_date, violations, sentence_id, criminal_id, prob_id))

        db.commit()
        cursor.close()
        flash('Sentence updated successfully.')
        return redirect(url_for('GET_sentence_info'))


    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the sentence.')
        print(e)
        return redirect(url_for('GET_sentence_info'))




#  Crime_charges Methods Start Here

def find_crime_charge_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Crime_charges')
    crime_charge_raw = cursor.fetchall()
    crime_charge_info = [{'Charge_ID': row[0], 'Crime_ID': row[1], 'Crime_code': row[2], 'Charge_status': row[3], 'Fine_amount': row[4], 'Court_fee': row[5], 'Amount_paid': row[6], 'Pay_due_date': row[7] } for row in crime_charge_raw]
    return crime_charge_info

@app.route('/GET_crime_charge_info', methods = ['GET']) # Get is the default btw
def GET_crime_charge_info():
    crime_charge_info = find_crime_charge_info()
    return render_template('Crime_charges_Information_Page.html', crime_charge_info = crime_charge_info)


@app.route('/POST_crime_charge', methods = ['POST'])
def POST_crime_charge():
    try:
        Charge_ID = request.form['Charge_ID']
        Crime_ID = request.form['Crime_ID']
        Crime_code = request.form['Crime_code']
        Charge_status = request.form['Charge_status']
        Fine_amount = request.form['Fine_amount']
        Court_fee = request.form['Court_fee']
        Amount_paid = request.form['Amount_paid']
        Pay_due_date = request.form['Pay_due_date']

        cursor = db.cursor()
        query = '''
                INSERT INTO Crime_charges 
                (Charge_ID, Crime_ID, Crime_code, Charge_status, Fine_amount, Court_fee, Amount_paid, Pay_due_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                '''
        cursor.execute(query, (Charge_ID, Crime_ID, Crime_code, Charge_status, Fine_amount, Court_fee, Amount_paid, Pay_due_date))

        db.commit()
        cursor.close()
        return redirect(url_for('GET_crime_charge_info'))
    except IntegrityError as e:
        error_message = "This crime charge already exists."
        crime_charge_info = find_crime_charge_info()
        return render_template('Crime_charges_Information_Page.html', crime_charge_info = crime_charge_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        crime_charge_info = find_crime_charge_info()
        return render_template('Crime_charges_Information_Page.html', crime_charge_info = crime_charge_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        crime_charge_info = find_crime_charge_info()
        return render_template('Crime_charges_Information_Page.html', crime_charge_info = crime_charge_info, error=error_message)
    
@app.route('/delete_crime_charge', methods=['POST'])
def delete_crime_charge():
    crime_charge_id = request.form['crime_charge_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Crime_charges WHERE Charge_ID = %s', (crime_charge_id,))
        db.commit()
        cursor.close()
        flash('Crime Charge deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the crime charge.')
        print(e)
    return redirect(url_for('GET_crime_charge_info'))
 


@app.route('/edit_crime_charge', methods=['POST'])
def edit_crime_charge():
    Charge_ID = request.form['Charge_ID']
    Crime_ID = request.form['Crime_ID']
    Crime_code = request.form['Crime_code']
    Charge_status = request.form['Charge_status']
    Fine_amount = request.form['Fine_amount']
    Court_fee = request.form['Court_fee']
    Amount_paid = request.form['Amount_paid']
    Pay_due_date = request.form['Pay_due_date']

    try:
        cursor = db.cursor()

        # SQL query to update crime charge details
        query = """
        UPDATE Crime_charges 
        SET Crime_ID = %s, Crime_code = %s, Charge_status = %s, Fine_amount = %s, Court_fee = %s, Amount_paid = %s, Pay_due_date = %s
        WHERE Charge_ID = %s
        """
        cursor.execute(query, (Crime_ID, Crime_code, Charge_status, Fine_amount, Court_fee, Amount_paid, Pay_due_date, Charge_ID))

        db.commit()
        cursor.close()
        flash('Crime Charge updated successfully.')
        return redirect(url_for('GET_crime_charge_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the crime charge.')
        print(e)
        return redirect(url_for('GET_crime_charge_info'))




#  Crime_officers Methods Start Here

def find_crime_officer_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Crime_officers')
    crime_officer_raw = cursor.fetchall()
    crime_officer_info = [ { 'Crime_ID': row[0], 'Officer_ID': row[1] } for row in crime_officer_raw ]
    return crime_officer_info

@app.route('/GET_crime_officer_info', methods = ['GET']) # Get is the default btw
def GET_crime_officer_info():
    crime_officer_info = find_crime_officer_info()
    return render_template('Crime_officers_Information_Page.html', crime_officer_info = crime_officer_info)


@app.route('/POST_crime_officer', methods = ['POST'])
def POST_crime_officer():
    try:
        Crime_ID = request.form['Crime_ID']
        Officer_ID = request.form['Officer_ID']
        cursor = db.cursor()
        query = 'INSERT INTO Crime_officers (Crime_ID,Officer_ID) VALUES (%s,%s)'
        cursor.execute(query,(Crime_ID, Officer_ID))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_crime_officer_info'))
    except IntegrityError as e:
        error_message = "A Crime Officers already exists."
        crime_officer_info = find_crime_officer_info()
        return render_template('Crime_officers_Information_Page.html', crime_officer_info = crime_officer_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        crime_officer_info = find_crime_officer_info()
        return render_template('Police_Information_Page.html', crime_officer_info = crime_officer_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        crime_officer_info = find_crime_officer_info()
        return render_template('Police_Information_Page.html', crime_officer_info = crime_officer_info, error=error_message)

@app.route('/delete_crime_officer', methods=['POST'])
def delete_crime_officer():
    crime_officer_id = request.form['crime_officer_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Crime_officers WHERE Crime_ID = %s', (crime_officer_id,))
        db.commit()
        cursor.close()
        flash('Crime Officers deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the crime officers.')
        print(e)
    return redirect(url_for('GET_crime_officer_info'))
 

# should not have edit since both are PK
# @app.route('/edit_crime_officer', methods=['POST'])
# def edit_crime_officer():
#     crime_id = request.form['Crime_ID']
#     officer_id = request.form['Officer_ID']
#     try:
#         cursor = db.cursor()

#         # SQL query to update officer details
#         query = """
#         UPDATE Crime_officers 
#         SET Last = %s, First = %s, Precinct = %s, Badge = %s, Phone = %s, Status = %s
#         WHERE Officer_ID = %s
#         """
#         cursor.execute(query, (last_name, first_name, precinct, badge_number, phone_number, status, officer_id))
        
#         db.commit()
#         cursor.close()
#         flash('Crime officers updated successfully.')
#         return redirect(url_for('GET_crime_officer_info'))

#     except Exception as e:
#         db.rollback()
#         flash('Error occurred while updating the crime officers.')
#         print(e)
#         return redirect(url_for('GET_crime_officer_info'))


#  Appeals Methods Start Here

def find_appeal_info():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM Appeals')
    appeal_raw = cursor.fetchall()
    appeal_info = [ { 'Appeal_ID': row[0], 'Crime_ID': row[1], 'Filing_date': row[2], 'Hearing_date': row[3], 'Status': row[4] } for row in appeal_raw ]
    return appeal_info

@app.route('/GET_appeal_info', methods = ['GET']) # Get is the default btw
def GET_appeal_info():
    appeal_info = find_appeal_info()
    return render_template('Appeals_Information_Page.html', appeal_info = appeal_info)


@app.route('/POST_appeal', methods = ['POST'])
def POST_appeal():
    try:
        Appeal_ID = request.form['Appeal_ID']
        Crime_ID = request.form['Crime_ID']
        Filing_date = request.form['Filing_date']
        Hearing_date = request.form['Hearing_date']
        Status = request.form['Status']

        cursor = db.cursor()
        query = 'INSERT INTO Appeals (Appeal_ID, Crime_ID, Filing_date, Hearing_date, Status) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (Appeal_ID, Crime_ID, Filing_date, Hearing_date, Status))
        db.commit()
        cursor.close()
        return redirect(url_for('GET_appeal_info'))
    except IntegrityError as e:
        error_message = "This Appeal already exists."
        appeal_info = find_appeal_info()
        return render_template('Appeals_Information_Page.html', appeal_info = appeal_info, error=error_message)
    except DataError as de:
        error_message = "Please input appropriate values for the fields"
        appeal_info = find_appeal_info()
        return render_template('Appeals_Information_Page.html', appeal_info = appeal_info, error=error_message)
    except DatabaseError as de:
        error_message = "Please input appropriate values for the fields"
        appeal_info = find_appeal_info()
        return render_template('Appeals_Information_Page.html', appeal_info = appeal_info, error=error_message)
    
@app.route('/delete_appeal', methods=['POST'])
def delete_appeal():
    appeal_id = request.form['appeal_id']
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM Appeals WHERE Appeal_ID = %s', (appeal_id,))
        db.commit()
        cursor.close()
        flash('Appeal deleted successfully.')
    except Exception as e:
        db.rollback()
        flash('Error occurred while deleting the appeal.')
        print(e)
    return redirect(url_for('GET_appeal_info'))
 


@app.route('/edit_appeal', methods=['POST'])
def edit_appeal():
    Appeal_ID = request.form['Appeal_ID']
    Crime_ID = request.form['Crime_ID']
    Filing_date = request.form['Filing_date']
    Hearing_date = request.form['Hearing_date']
    Status = request.form['Status']

    try:
        cursor = db.cursor()

        # SQL query to update appeal details
        query = """
        UPDATE Appeals 
        SET Crime_ID = %s, Filing_date = %s, Hearing_date = %s, Status = %s
        WHERE Appeal_ID = %s
        """
        cursor.execute(query, (Crime_ID, Filing_date, Hearing_date, Status, Appeal_ID))

        db.commit()
        cursor.close()
        flash('appeals updated successfully.')
        return redirect(url_for('GET_appeal_info'))

    except Exception as e:
        db.rollback()
        flash('Error occurred while updating the appeal.')
        print(e)
        return redirect(url_for('GET_appeal_info'))






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



# # Appeals Methods

# def find_appeal_info():
#    cursor = db.cursor()
#    cursor.execute('SELECT * FROM Appeals')
#    Appeals_raw = cursor.fetchall()
#    Appeals_info = [{'Appeal_ID': row[0], 'Crime_ID': row[1], 'Filing_date': row[2], 'Hearing_date': row[3], 'Status': row[4]} for row in Appeals_raw]
#    return Appeals_info

# @app.route('/GET_appeal_info', methods = ['GET']) # Get is the default btw
# def GET_appeal_info():
#     appeal_info = find_appeal_info()
#     return render_template('Appeals_Information_Page.html', appeal_info = appeal_info)



# Joining Tables Page Method

@app.route('/join_tables') # Get is the default btw
def GET_join_tables():
    return render_template('Join_Tables.html')

# Routing the Join requests from the user
@app.route('/joins', methods = ['POST'])
def GET_joined_tables():
    selected_tables = request.form.getlist('table')

    if not selected_tables:
        error_message = "Please select at least one table to join"
        officer_info = find_officer_info()
        return render_template('Join_Tables.html', error=error_message)
    # joined_data = perform_table_join(selected_tables)
    cursor = db.cursor()
    query = 'SELECT * FROM '+selected_tables[0]
    for table in selected_tables[1:]:
        query += ' NATURAL JOIN '+table
    cursor.execute(query)
    column_names = cursor.column_names
    joined_data_raw = cursor.fetchall()
    if joined_data_raw == []:
        error_message = "Cannot join these tables"
        officer_info = find_officer_info()
        return render_template('Join_Tables.html', error=error_message)
    cursor.close()
    joined_data = [dict(zip(column_names, row)) for row in joined_data_raw]
    return render_template('Join_Tables.html', joined_data = joined_data, tables=selected_tables)


# AI Natural Language to SQL Query Page Methods

@app.route('/AI_NL_to_SQL')
def GET_query():
    return render_template('AI_NL_to_SQL.html')

# Routing the AI NL to SQL Query requests from the user
@app.route('/ai', methods=['GET', 'POST'])
def AI_query():
    if request.method == 'POST':

        database_schema = """ 
    CREATE TABLE Criminals (
    Criminal_ID DECIMAL(6,0) NOT NULL,
    Last VARCHAR(15),
    First VARCHAR(10),
    Street VARCHAR(30),
    City VARCHAR(20),
    State CHAR(2),
    Zip CHAR(5),
    Phone CHAR(10),
    V_status CHAR(1) DEFAULT 'N',
    P_status CHAR(1) DEFAULT 'N',
    PRIMARY KEY (Criminal_ID)
);
-- Criminals V_status Y (Yes), N (No) 
-- Criminals P_status Y (Yes), N (No) 

CREATE TABLE Crimes (
    Crime_ID DECIMAL(9,0) NOT NULL ,
    Criminal_ID DECIMAL(6,0) NOT NULL,
    Classification CHAR(1) DEFAULT 'U',
    Date_charged DATE,
    Status CHAR(2) NOT NULL,
    Hearing_date DATE,
    Appeal_cut_date DATE,
    PRIMARY KEY (Crime_ID),
    FOREIGN KEY (Criminal_ID) REFERENCES Criminals(Criminal_ID),
    CHECK (Hearing_date > Date_charged)
);
-- Crimes Classification F (Felony), M (Misdemeanor), O (Other), U (Undefined) 
-- Crimes Status CL (Closed), CA (Can Appeal), IA (In Appeal) 

CREATE TABLE Alias (
  Alias_ID DECIMAL(6,0) NOT NULL,
  Criminal_ID DECIMAL(6,0) NOT NULL,
  Alias VARCHAR(20),
  PRIMARY KEY (Alias_ID),
  FOREIGN KEY (Criminal_ID) REFERENCES Criminals(Criminal_ID)
);

CREATE TABLE Prob_officer (
  Prob_ID DECIMAL(5,0) NOT NULL,
  Last VARCHAR(15),
  First VARCHAR(10),
  Street VARCHAR(30),
  City VARCHAR(20),
  State CHAR(2),
  Zip CHAR(5),
  Phone CHAR(10),
  Email VARCHAR(30),
  Status CHAR(1) NOT NULL,
  PRIMARY KEY (Prob_ID)
);
-- Prob_officers Status A (Active), I (Inactive) 


CREATE TABLE Sentences (
  Sentence_ID DECIMAL(6,0) NOT NULL,
  Criminal_ID DECIMAL(6,0) NOT NULL,
  Type CHAR(1),
  Prob_ID DECIMAL(5,0) NOT NULL,
  Start_date DATE,
  End_date DATE,
  Violations DECIMAL(3,0) NOT NULL,
  PRIMARY KEY (Sentence_ID),
  FOREIGN KEY (Criminal_ID) REFERENCES Criminals(Criminal_ID),
  FOREIGN KEY (Prob_ID) REFERENCES Prob_officer(Prob_ID),
  CHECK (End_date >= Start_date)
);
-- Sentences Type J ( Jail Period), H (House Arrest), P (Probation) 


CREATE TABLE Crime_codes (
  Crime_code DECIMAL(3) NOT NULL,
  Code_description VARCHAR(30) NOT NULL UNIQUE,
  PRIMARY KEY (Crime_code)
);

CREATE TABLE Crime_charges (
  Charge_ID DECIMAL(10,0) NOT NULL,
  Crime_ID DECIMAL(9,0) NOT NULL,
  Crime_code DECIMAL(3,0) NOT NULL,
  Charge_status CHAR(2),
  Fine_amount DECIMAL(7, 2),
  Court_fee DECIMAL(7, 2),
  Amount_paid DECIMAL(7, 2),
  Pay_due_date DATE,
  PRIMARY KEY (Charge_ID),
  FOREIGN KEY (Crime_ID) REFERENCES Crimes(Crime_ID),
  FOREIGN KEY (Crime_code) REFERENCES Crime_codes(Crime_code)
);

-- Crime_charges Charge_status PD (Pending), GL (Guilty), NG (Not Guilty) 

 
CREATE TABLE Officers (
  Officer_ID DECIMAL(8,0) NOT NULL,
  Last VARCHAR(15),
  First VARCHAR(10),
  Precinct CHAR(4) NOT NULL,
  Badge VARCHAR(14) UNIQUE,
  Phone CHAR(10),
  Status CHAR(1) DEFAULT 'A',
  PRIMARY KEY (Officer_ID)
);
-- Officers Status A (Active), I (Inactive) 

CREATE TABLE Crime_officers (
  Crime_ID DECIMAL(9,0) NOT NULL,
  Officer_ID DECIMAL(8,0) NOT NULL,
  PRIMARY KEY (Crime_ID, Officer_ID),
  Constraint crime_officers_fk1 FOREIGN KEY (Crime_ID) REFERENCES Crimes(Crime_ID),
  Constraint crime_officers_fk2 FOREIGN KEY (Officer_ID) REFERENCES Officers(Officer_ID)
);


CREATE TABLE Appeals (
  Appeal_ID DECIMAL(5,0) NOT NULL,
  Crime_ID DECIMAL(9,0) NOT NULL,
  Filing_date DATE,
  Hearing_date DATE,
  Status CHAR(1) DEFAULT 'P',
  PRIMARY KEY (Appeal_ID),
  FOREIGN KEY (Crime_ID) REFERENCES Crimes(Crime_ID)
);
-- Appeals Status P (Pending), A (Approved), D (Disapproved)


CREATE TABLE Users (
    ID INT AUTO_INCREMENT PRIMARY KEY UNIQUE,
    Username VARCHAR(20) NOT NULL UNIQUE,
    User_Password VARCHAR(20) NOT NULL,
    Write_access BOOLEAN NOT NULL
);"""


        OPENAI_API_KEY = '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'

        # Ensure the API key is set
        if not OPENAI_API_KEY:
            raise ValueError("No OpenAI secret key found. Set the OPENAI_API_KEY environment variable.")

        # Set the API key
        openai.api_key = OPENAI_API_KEY

        # Your existing code for the query
        question = request.form['user_question']

        # Create a client and make a request

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a police records website that is connected to a database of police officers and criminals. When the user asks a question, you must output the SQL query that can be run against the database to return the data that answers the question. ONLY RETURN THE SQL QUERY, DO NOT INLCUDE ANY OTHER TEXT PLEASE! Use the provided database schema to answer the questions. The SQL commands to create the database schema are as follows: "+database_schema},
                {"role": "user", "content": question}
            ]
        )
        query = response.choices[0].message.content

        # answer = response['choices'][0].get('message', {}).get('content', '')

        cursor = db.cursor()
        try:
            cursor.execute(query)
            column_names = cursor.column_names
            joined_data_raw = cursor.fetchall()

            if joined_data_raw == []:
                error_message = "This question cannot be answered with the database."
                officer_info = find_officer_info()
                return render_template('AI_NL_to_SQL.html', error=error_message)
            cursor.close()
            joined_data = [dict(zip(column_names, row)) for row in joined_data_raw]
    
            return render_template('AI_NL_to_SQL.html', query=query, joined_data = joined_data, question = question)

        except mysql.connector.errors.ProgrammingError as e:
            if e.errno == 1054:
            
                error_message = "This question cannot be answered with the database."
                officer_info = find_officer_info()
                return render_template('AI_NL_to_SQL.html', error=error_message)


        finally:
            # Make sure to close the cursor and connection
            cursor.close()


if __name__ == '__main__':
    app.run(debug=True)


