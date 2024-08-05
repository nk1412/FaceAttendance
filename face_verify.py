import face_recognition
import cv2
import pickle

def verify_face(frame):

    with open('./resources/pickle_data/encodings1.pkl', 'rb') as file:
        preloaded_encodings = pickle.load(file)

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame,num_jitters=1)

    if not face_encodings:
        return "Unknown", 0.0

    best_user = None
    highest_similarity = 0.0
    for current_face_encoding, current_face_location in zip(face_encodings, face_locations):
        for user, user_face_encodings in preloaded_encodings.items():
            similarities = face_recognition.face_distance(user_face_encodings, current_face_encoding)
            average_similarity = (1.0 - sum(similarities) / len(similarities)) * 100

            if average_similarity > highest_similarity:
                highest_similarity = average_similarity
                best_user = user

    return best_user, highest_similarity
    

def run():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, 640)
    video_capture.set(4, 480)
    video_capture.set(cv2.CAP_PROP_FPS, 60)

    while True:
        ret,frame = video_capture.read()
        frame = cv2.flip(frame, 1)
        user, average_similarity = verify_face(frame)

        if user != "Unknown" and average_similarity >= 50.0:
            print(f"Welcome, {user}! Similarity: {average_similarity:.2f}%")
            return user
        else:
            cv2.putText(frame, f"Unknown user. Similarity: {average_similarity:.2f}%", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

run()


