from flask import Flask, url_for, render_template, request, redirect, abort, flash #import Flask class
from markupsafe import escape
from flask_wtf import FlaskForm #HTML forms written in python using the wtforms library
from wtforms.fields import *
from wtforms.widgets import TextArea
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerRangeField, FileField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo

app = Flask(__name__) #create object instance of a Flask for our application
app.config['SECRET_KEY'] = 'a09ac98119958768d24d2fb80baa24203416cf6b' #a secret key for my app that will protect HTML forms against cross site request forgery (CSRF) attacks and any potential web exploits

    
#this is a Flask decorator; decorators are wrappers to functions which we can modify for our own use
@app.route('/register', methods=['GET', 'POST']) #first parameter is the URL the flask maps to, second parameter is to specify the HTTP methods the webpage is allowed to respond to. POST is a HTTP request that is used to send data to a server to create/update a resource. GET is used to request data from a resource.
def register(): #defining register function that will enable users to register their user credentials and create an account
    
    form = RegisterForm() #this is an object instance of our RegisterForm class which is passed into a template to generate the necessary HTML form for user registration
    
    if form.validate_on_submit(): #if the form is validated when it was submitted
        flash(f'Account created for {form.username.data}.', 'success') #the flash function notifies the user their account has been created upon registration; f string includes the notification in string form, with the inputted username as the placeholder. The second argument will make the flash notification green, for success.
        return redirect(url_for('login')) #redirects user to login page after registration.
    
    if request.method == 'POST': #if the request is to send data to a server AKA POST request
        db = sqlite3.connect('users.db') #then connect to a database which will store user credentials
        c = db.cursor() #initialize db cursor that will let me manipulate the database
        
        try: #try block is only triggered once with the one-time creation of the table
            c.execute('CREATE TABLE IF NOT EXISTS Users (Username TEXT PRIMARY KEY, Password TEXT)') #SQL statement that creates the Users table, which will have two columns: Username being the primary key and accepting text format, and password accepting text format.
            db.commit() #commit the changes to the database
        except: #except block is triggered every time as long as the Users table exists
            pass #pass statement will allow the program to navigate to the subsequent lines of code
        
        c.execute('INSERT INTO Users VALUES(?, ?);', (form.username.data, form.password.data)) #SQL statement that will insert the inputted User credential values into the Users table, by referencing the form and extracting the values from it
        db.commit() #commit the changes to the database
        return render_template(register.html, page_title = Register, page_form = form) #return registration form by rendering the HTML template for it
        #the first argument references the html template file, the second argument sets the name of the page, and the third argument passes in the registration form 
    else:
        return render_template('register.html', page = url_for('register')) #otherwise, displays the HTML page for the register form
            #we have two parameters: html file name, & the variable 'page' (referenced in the HTML) and its value which is the URL of the webpage referenced through the function name

                  
@app.route('/login', methods=['GET', 'POST']) #this flask maps to the login url, with both vital HTTP methods specified in the decorator
def login(): #defining login function that will enable users to log in to their accounts after registering
    
    form = LoginForm() #this is an object instance of our LoginForm class which is passed into a template to generate the necessary HTML form for user login
    
    if form.validate_on_submit(): #if the form is validated on submit
        if form.username.data == "admin": #given that the username the user provided in the form is admin
            return redirect(url_for('addBook')) #redirect that user to the page where they're able to add stock/books. The redirect method was used here for this task, as well as the url_for method as the argument which references the function used for adding stock
        else:
            flash('Access denied.', 'danger') #otherwise notify the user that they can't access this page, by displaying a flash box in red, where the colour red is made possible with the second argument passed in, which is a bootsrap element
                  
    if request.method == 'POST': #if the request is to send data to a server AKA POST request
        db = sqlite3.connect('users.db') #then connect to the database which will examine user credentials according to what's stored in the Users table
        c = db.cursor() #initialize db cursor that will let me manipulate the database
        c.execute("SELECT Username, Password FROM Users WHERE Username=? AND Password=?;", (form.username.data, form.password.data)) #SQL statement that checks for the username and password values in the table that the user inputted into the login form, by referencing the form object and extracting the values from it by calling its attributes     

    if(int(c.fetchone()[0]))>0: #This checks if there are any present values in the tables, and if valid
        flash('Login successful.', 'success') #the flash function notifies the user their account has been logged into upon success
        return render_template('login.html', page_title = 'Login', page_form = form) #displays the html page for the login page by rendering the HTML template for it
                  
    else:
        flash('Login unsuccessful', 'danger') #otherwise display a flash error message that notifies the login has been unsuccessful
        redirect(url_for(wrong_password)) #redirect the user to the template referenced with its function name, which is a simple html page that tells the user either their username or password was wrong

        
@app.errorhandler(403) #this decorator allows us to modify error messages for the end user to see
def wrong_password(error):
    return render_template('wrong_passwd.html'), 403 #writing our own error message by redirecting to a dedicated page for the error    

                  
