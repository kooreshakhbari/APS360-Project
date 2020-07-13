from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import flask_login
import os
app = Flask(__name__)
app.secret_key = 'secret string lol'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))



users = {'aps360': {'password': 'Group.32'}}

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@app.route('/')
def login_page():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = request.form['email']
    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('upload_file'))

    return self.login_manager.unauthorized()

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/upload')
@flask_login.login_required
def upload_file():
   return render_template('/upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
@flask_login.login_required
def upload_file1():
   if request.method == 'POST':
      # files = request.files.getlist("file")
      # for f in files:
      #    f.save(secure_filename(f.filename))
      # return 'file uploaded successfully'

      target = os.path.join(APP_ROOT, 'images/')
      print(target)
      if not os.path.isdir(target):
         os.mkdir(target)
      else:
         print("Couldn't create upload directory: {}".format(target))
      print(request.files.getlist("file"))
      for upload in request.files.getlist("file"):
         print(upload)
         print("{} is the file name".format(upload.filename))
         filename = upload.filename
         destination = "/".join([target, filename])
         print ("Accept incoming file:", filename)
         print ("Save it to:", destination)
         upload.save(destination)
      return 'file uploaded successfully'

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/gallery')
@flask_login.login_required
def get_gallery():

   image_names = os.listdir('./images')
   print(image_names)
   return render_template("gallery.html", image_names=image_names)
		
if __name__ == '__main__':
   app.run(debug = True)