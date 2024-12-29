from flask import Flask, Response
import threading
import cv2
import os
from tkinter import Tk, Label
from PIL import Image, ImageTk
from simple_facerec import SimpleFacerec
from api_call import gate_pass_data,post_face_detect_flag , post_real_t_match # Assuming gate_pass_data is imported from your API
from datetime import datetime
import requests
import cvzone
from cvzone.Utils import cornerRect

# Initialize gate pass data
gate_pass_data = gate_pass_data()

# Initialize face recognition
sfr = SimpleFacerec()
faces_directory = "C:/media/userprofiles/photos"

sfr.load_encoding_images(faces_directory)
known_images = set(os.listdir(faces_directory))

gate_open = 0  # Initial state of the gate (closed)


def check_for_new_images():
    """
    Check if new images are added to the faces directory and reload encodings if necessary.
    """
    global known_images
    current_images = set(os.listdir(faces_directory))
    if current_images != known_images:
        sfr.load_encoding_images(faces_directory)
        known_images = current_images
        print("New images detected and loaded for encoding.")


def check_gate_pass(user_id):
    """
    Check if the user ID is in gate_pass_data and if their master admin approval is "pass".
    """
    global gate_pass_data
    for gatepass in gate_pass_data:
        if str(gatepass['user']) == user_id and gatepass['master_admin_approval'] == 'pass':
            return True
    return False


def save_face_image(image, file_path="temp_face.jpg"):
    """
    Save the detected face as a temporary image file.
    """
    cv2.imwrite(file_path, image)
    return file_path


def post_entry(data, image=None):
    """
    Post data to the API with the option to include an image file.
    """
    url = "http://localhost:8000/api/api/class-entries/"  # Replace with your API endpoint

    files = {}
    if image:
        with open(image, 'rb') as img_file:
            files['detected_face'] = ('face.jpg', img_file, 'image/jpeg')
            try:
                response = requests.post(url, data=data, files=files)
                print(f"Response: {response.status_code}, {response.text}")
            except Exception as e:
                print(f"Error sending data to API: {e}")

    # Clean up the temporary file
    if image and os.path.exists(image):
        try:
            os.remove(image)
        except Exception as e:
            print(f"Error deleting file: {e}")


def handle_face_upload(face_image, user_id, face_percentage):
    """
    Handle API data preparation and file upload for a detected face.
    """
    date = datetime.now().strftime('%Y-%m-%d')
    time_in = datetime.now().strftime('%H:%M:%S')

    # Prepare data to send
    data = {
        "user": user_id,
        "gatepass": "-",
        "time_in": time_in,
        "date": date,
        "image_type": "face",
        "matching_percentage": face_percentage,
        "activities": "Gate IN",
        "alert": "-",
        "action": "Open",
        "dtected_face_file_id": user_id,
    }

    # Save face image temporarily
    temp_file_path = save_face_image(face_image)

    # Post data with file
    post_entry(data, image=temp_file_path)


# Flask application
app = Flask(__name__)

# Shared variable for the HTTP video feed
global_frame = None





def generate_video_feed():
    """
    Generate a video stream for the HTTP feed.
    """
    global global_frame
    while True:
        if global_frame is not None:
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', global_frame)
            if not ret:
                continue
            # Yield the frame as part of an HTTP response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """
    HTTP endpoint for the video feed.
    """
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')


def start_flask():
    """
    Start the Flask application on a separate thread.
    """
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


# --------------------


# Global flag to track face detection status
face_detected = False
last_detected_time = None
textflag = 0 

data = {"flag": textflag}

# Ensure the args parameter is a tuple
pf1 = threading.Thread(target=post_face_detect_flag, args=(data,))
pf1.start()


def start_face_detection(cam_link, label: Label):
    """
    Start face detection and display video feed with detected face information.
    """
    global global_frame, face_detected, last_detected_time
  
    cap = cv2.VideoCapture(cam_link)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def process_frame():
        global global_frame, face_detected, last_detected_time,textflag
        ret, frame = cap.read()
        if ret:
            check_for_new_images()

            # Convert to RGB (if it is not already in that format)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Get face locations, names, and confidences
            face_locations, face_names, confidences = sfr.detect_known_faces(frame_rgb)

            # If no face is detected, reset the detection flag
            if len(face_locations) == 0:
                face_detected = False
                
                textflag = 0
                
                
                
                data3 = {"flag": textflag}

                # Ensure the args parameter is a tuple
                pf3 = threading.Thread(target=post_face_detect_flag, args=(data3,))
                pf3.start()

            for face_loc, name, confidence in zip(face_locations, face_names, confidences):
                y1, x2, y2, x1 = face_loc
                
                cornerRect(frame, (x1, y1, x2 - x1, y2 - y1), l=30, t=3, colorR=(0, 255, 0), rt=0)
                
                
                if textflag == 0:
                    
                    text = "Matching :" + str(confidences)  
                    
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else :
                    
                    textmatched = "Detected : " + str(name)
                    cv2.putText(frame, textmatched, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                
                confidence_data = {
                    "real_t_match":confidence
                }
                
                cnf = threading.Thread(target=post_real_t_match, args=(confidence_data,))
                cnf.start()
                # Check if the face is detected with sufficient confidence and hasn't been detected recently
                if confidence > 60.00 and not face_detected:
                    # Mark the face as detected
                    face_detected = True
                    last_detected_time = datetime.now()
                    

                    # Draw rectangle around the face
                   
                    textflag = 1
                     
                    data2 = {"flag": textflag}

                    # Ensure the args parameter is a tuple
                    pf2 = threading.Thread(target=post_face_detect_flag, args=(data2,))
                    pf2.start()


                    print(f"Detected: {name} at {face_loc} with confidence: {confidence:.2f}")

                    string = name
                    user_id = string.split('_')[0]  # Extract ID from the name string
                    print("User ID:", user_id)

                    # Check if the user has an approved gate pass
                    if check_gate_pass(user_id):
                        gate_open = 1  # Open the gate
                        print("Gate status: Open")

                        # Crop the face region from the frame
                        face_image = frame[y1:y2, x1:x2]

                        # Start thread to handle face upload
                        upload_thread = threading.Thread(
                            target=handle_face_upload,
                            args=(face_image, user_id, confidence)
                        )
                        upload_thread.start()

                    else:
                        gate_open = 0  # Keep the gate closed
                        print("Gate status: Closed")

                        # Prepare data for unknown faces
                        date = datetime.now().strftime('%Y-%m-%d')   
                        time_in = datetime.now().strftime('%H:%M:%S')

                        data = {
                            "user": "",
                            "gatepass": "-",
                            "time_in": time_in,
                            "date": date,
                            "image_type": "face",
                            "matching_percentage": "0",
                            "activities": "Rejected",
                            "alert": "Unknown face",
                        }

                        # Post data without file
                        post_thread = threading.Thread(target=post_entry, args=(data,))
                        post_thread.start()

            # Update the global frame for HTTP streaming
            global_frame = frame.copy()

            # Convert frame to Tkinter-compatible image format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)

        # Reduced frame update interval
        label.after(50, process_frame)

    process_frame()
    

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()
