import torch
from torch import nn, optim
from torchvision import transforms
from PIL import Image
from PIL import Image, UnidentifiedImageError

# Define the same CNN model architecture (exactly as during training)
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(self._get_flattened_size(), 128)
        self.fc2 = nn.Linear(128, 10)  # 10 classes output
        
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)  # Flatten
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x
    
    def _get_flattened_size(self):
        with torch.no_grad():
            sample_input = torch.zeros(1, 3, 128, 128)  # Simulate an input batch
            sample_output = self.pool(self.relu(self.conv1(sample_input)))
            sample_output = self.pool(self.relu(self.conv2(sample_output)))
            return sample_output.view(1, -1).size(1)  # Flatten and get size

# Load the model
model = CNN()
model.load_state_dict(torch.load("cnn_model.pth"))
model.eval()  # Set the model to evaluation mode

# Define the transform for input images (same as used during training)
transform = transforms.Compose([
    transforms.Resize((128, 128)),  # Resize image to 128x128
    transforms.ToTensor(),          # Convert image to tensor
    transforms.Normalize((0.5,), (0.5,))  # Normalize to same scale as training data
])

# Function to make predictions

def predict(image_path):
    # Ignore hidden files like .DS_Store
    if image_path.endswith(".DS_Store"):
        print(f"Skipping non-image file: {image_path}")
        return None  # Or return a default value like -1
    
    try:
        # Load and transform the image
        image = Image.open(image_path).convert("RGB")
        image = transform(image)
        image = image.unsqueeze(0)  # Add batch dimension (1, 3, 128, 128)

        # Make prediction
        with torch.no_grad():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            return predicted.item()  # Return the predicted class label
    except UnidentifiedImageError:
        print(f"Skipping invalid image file: {image_path}")
        return None  # Or return a default value


# # Example usage:
# image_path = "path_to_your_image.jpg"  # Replace with the path to your image
# predicted_class = predict(image_path)
# print(f"Predicted class: {predicted_class}")
