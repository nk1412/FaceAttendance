import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import cv2
import face_recognition
import pickle
import time
import mysql.connector
from datetime import datetime, timedelta
import attendance
from testnew import realORfake
import torch

database_config = {
    'host': '',
    'port': 3306,
    'user': 'nandu',
    'password': 'Nk@1412',
    'database': 'FA',
}

mydb = mysql.connector.connect(**database_config)

cursor = mydb.cursor()

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.my_dict = {}
        self.vid = cv2.VideoCapture(0)
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="orange")
        self.canvas.pack()

        with open('encodings1.pkl', 'rb') as file:
            self.preloaded_encodings = pickle.load(file)

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.logged_in_users = set()
        self.last_login_time = {}
        self.last_logout_time = {}

        self.image_path = "logo.png"
        self.original_image = Image.open(self.image_path)
        self.resized_image = self.original_image.resize((100, 100), Image.LANCZOS)

        self.logo = ImageTk.PhotoImage(self.resized_image)

        self.logo_label = tk.Label(self.canvas, image=self.logo,bg="orange")
        self.logo_label.grid(padx=10,pady=10,row=0, column=0,sticky=tk.W)

        self.login_status_label = tk.Label(self.canvas, text="", font=("Helvetica", 16),bg="orange")
        self.login_status_label.grid(padx=10,pady=10,row=0, column=0,sticky=tk.E)
        message = "Automated Facial-Biometric Attendance"
        self.login_status_label.config(text=message)

        self.clock_label = tk.Label(self.canvas, font=('calibri', 40, 'bold'), background='orange', foreground='white')
        self.clock_label.grid(row=0, column=1, padx=30, pady=10, sticky=tk.S)
        self.date_label = tk.Label(self.canvas,  background='orange', font=("Helvetica", 12))
        self.date_label.grid(row=1, column=1, padx=30, pady=10, sticky=tk.N)

        self.video_frame = tk.Label(self.canvas)
        self.video_frame.grid(padx=10,pady=10,row=2, column=0)

        self.message_text = ScrolledText(self.canvas, height=10, width=30, wrap=tk.WORD)
        self.message_text.grid(padx=10,pady=10,row=2, column=1)
        self.check = 0
        self.run()

    def run(self):
        time_string = time.strftime('%H:%M:%S %p')
        self.clock_label.config(text=time_string)

        current_date = time.strftime("%Y-%m-%d %A")
        self.date_label.config(text=current_date)

        ret, frame = self.vid.read()
        value = datetime.now()
        
        if ret:
            frame = cv2.flip(frame, 1)
            if realORfake.start(frame):
                user, average_similarity = self.verify_face(frame)

                if user != "Unknown" and average_similarity >= 50.0 :
                    self.updatedb(user)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=image)
            self.video_frame.imgtk = photo
            self.video_frame.configure(image=photo)

        if value.minute == 59 and self.check == 0:
            print("hello")
            self.check = 1
            attendance.set()

        self.root.after(10, self.run)

    def updatedb(self,user):
        result = self.find(user,"login")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = datetime.now()
        #value = datetime.combine(datetime.today(), value)
        if result[0][0] is not None:
            ress = self.find(user,"logout")
            if ress[0][0] is None:
                resultx = datetime.strptime(result[0][0], '%H:%M:%S').time()
                resultx = datetime.combine(datetime.today(), resultx)
                print(value,resultx)
                time_diff = value - resultx

                if time_diff >= timedelta(minutes=1) and  (user not in self.last_logout_time or self.last_logout_time[user] is None):
                    self.update(user,"logout")
                    login_message = f"{timestamp} - {user} logged out.\n"
                    self.message(login_message)

                elif time_diff == timedelta(seconds=30):
                    login_message = f"{user} already logged in.\n"
                    self.message(login_message)
            else:
                pass
        else:
            self.update(user,"login")
            login_message = f"{timestamp} - {user} logged in.\n"
            self.message(login_message)
        
    def update(self,user,mode):        
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        query = f"UPDATE daywise SET `{mode}` = %s WHERE `snum` = %s"
        cursor.execute(query, (timestamp,user))
        mydb.commit()

    def find(self,user,mode):
        query = f"select {mode} from daywise WHERE `snum` = %s"
        cursor.execute(query, (user,))
        result = cursor.fetchall()
        return result

    def message(self,login_message):
        self.message_text.insert(tk.END, login_message)
        self.message_text.see(tk.END)

    def on_quit(self):
        cursor.close()
        mydb.close()
        self.vid.release()
        self.root.destroy()

    def verify_face(self, frame):

        frame_gpu = torch.tensor(frame).to(self.device)
        frame_numpy = frame_gpu.numpy()

        face_locations = face_recognition.face_locations(frame_numpy)
        face_encoding = face_recognition.face_encodings(frame_numpy, num_jitters=1)
        face_encodings = torch.tensor(face_encoding).to(self.device)

        if not face_locations:
            return "Unknown", 0.0

        locations_tensor = torch.tensor(face_locations).to(self.device)

        best_user = None
        highest_similarity = 0.0
        for user, user_encodings in self.preloaded_encodings.items():

            user_encodings_gpu = torch.tensor(user_encodings).to(self.device)

            similarities = torch.cdist(user_encodings_gpu, face_encodings)
            average_similarity = torch.mean((1 - similarities) * 100)

            if average_similarity > highest_similarity:
                highest_similarity = average_similarity
                best_user = user

        if best_user:
            best_user = best_user
            highest_similarity = highest_similarity.cpu().item()

        return best_user, highest_similarity

def main():
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
