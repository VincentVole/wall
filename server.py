from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import MySQLConnector
import re
import md5
import os, binascii
app = Flask(__name__)
app.secret_key = 'sdf1j3kjf02i9efhwj'
mysql = MySQLConnector(app,'lardb')
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
	if request.form['form_type'] == 'register':
		valid = True
		#fields can't be blank
		if len(request.form['email']) < 1:
			flash('Email cannot be empty!', 'email')
			valid = False
		if len(request.form['first_name']) < 2:
			flash('First name must be at least 2 characters long!', 'first_name')
			valid = False
		if len(request.form['last_name']) < 2:
			flash('Last name must be at least 2 characters long!', 'last_name')
			valid = False
		if len(request.form['password']) < 1:
			flash('Password cannot be empty!', 'password')
			valid = False
		if len(request.form['confirm_password']) < 1:
			flash('Confirm password cannot be empty!', 'confirm_password')
			valid = False

		#must have valid email
		EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
		if not EMAIL_REGEX.match(request.form['email']):
			flash('Invalid email!', 'email')
			valid = False

		#first and last names can't contain numbers

		# NAME_REGEX = re.compile(r'\d')
		# if NAME_REGEX.search(request.form['first_name']):
		# 	flash('First name may not contain numbers!', 'first_name')
		# if NAME_REGEX.search(request.form['last_name']):
		# 	flash('Last name may not contain numbers!', 'last_name')

		NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
		if not NAME_REGEX.search(request.form['first_name']):
			flash('First name must contain only letters!', 'first_name')
			valid = False
		if not NAME_REGEX.search(request.form['last_name']):
			flash('Last name must contain only letters!', 'last_name')
			valid = False


		#password must be more than 8 characters
		if len(request.form['password']) < 8:
			flash('Password has to be at least 8 characters!', 'password')
			valid = False

		#passord and confirm password fields must match
		if request.form['password'] != request.form['confirm_password']:
			flash('Passwords must match!', 'password')
			flash('Passwords must match!', 'confirm_password')
			valid = False

		users = mysql.query_db("SELECT users.id as id, users.email as email, users.password as password FROM users")
		for user in users:
			if request.form['email'] == user['email']:
				valid = False
				flash('That email already has an account associated with it!', 'email')

		if valid:
			flash('Registration successful! Thank you!', 'register')
			salt = binascii.b2a_hex(os.urandom(15)) #15 is number of bytes we get back. b2a turns string into normal alphanumeric string
			
			query = "INSERT INTO users(first_name, last_name, email, password, salt, created_at, updated_at) VAlUES(:first_name, :last_name, :email, :password, :salt, NOW(), NOW())"
			data = {
				'first_name': request.form['first_name'],
				'last_name': request.form['last_name'],
				'email': request.form['email'],
				'password': md5.md5(request.form['password'] + salt).hexdigest(),
				'salt': salt
			}
			mysql.query_db(query, data)
		return redirect('/')
	elif request.form['form_type'] == 'login':
		#fields can't be blank
		if len(request.form['email']) < 1:
			flash('Email cannot be empty!', 'login_email')
		#email must be valid
		EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
		if not EMAIL_REGEX.match(request.form['email']):
			flash('Invalid email!', 'login_email')
		#check password
		users = mysql.query_db("SELECT users.id as id, users.email as email, users.password as password, users.salt as salt FROM users")
		email_in_db = False
		for user in users:
			if request.form['email'] == user['email']:
				print user
				hashed_password = md5.md5(request.form['password'] + user['salt']).hexdigest()
				if hashed_password == user['password']:
					session['user'] = user['id']
				else:
					flash('Email and password do not match!', 'login_pass')
				email_in_db = True
		if not email_in_db:
			flash('That user does not exist.', 'login_pass')
		return redirect('/')
	elif request.form['form_type'] == 'logout':
		session.clear()
		return redirect('/')


app.run(debug=True)