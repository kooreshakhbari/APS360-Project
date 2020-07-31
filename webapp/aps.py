from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
from jinja2 import Template
import flask_login
import os
import numpy as np
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.utils.data import ConcatDataset
from torch.autograd import Variable
import os
from PIL import Image
import requests
    
classes = ['almond', 'apple', 'asparagus', 'bacon', 'banana', 'beef_ground',
            'beef_steak', 'blueberries', 'bun_hotdog', 'cabbage', ' carrot', 
            'cauliflower', 'celery', 'cheese_shredded', 'chicken_breast', 
            'chicken_leg', 'corn',  'cucumber', 'egg', 'garlic',
            'grape', 'ketchup', 'lemon', 'lobster', 'mango',
            'mayonnaise', 'milk', 'mushroom', 'mustard', 'noodle', 'oil_vegetable', 
            'onion', 'orange', 'pepper_bell', 'pepper_chile', 
            'pineapple', 'potato', 'rice', 'salmon', 'sausage', 'scallion',
            'shrimp', 'spaghetti', 'spinach', 'tomato']
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


#Logout route
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

#Default route
@app.route('/')
def login_page():
    return redirect(url_for('login'))

#Login route, show login html and post to check creds
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('/login.html')
    else:
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



#Upload route, come to this after user logs in successfully
@app.route('/upload')
@flask_login.login_required
def upload_file():
   return render_template('/upload.html')
	
#This is called from the upload.html form
@app.route('/uploader', methods = ['GET', 'POST'])
@flask_login.login_required
def upload_file1():
    if request.method == 'POST':
        target = os.path.join(APP_ROOT, 'images/')
        print(target)
        if not os.path.isdir(target):
            os.mkdir(target)
        else:
            print("Couldn't create upload directory: {}".format(target))
            #Redirect to error page
        
        print(request.files.getlist("file"))
        for upload in request.files.getlist("file"):
            print(upload)
            print("{} is the file name".format(upload.filename))
            filename = str(time.time()) + upload.filename
            destination = "/".join([target, filename])
            print ("Accept incoming file:", filename)
            print ("Save it to:", destination)
            upload.save(destination)
        #print(request.form['ex_ing'])
        exluded = str(request.form['ex_ing'])
        return redirect(url_for('run_ai', exc_list=exluded))


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

#You can go to this manually to see all the uploaded images
@app.route('/gallery')
@flask_login.login_required
def get_gallery():

   image_name = os.listdir('./images')
   print(image_name)
   return render_template("gallery.html", image_names=enumerate(image_name), labels=image_name)


#Come here after all files get uploaded
#Here we run ai model and get the labels
@app.route('/ai')
@flask_login.login_required
def run_ai():

    folder_path = "./images"
    image_names = os.listdir('./images')
    labels = []
    for img in os.listdir(folder_path):
        if (img.endswith(".jpg") 
            or img.endswith(".png")
            or img.endswith(".JPG")
            or img.endswith(".PNG")):
            labels.append(classify_image(folder_path + "/" + img))
    print("The labels are: " + str(labels))
    #TODO: Change labels=images_names to labels
    return render_template("model_output.html", image_names=enumerate(image_names), labels=labels, len_images=len(image_names), excluded=session.get("exc_list", None))

class Transfer3(nn.Module):
    def __init__(self):
        super(Transfer3, self).__init__()
        self.name = "Kooresh_Transfer3_contd95"
        self.conv1 = nn.Conv2d(256, 70, 2)
        self.fc1 = nn.Linear(70 * 5 * 5, 200)
        self.fc2 = nn.Linear(200, len(classes))
  
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = x.view(-1, 70 * 5 * 5)
        x = torch.tanh(self.fc1(x))
        x = self.fc2(x)
        return x

def classify_image(img_path):

    """
    Classifies an image given an image path.

    Parameters: 
        img_path: A string representing the image file path
    
    Returns:
        A string representing the label 
    """
    transform = transforms.Compose([transforms.Resize((224,224)), 
                      transforms.ToTensor(), 
                      transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])
    test_img = transform(Image.open(img_path))
    test_img.unsqueeze_(0)
    input = Variable(test_img)
    model = Transfer3()
    model_path = '/home/Kooresh/APS360-Project/model_Defne_Transfer7_contd110_bs256_lr8e-05_epoch19'
    model_state = torch.load(model_path)
    model.load_state_dict(model_state)
    alexnet = torchvision.models.alexnet(pretrained=True)
    label = model(alexnet.features(input))
    
    return classes[label.data.numpy().argmax()]

@app.route('/run_api', methods = ['GET', 'POST'])
@flask_login.login_required
def call_api():
    ingredient_list=[]
    if request.method == 'POST':
        for i in range(int(request.form['len_img'])):
            ingredient_list.append(str(request.form[str(i)]))
        

    for i in range(3):
        cutoff = 3 - i

        if len(ingredient_list) > cutoff:
            ingredient_list = ingredient_list[:cutoff]

        ingredient_string = ''
        for ingredient in ingredient_list:
            ingredient_string += ingredient + ', '

        ingredient_string = ingredient_string[:-2]
        print('ingredientString is', ingredient_string)

        # Set up the parameters we want to pass to the API.
        # q: any ingredient in string form
        # app_id is the application ID of recipe search 
        # app_key is the application authentication key
        parameters = {"q": ingredient_string, "app_id": '85b9158f', "app_key": 'b6e60f224ffd3c0a1d048088ada1dc22', "excluded": request.form['excluded_ing']}
        # Make a get request with the parameters
        response = requests.get("https://api.edamam.com/search", params=parameters)

        # If status code is 200, the request is successful
        print('Status Code:', response.status_code)

        # Get the response data as a python object.
        data = response.json()

        if len(data['hits']) is 0:
            continue
        

        recipes = {"Name": [], "Links": []}
        for hit in data['hits']:
            try:
                print('Recipe:', hit['recipe']['label'])
                recipes["Name"].append(hit['recipe']['label'])
                print('Recipe Instructions Link:', hit['recipe']['url'])
                recipes["Links"].append(hit['recipe']['url'])
                print(' ')
            except:
                pass

        break
    print(recipes)
    return render_template("recipes.html", recipes=(recipes), length=enumerate(recipes["Name"]))


if __name__ == '__main__':
   app.run(debug = True)


