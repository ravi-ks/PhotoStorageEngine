import os
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto import Random
import atexit 
import sys
import pathlib
import time
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="WTbot",
  password="lufthansaWT"
)

mycursor = mydb.cursor()
mycursor.execute("use webTechnologyProject")
mycursor.execute("SELECT * FROM authentication")

myresult = mycursor.fetchall()

valid_usernames = []
valid_passwords = []

for x in myresult:
  valid_usernames.append(x[0])
  valid_passwords.append(x[1])

mycursor.execute("SELECT * FROM rsa")
myresult = mycursor.fetchall()

key = ""
iv = ""

for x in myresult:
  key = x[0]
  iv = x[1]
  
app = Flask(__name__)

app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.jpeg']
app.config['UPLOAD_PATH'] = 'static/images'
pathToImagesDir = "/home/ravi_kumar/wt_project/flask_clone/static/images/" 
pathToStaticDir = "/home/ravi_kumar/wt_project/flask_clone/static/" 
global loggedIn
loggedIn = False

@atexit.register 
def goodbye(): 
    allImages = os.listdir('static/images')
    for files in allImages:
        if files.lower().endswith('.enc'):
            p = pathlib.Path(pathToImagesDir + "new_" + os.path.splitext(files)[0])
            if p.is_file():
                os.remove(pathToImagesDir + "new_" + os.path.splitext(files)[0])
  
@app.route('/')
def login():
     global loggedIn
     loggedIn = False
     return render_template('login.html')

@app.route('/login', methods=['POST'])
def authenticate():
     global loggedIn
     user_name=request.form['uname']
     user_passwd=request.form['psw']
     if user_name in valid_usernames:
          if user_passwd in valid_passwords:
               loggedIn = True
               return redirect(url_for('index'))
     return render_template('unsuccessfull_login.html')

       
@app.route('/index')
def index():
    global loggedIn
    if loggedIn:
        return render_template('index.html')    
    else:
        return redirect(url_for('login'))

        
@app.route('/upload')
def upload():
    global loggedIn
    if loggedIn:
        return render_template('upload.html')
    else:
        return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("file")
    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                
    return redirect(url_for('gallery'))

@app.route('/hide', methods=['POST'])
def hide_files():
    uploaded_files = request.files.getlist("file")
    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                encrypt(pathToImagesDir + filename)
                os.remove(os.path.join(app.config['UPLOAD_PATH'], filename))
                delete_original(filename, 0)
                #decrypt(enc_file_name)
    return redirect(url_for('gallery'))

@app.route('/hide_img_gallery', methods=['POST'])
def hide_img_gallery():
    uploaded_files = request.form["hide"]
    #print("uploaded files: ")
    #print(uploaded_files)
    filename_list = uploaded_files.split('/')
    temp = filename_list[1].split('_')
    filename_list1=""
    for i in range(1, len(temp)-1):
        filename_list1 = filename_list1 + temp[i] + "_"
    filename_list1 = filename_list1 + temp[len(temp)-1]
    filename = filename_list1
    #print("file to be encrypted: \n" + filename)
    encrypt(pathToImagesDir + filename)
    delete_original(filename, 1)
    return redirect(url_for('gallery'))

def delete_original(filename, fromGallery):
    if fromGallery == 0:
          dir_path = os.path.dirname("/home/ravi_kumar/Pictures") 
  
          for root, dirs, files in os.walk(dir_path): 
              for file in files:  
            
                  # change the extension from '.mp3' to  
                  # the one of your choice. 
                  if file==filename: 
                      os.remove(root+'/'+str(file)) 
            
          dir_path = os.path.dirname("/home/ravi_kumar/Images") 
  
          for root, dirs, files in os.walk(dir_path): 
              for file in file:  
            
                  # change the extension from '.mp3' to  
                  # the one of your choice. 
                  if file==filename: 
                      os.remove(root+'/'+str(file))  
    else:
          dir_path = os.path.dirname("/home/ravi_kumar/wt_project/flask_clone/static/images") 
  
          for root, dirs, files in os.walk(dir_path): 
              for file in files:  
            
                  # change the extension from '.mp3' to  
                  # the one of your choice. 
                  if file==filename: 
                      os.remove(root+'/'+str(file))
                      
                                