@app.route('/home', methods=["POST", "GET"]) #this flask maps to the homepage URL, where the admin user can add a book/stock. It accepts both vital HTTP methods that are specificed as an argument in the decorator
def addBook(): #this function allows the admin user to add a book for sale by providing all the necessary information about it
                  
    form = AddBook() #this is an object instance of our AddBookForm class which is passed into a template to generate the necessary HTML form for adding a book/stock into the system
                    
    if request.method == "POST": #if the HTTP request is a POST, AKA requesting to send data to a server
        db = sqlite3.connect('books.db') #then connect to a database which will store all the details about a book the admin user wants to sell
        c = db.cursor() #initialize db cursor that will let me manipulate the database
                  
        try: #try block is only triggered once with the one-time creation of the table
            c.execute('CREATE TABLE IF NOT EXISTS Books (ISBN TEXT PRIMARY KEY, Author TEXT, Description TEXT, Name TEXT, Publish_Date DATE, Trade_Price FLOAT, Retail_Price FLOAT, Quantity INTEGER)') #SQL statement to create the Books table and all the necessary columns; the notable one being the ISBN column which is the primary key considering it's unique for each book, therefore it can be used to uniquely identify records
            db.commit() #commit the changes to the database
    except: #try block is only triggered once with the creation of the table
            pass #pass statement will allow the program to navigate to the subsequent lines of code
                  
        c.execute('INSERT INTO Books VALUES(?,?,?,?,?,?,?,?);',
                 (form.bookISBN.data, form.bookAuthor.data, form.bookDes.data, form.bookName.data,
                  form.bookPubDate.data, form.bookTradePrice.data,
                  form.bookRetailPrice.data, form.bookQuantity.data)) #SQL statement that will insert the inputted values relating to the book into the Books table, by referencing the form instance and extracting the values from it by calling its attributes        
                  
        db.commit() #commit the changes to the database
        return flash('Submitted', 'succcess') #display a flash message to the user to notify them they have successfully added a book/stock
                  
    else:
        return redirect(url_for(addBook)) #otherwise, redirect the user back to the page

    
#the 3 classes below are substitutes for writing forms in HTML; instead, I wrote them in python and referenced them in my templates where they're converted into HTML forms
    
class RegisterForm(FlaskForm): #the creation of the Register form, where the user will register their user credentials
    username = StringField('Username', validators = [DataRequired()]) #the username attribute is specified to be a text/string field. The first argument passed into the function is the value to be displayed, and the second argument ensures/validates that the user has provided the data
    password = PasswordField('Password', validators = [DataRequired(), Length(min=8, max=16)]) #the password attribute is specified to be a password, where the first argument passed into the function is the value to be displayed, the second argument ensures/validates that the user has provided the data, it will also requires the user password to be at least 8 characters long, which is found to be the minimum optimal password length according to a Microsoft article
    confirm_password = EqualTo('Confirm Password', validators = [DataRequired(), EqualTo(password)]) #the confirm_password attribute is for the user to repeat their password to validate that the initial password the user inputted is correct by equating them and evaluating if they're the same. The first parameter is how the displayed value, the second parameter ensures that the user has provided the data, as well as validating that the inputted data is equal to the data inputted into the password attribute. 
    submit = SubmitField('Register') #the submit attribute is basically a button that the user clicks to submit all the information they provided for the form        #syntax error here, password in equal to function needs to be in lower case, not upper
    
                  
class LoginForm(FlaskForm): #the creation of the Login form, where the user will provide data to the form to authenticate their login process
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired(), Length(min=8, max=16)]) 
    rememeber = BooleanField('Remember me?') #the remember attribute has a boolean field assigned to it, meaning the form will ask if the user wants the app to remember their user details for faster logins in the future
    submit = SubmitField('Log in') #the submit attribute is basically a button that the user clicks to submit all the information they provided for the form
    
                  
class AddBookForm(FlaskForm): #the creation of the Add book/stock form, where the user will provide the necessary data about the books they want to sell
    bookName = StringField('Name', validators = [DataRequired()])
    bookAuthor = StringField('Author', validators = [DataRequired()])
    bookDesc = StringField('Description', widget=TextArea()) #the second argument for the attribute provides an area where the user can type the description in
    bookISBN = StringField('ISBN', validators = [DataRequired()]) #the name, author, description and ISBN of the book will need to be inputted by the user as a requirement as per the validator argument
    bookPubDate = DateField('Publication Date', validators = [DataRequired()], format='%d-%m-%y') #a date field is used for the publication date, where the date format is specified as the third argument in the method
    bookCover = FileField('Front Cover', validators = [DataRequired()]) #a file field is used to store the cover of the book in a file
    bookTradePrice = IntegerRangeField('Trade Price', validators = [DataRequired()])
    bookRetailPrice = IntegerRangeField('Retail Price', validators = [DataRequired()])
    bookQuantity = IntegerRangeField('Quantity', validators = [DataRequired()]) #integer fields are used for the prices and quantities since the data is of numerical nature for these attributes 
    addBook = SubmitField('Add Stock') #the submit field is used here for the addBook attribute to allow the user to submit the form after they've provided all the necessary information about a book