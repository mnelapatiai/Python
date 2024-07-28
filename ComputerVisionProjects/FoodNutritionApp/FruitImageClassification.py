import glob
import numpy as np
import matplotlib.pyplot as plt

def loadimage(single_folder_path, fruits):
    # Create a dictionary to store arrays and labels for each fruit
    data = {fruit: [] for fruit in fruits}
    labels = {fruit: [] for fruit in fruits}
    
    # Iterate over each fruit type
    for fruit in fruits:
        # Construct the search pattern for the current fruit
        strr = f"{single_folder_path}/{fruit.lower()}_*.png"
        # Load data for the current fruit
        for file in glob.glob(strr):
            # Read an image as array
            img = np.asarray(plt.imread(file))
            # Append to the corresponding fruit array
            data[fruit].append(img)
            # Append the label
            labels[fruit].append(fruit)
    
    return data, labels

# List of fruit types
fruits = ["Apple", "Banana", "Cherry", "Chickoo", "Grapes", "Kiwi", "Mango", "Orange", "Strawberry"]

# Specify the folder where images are stored
single_folder_path = "path_to_your_images_folder"

# Load the data from the specified folder
data, labels = loadimage(single_folder_path, fruits)

# Function to display images for a given fruit
def display_images(fruit_name, data, num_images=5):
    images = data[fruit_name]
    plt.figure(figsize=(10, 10))
    for i in range(min(num_images, len(images))):
        plt.subplot(1, num_images, i + 1)
        plt.imshow(images[i])
        plt.title(f"{fruit_name} {i + 1}")
        plt.axis('off')
    plt.show()

# Display images for each fruit
for fruit in fruits:
    display_images(fruit, data)

