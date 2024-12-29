import cv2
import json
from tkinter import Label
from PIL import Image, ImageTk
from api_call import gate_pass_data
from datetime import datetime
from api_call import post_entry
import threading

qr_code_detector = cv2.QRCodeDetector()
gate_open = 0

def call_api_data():
    api_data = gate_pass_data()
    return api_data


def start_qr_read(cam, label: Label):
    cap = cv2.VideoCapture(cam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Lower resolution
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def process_frame():
        global gate_open
        ret, frame = cap.read()
        if ret:
            data, bbox, _ = qr_code_detector.detectAndDecode(frame)
            
            if bbox is not None:
                for i in range(len(bbox)):
                    point1 = tuple(map(int, bbox[i][0]))
                    point2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
                    cv2.line(frame, point1, point2, (0, 255, 0), 2)
                
                if data:
                    cv2.putText(frame, f"QR Code: {data}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    try:
                        qr_data = json.loads(data)
                        gatepass_number = qr_data.get("gatepass_number")
                        api_data = call_api_data()
                        for pass_data in api_data:
                            if pass_data.get("gatepass_number") == gatepass_number and pass_data.get("master_admin_approval") == "pass":
                                print("User verified, opening gate...., Serial input: 1")
                                gate_open = 1
                                label.after(5000, close_gate)
                                
                                user = pass_data.get("user")
                                gatepass = pass_data.get("gatepass_number")    
                                
                                date = datetime.now().strftime('%Y-%m-%d')   
                                                         
                                time_in = datetime.now().strftime('%H:%M:%S')

                                data = {
                                    "user": user,
                                    "gatepass": gatepass,
                                    "time_in": time_in,  # Date format: YYYY-MM-DD  # Time format: HH:MM:SS
                                    "date": date ,      # Date format: YYYY-MM-DD
                                    "image_type":"QR Code",
                                    "matching_percentage": "0",   # Date format: YYYY-MM-DD
                                    "activities":"Gate IN ",
                                    "alert":"-",
                                    "action":"Open"
                                    }
                                
                                # post_entry(data)
                                post_thread = threading.Thread(target=post_entry, args=(data,))
                                
                                
                              
                                
                            else:
                                print("admin is not approved")
                                
                                date = datetime.now().strftime('%Y-%m-%d')   
                                                         
                                time_in = datetime.now().strftime('%H:%M:%S')

                                data = {
                                    "user": "",
                                    "gatepass": "",
                                    "time_in": time_in,  # Date format: YYYY-MM-DD  # Time format: HH:MM:SS
                                    "date": date ,      # Date format: YYYY-MM-DD
                                    "image_type":"QR Code",
                                    "matching_percentage": "0",   # Date format: YYYY-MM-DD
                                    "activities":"Rejected",
                                    "alert":"not approved ",
                                    "action":"Close"
                                    }
                                
                                post_thread = threading.Thread(target=post_entry, args=(data,))
                                
                                # post_entry(data)
                                
               
                                
                    except json.JSONDecodeError:
                        print("Invalid QR code data format.")
            
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)
        
        label.after(50, process_frame)  # Reduced frame update interval

    def close_gate():
        global gate_open
        gate_open = 0
        print("Gate closed. Serial input: 0")

    process_frame()
