import os
from PIL import Image, ImageChops

directory = "./base_screenshots"  # Replace with your directory path
png_files = [f for f in os.listdir(directory) if f.endswith('.png')]

print("Images to compare: " + str(png_files))

for filename in png_files:
    base_image = Image.open("./base_screenshots/" + filename)
    test_image = Image.open(filename)
    diff = ImageChops.difference(base_image, test_image)
    if diff.getbbox():
        print("ERROR: " + filename + " are different")
    else:
        print(filename + " are identical")
