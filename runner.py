# Runs the facial recognition program
import os
os.system('python build_face_dataset.py --cascade haarcascade_frontalface_default.xml --output dataset/adrian')