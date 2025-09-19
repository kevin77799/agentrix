# In backend/disease_agent/app.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import io
import torch
import torch.nn as nn
from torchvision import transforms

app = FastAPI()

# --- 1. Recreate the Model Architecture (from your notebook) ---
class CNN(nn.Module):
    def __init__(self, K):
        super(CNN, self).__init__()
        self.conv_layers = nn.Sequential(
            # conv1
            nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.MaxPool2d(2),
            # conv2
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(2),
            # conv3
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.Conv2d(in_channels=128, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(2),
            # conv4
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(256),
            nn.Conv2d(in_channels=256, out_channels=256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(256),
            nn.MaxPool2d(2),
        )

        self.dense_layers = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(50176, 1024),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(1024, K),
        )

    def forward(self, X):
        out = self.conv_layers(X)
        out = out.view(-1, 50176) # Flatten
        out = self.dense_layers(out) # Fully connected
        return out

# --- 2. Load the Model and Weights ---
try:
    # There are 39 classes in the model from your notebook
    model = CNN(39)
    # Load the weights you downloaded
    model.load_state_dict(torch.load('plant_disease_model_1_latest.pt', map_location=torch.device('cpu')))
    model.eval() # Set the model to evaluation mode
    print("PyTorch Model loaded successfully!")
except Exception as e:
    print(f"Error loading PyTorch model: {e}")
    model = None

# --- 3. Define Image Transforms and Class Names ---
# These transforms must match the ones used during training
image_transforms = transforms.Compose(
    [transforms.Resize(255), transforms.CenterCrop(224), transforms.ToTensor()]
)

# Based on the notebook, there are 39 classes. This is a reconstructed list.
class_names = [
    'Apple - Apple scab', 'Apple - Black rot', 'Apple - Cedar apple rust', 'Apple - healthy',
    'Blueberry - healthy', 'Cherry (including sour) - Powdery mildew', 'Cherry (including sour) - healthy',
    'Corn (maize) - Cercospora leaf spot Gray leaf spot', 'Corn (maize) - Common rust',
    'Corn (maize) - Northern Leaf Blight', 'Corn (maize) - healthy', 'Grape - Black rot',
    'Grape - Esca (Black Measles)', 'Grape - Leaf blight (Isariopsis Leaf Spot)', 'Grape - healthy',
    'Orange - Haunglongbing (Citrus greening)', 'Peach - Bacterial spot', 'Peach - healthy',
    'Pepper, bell - Bacterial spot', 'Pepper, bell - healthy', 'Potato - Early blight',
    'Potato - Late blight', 'Potato - healthy', 'Raspberry - healthy', 'Soybean - healthy',
    'Squash - Powdery mildew', 'Strawberry - Leaf scorch', 'Strawberry - healthy',
    'Tomato - Bacterial spot', 'Tomato - Early blight', 'Tomato - Late blight', 'Tomato - Leaf Mold',
    'Tomato - Septoria leaf spot', 'Tomato - Spider mites Two-spotted spider mite',
    'Tomato - Target Spot', 'Tomato - Tomato Yellow Leaf Curl Virus', 'Tomato - Tomato mosaic virus',
    'Tomato - healthy', 'Background Without Leaves'
]

# --- 4. Prediction Logic ---
def predict_disease(image: Image.Image):
    if model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    
    # Apply transformations and add a batch dimension
    input_tensor = image_transforms(image).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        
    # Get prediction
    _, predicted_idx = torch.max(output, 1)
    predicted_class_name = class_names[predicted_idx.item()]
    
    # Get confidence score
    probabilities = torch.nn.functional.softmax(output, dim=1)
    confidence = float(probabilities[0, predicted_idx.item()])
    
    return {"disease": predicted_class_name, "confidence": confidence}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')
    prediction = predict_disease(image)
    return prediction

@app.get("/")
def read_root():
    return {"message": "Disease Detection Agent is running with a PyTorch model."}