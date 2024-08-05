import face_recognition
import cv2
import pickle

def verify_face(frame):
    with open('./resources/pickle_data/encodings1.pkl', 'rb') as file:
        preloaded_encodings = pickle.load(file)

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, num_jitters=1)

    if not face_encodings:
        return []

    users = []
    for current_face_encoding, current_face_location in zip(face_encodings, face_locations):
        user_similarities = {}
        for user, user_face_encodings in preloaded_encodings.items():
            similarities = face_recognition.face_distance(user_face_encodings, current_face_encoding)
            average_similarity = (1.0 - sum(similarities) / len(similarities)) * 100

            if average_similarity >= 50.0:
                user_similarities[user] = average_similarity

        users.append((current_face_location, user_similarities))

    return users


def run(image_path):
    frame = cv2.imread(image_path)

    if frame is None:
        print("Error: Unable to read the image.")
        return

    users_info = verify_face(frame)

    for face_location, user_info in users_info:
        for user, similarity in user_info.items():
            if user != "Unknown":
                print(f"Detected user: {user}, Similarity: {similarity:.2f}%")
                cv2.putText(frame, f"{user} - Similarity: {similarity:.2f}%", (face_location[3], face_location[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Face Recognition", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

run('testimg1.jpg')