def encrypt(uploaded_file):
        input_file = open(uploaded_file)
        input_data = input_file.read()
        input_file.close()

        cfb_cipher = AES.new(key, AES.MODE_CFB, iv)
        enc_data = cfb_cipher.encrypt(input_data)

        enc_file = open(uploaded_file+".enc", "w")   
        enc_file.write(enc_data)
        enc_file.close()
        
def decrypt(encrypted_file):
        enc_file2 = open(pathToImagesDir + encrypted_file)
        enc_data2 = enc_file2.read()
        enc_file2.close()

        cfb_decipher = AES.new(key, AES.MODE_CFB, iv)
        plain_data = cfb_decipher.decrypt(enc_data2)
        fname = os.path.splitext(encrypted_file)[0]
        output_file = open(pathToImagesDir + "new_" + fname, "w")
        output_file.write(plain_data)
        output_file.close()
      
@app.route('/about')
def about():
    global loggedIn
    if loggedIn:
        return render_template('about.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/contact')
def contact():
    global loggedIn
    if loggedIn:
        return render_template('contact.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/contact', methods=['POST'])
def contact_queries():
          mycursor = mydb.cursor()
          sql = "INSERT INTO contactQueries VALUES (%s, %s, %s)"
          val = (request.form['name'], request.form['mail'], request.form['message'])
          mycursor.execute(sql, val)
          mydb.commit()
          return redirect(url_for('index'))
    
@app.route('/gallery', methods=['POST', 'GET'])
def gallery():
    global loggedIn
    if loggedIn:
        canUnhide = []
        canHide = []
        allImages = os.listdir('static/images')
        for files in allImages:
            if files.lower().endswith('.enc'):
                decrypt(files)
                canUnhide.append("images/new_" + os.path.splitext(files)[0])
        allImages = os.listdir('static/images')
        #print(canUnhide)
        allImages= ['images/' + file for file in allImages if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        #print(allImages)
        
        return render_template('gallery.html', allImages = allImages, canUnhide = canUnhide, canUnhidelen = len(canUnhide))
    
    else:
        return redirect(url_for('login'))
        

@app.route('/delete',  methods=['POST', 'GET'])
def delete_image():
    if request.method == 'POST':
        imageToBeDeleted = request.form['delete']
        imageToBeDeleted11 = imageToBeDeleted.split('/')
        temp = imageToBeDeleted11[1].split('_')
        imageToBeDeleted1=""  
        for i in range(1, len(temp)-1):
                  imageToBeDeleted1 = imageToBeDeleted1 + temp[i] + "_"
        imageToBeDeleted1 = imageToBeDeleted1 + temp[len(temp)-1]
        p = pathlib.Path(pathToImagesDir + imageToBeDeleted1+'.enc')
        if p.is_file():
            os.remove(pathToImagesDir + imageToBeDeleted1+'.enc')
        os.remove(pathToStaticDir + imageToBeDeleted)
        return redirect(url_for('gallery'))
        

@app.route('/unhide', methods=['POST', 'GET'])
def unhide_image():
    if request.method == 'POST':
        imageToBeDeleted = request.form['unhide']
        imageToBeDeleted11 = imageToBeDeleted.split('/')
        temp = imageToBeDeleted11[1].split('_')
        imageToBeDeleted1=""
        for i in range(1, len(temp)-1):
                  imageToBeDeleted1 = imageToBeDeleted1 + temp[i] + "_"
        imageToBeDeleted1 = imageToBeDeleted1 + temp[len(temp)-1]
        p = pathlib.Path(pathToImagesDir + imageToBeDeleted1 + '.enc')
        if p.is_file():
            os.remove(pathToImagesDir + imageToBeDeleted1 + '.enc')
        if imageToBeDeleted11[1].split('_')[0] == 'new':
            os.rename(pathToImagesDir + 'new_' + imageToBeDeleted1, pathToImagesDir + imageToBeDeleted1)
        return redirect(url_for('gallery'))
        

           
sys.tracebacklimit = 0
if __name__ == '__main__':
    app.run(debug = True)
