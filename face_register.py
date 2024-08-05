import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import face_recognition
import cv2
import numpy as np
import pickle
import mysql.connector

database_config = {
    'host': '',
    'port': 3306,
    'user': 'nandu',
    'password': 'Nk@1412',
    'database': 'FA',
}

mydb = mysql.connector.connect(**database_config)
cursor = mydb.cursor()

try:
    with open('./resources/pickle_data/encodings1.pkl', 'rb') as file:
        preloaded_encodings = pickle.load(file)
except (FileNotFoundError, EOFError):
    preloaded_encodings = {}

def save_face_encodings(user, face_encodings):
    if user in preloaded_encodings:
        preloaded_encodings[user] = np.concatenate((preloaded_encodings[user], face_encodings))
    else:
        preloaded_encodings[user] = face_encodings

def capture_and_encode_face(video_capture, user):
    face_encodings = []

    while True:
        ret, frame = video_capture.read()

        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) > 0:
            face_location = face_locations[0]
            face_encoding = face_recognition.face_encodings(frame, [face_location])

            if len(face_encoding) > 0:
                center_x, center_y = 320, 240
                radius = 140
                distance_to_center = np.sqrt((center_x - frame.shape[1] // 2) ** 2 + (center_y - frame.shape[0] // 2) ** 2)

                cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), 2)

                if distance_to_center <= radius:
                    face_encodings.append(face_encoding[0])

            if len(face_encodings) >= 7:
                break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)

        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        root.update()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    save_face_encodings(user, face_encodings)

def find(user):
    query = f"select * from daywise WHERE `snum` = %s"
    cursor.execute(query, (user,))
    result = cursor.fetchall()
    return result

def preload():

    user = entry_rollno.get().upper()
    if not find(user):
        name = entry_name.get().upper()
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, 640)
        video_capture.set(4, 480)

        capture_and_encode_face(video_capture, user)
        video_capture.release()

        with open('./resources/pickle_data/encodings1.pkl', 'wb') as file:
            pickle.dump(preloaded_encodings, file)

        print("Face registered successfully")
        query = f"INSERT INTO daywise(snum, sname) values(%s, %s)"
        cursor.execute(query, (user, name))
        mydb.commit()

        query = f"INSERT INTO periods(snum) values(%s)"
        cursor.execute(query, (user,))
        mydb.commit()

        query = f"INSERT INTO output(snum) values(%s)"
        cursor.execute(query, (user,))
        mydb.commit()

        # Ask the user to continue or exit
        answer = tk.messagebox.askquestion("Continue", "Do you want to continue?")
        if answer == 'yes':
            entry_rollno.delete(0, tk.END)
            entry_name.delete(0, tk.END)
            video_label.configure(image="")
        else:
            root.destroy()
    else:
        tk.messagebox.showinfo("User Exists", "User already exists!")

# Create the main Tkinter window
root = tk.Tk()
root.title("Face Recognition")

# Create labels and entry widgets
label_rollno = tk.Label(root, text="Roll No:")
entry_rollno = tk.Entry(root)

label_name = tk.Label(root, text="Full Name:")
entry_name = tk.Entry(root)

# Create a label for displaying video frames
video_label = tk.Label(root)

# Create a button to start the registration process
register_button = tk.Button(root, text="Register", command=preload)

# Layout management using grid
label_rollno.grid(row=0, column=0, pady=10)
entry_rollno.grid(row=0, column=1, pady=10)
label_name.grid(row=1, column=0, pady=10)
entry_name.grid(row=1, column=1, pady=10)
video_label.grid(row=2, column=0, columnspan=2, pady=10)
register_button.grid(row=3, column=0, columnspan=2, pady=10)

# Start the Tkinter main loop
root.mainloop()
