from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
import joblib
import os

model = joblib.load(os.path.join(os.path.dirname(__file__), 'svm_rbf_model_svc.joblib'))

def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save user to the database
            return redirect('/login')  # Redirect to login page after signup
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # If credentials are correct, log the user in and redirect to the profile page
            login(request, user)
            return redirect('profile')  # Replace 'profile' with your profile page's URL name
        else:
            # If credentials are incorrect, return an error message
            return render(request, 'login.html', {'error': 'Incorrect username or password'})
    
    # For GET request, just display the login page
    return render(request, 'login.html')

def profile(request):
    img_url = None
    result1 = None
    result2 = None
    
    if(request.method=="POST"):
        if(request.FILES.get('uploadImage')):
            img_name = request.FILES['uploadImage']
            # create a variable for our FileSystem package
            fs = FileSystemStorage()
            filename = fs.save(img_name.name,img_name)
            #urls
            img_url = fs.url(filename)
            #find the path of the image
            img_path = fs.path(filename)
 
            #start implementing the opencv condition
            img = cv2.imread(img_path,cv2.IMREAD_COLOR)
            # Convert to grayscale (single channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #resize the image for a constant use
            img = cv2.resize(img,(64,64))
            #flatten the image for the better clear shape of the disease spread on the skin
            img = img.flatten()
            #using the normalization predefined function to find the value
            img = np.expand_dims(img,axis=0)
 
            #we sill start executing with our model
            predict = model.predict(img)[0]
            
            ''''''
            skin_disease_names = ['Cellulitis','Impetigo','Athlete Foot','Nail Fungus','Ringworm','Cutaneous Larva Migrans','Chickenpox','Shingles']
            # diagnosis = ['']
 
            result1 = skin_disease_names[predict]
            # result2 = diagnosis[predict]
 
    return render(request,'profile.html',{'img':img_url,'obj1':result1,'obj2':result2})