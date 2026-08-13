from django.shortcuts import render, redirect

from Detector.utility.classification import train_and_evaluate
from .models import Detector
from django.contrib import messages

def detector_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        loginId = request.POST.get('loginId')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        address = request.POST.get('address')

        # Optional: check if loginId or email already exists
        if Detector.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('detector_registerForm')  # Replace with your actual template/view name

        if Detector.objects.filter(loginId=loginId).exists():
            messages.error(request, "Login ID is already taken.")
            return redirect('detector_registerForm')

        detector = Detector(
            name=name,
            email=email,
            loginId=loginId,
            mobile=mobile,
            password=password,
            address=address,
            status='waiting'  # Default value, could be omitted since it's in model
        )
        detector.full_clean()
        detector.save()  
        messages.success(request, "Registration successful! Please wait for activation.")
        return render(request, 'detector_registerForm.html')  # Replace with your registration template name

    return render(request, 'detector_registerForm.html')  # Replace with your registration template name

def detector_login(request):
    if request.method == 'POST':
        loginId = request.POST.get('loginId')
        password = request.POST.get('password')

        try:
            # Check if user exists with matching loginId and password
            user = Detector.objects.get(loginId=loginId, password=password)

            if user.status != 'Active':
                messages.warning(request, "Your account is not active. Please wait for admin approval.")
                return render(request, 'detector_LoginForm.html')

            # Store user info in session
            request.session['id'] = user.id
            request.session['detector_name'] = user.name
            messages.success(request, f"Welcome, {user.name}!")
            return render(request,'detector/detectorHome.html')
        except Detector.DoesNotExist:
            messages.error(request, "Invalid Login ID or Password.")
            return render(request, 'detector_LoginForm.html')
        
    return render(request, 'detector_LoginForm.html')


from django.contrib import messages
from django.shortcuts import render

def DetectorHome(request):
    
    if not request.session.get('id'):
        return render(request, 'detector_LoginForm.html')
    return render(request, 'detector/detectorHome.html')



def training(request):
    if not request.session.get('id'):
        return render(request, 'detector_LoginForm.html')
    results=train_and_evaluate()
    return render(request,'detector/training.html',{'results':results})
     


def logout(request):
    request.session.flush()  # clears all session data
    return render(request,'detector_LoginForm.html')


import torch
import torch.nn.functional as F
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from django.shortcuts import render
from .utility.classification import GCN, GAT, GraphSAGE, GIN  # Ensure these models are imported
import pandas as pd

# Function to load the trained model
def load_trained_model(model_name):
    model = None
    if model_name == "GCN":
        model = GCN(in_channels=39, hidden_channels=32, out_channels=2)  # Adjust based on your data
    elif model_name == "GAT":
        model = GAT(in_channels=39, hidden_channels=32, out_channels=2)
    elif model_name == "GraphSAGE":
        model = GraphSAGE(in_channels=39, hidden_channels=32, out_channels=2)
    elif model_name == "GIN":
        model = GIN(in_channels=39, hidden_channels=32, out_channels=2)
    
    model.load_state_dict(torch.load(f"{model_name}_model.pth"))
    return model



from torch_geometric.data import Data
import torch
import numpy as np
from sklearn.preprocessing import StandardScaler


def prediction(request):
    if not request.session.get('id'):
        return render(request, 'detector_LoginForm.html')
    
    if request.method == 'POST':
        # Collect the input data (assuming 39 features)
        data_input = request.POST.get('data_input')
        print(data_input)
        # Split the string by commas into a list
        input_data = data_input.split(',')
        print(input_data)
        
        # Ensure the input data is not empty
        if not input_data or len(input_data) != 39:
            return render(request, 'detector/prediction.html', {'error': 'Please provide all 39 features.'})

        input_data = np.array([input_data], dtype=np.float32)
        print(input_data)
        # Preprocess the input data (Standardize)
        try:
            scaler = StandardScaler()
            input_data = scaler.fit_transform(input_data)  # Same preprocessing as the training data
        except ValueError as e:
            return render(request, 'detector/prediction.html', {'error': str(e)})

        # Load the model (e.g., GCN)
        model = load_trained_model("GCN")  # Change model based on user choice if needed

        # Convert the input data into a torch tensor
        input_tensor = torch.tensor(input_data, dtype=torch.float)

        # Create a dummy edge_index for a single node (since the input has no edges)
        edge_index = torch.tensor([[], []], dtype=torch.long)  # Empty graph; you may need a proper graph here

        # Create a Data object for GNN (even though there's no actual graph, this mimics the expected input format)
        data = Data(x=input_tensor, edge_index=edge_index)

        # Make the prediction
        model.eval()
        with torch.no_grad():
            output = model(data)
            prediction = output.argmax(dim=1).item()

        # Map the prediction to a label
        prediction_label = 'Normal' if prediction == 0 else 'Anomalous'

        return render(request, 'detector/prediction.html', {'prediction': prediction_label, 'features': range(1, 40)})
    
    return render(request, 'detector/prediction.html', {'features': range(1, 40)})
