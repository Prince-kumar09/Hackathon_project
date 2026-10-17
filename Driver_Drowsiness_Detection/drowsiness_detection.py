
import cv2
import time
import winsound

# Step 1: Load face and eye detection models
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)

# Check whether models loaded successfully
if face_cascade.empty() or eye_cascade.empty():
    print("Face/Eye detection model load nahi hua!")
    raise SystemExit

# Step 2: Open laptop camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera open nahi hua!")
    raise SystemExit

print("Camera started! Band karne ke liye q dabayein.")

eyes_missing_since = None
alarm_played = False

try:
    while True:
        # Step 3: Read camera frame
        success, frame = camera.read()

        if not success:
            print("Camera se video nahi mil raha!")
            break

        # Step 4: Convert frame to grayscale
        gray = cv2.cvtColor(
            frame, cv2.COLOR_BGR2GRAY
        )

        # Step 5: Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(80, 80)
        )

        eyes_detected = False

        for (x, y, w, h) in faces:
            # Draw green rectangle around face
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            # Search for eyes only in the upper face
            upper_gray = gray[
                y:y + h // 2,
                x:x + w
            ]

           
            eyes = eye_cascade.detectMultiScale(
            upper_gray,
                 scaleFactor=1.15,
                 minNeighbors=8,
                 minSize=(20, 15)
                )

            

            if len(eyes) > 0:
                eyes_detected = True

            # Draw blue rectangles around detected eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(
                    frame,
                    (x + ex, y + ey),
                    (x + ex + ew, y + ey + eh),
                    (255, 0, 0),
                    2
                )

        # Step 6: Basic eye-missing timer
        if len(faces) == 0:
            eyes_missing_since = None
            alarm_played = False
            status = "Face not detected"

        elif eyes_detected:
            eyes_missing_since = None
            alarm_played = False
            status = "Eyes detected"

        else:
            if eyes_missing_since is None:
                eyes_missing_since = time.time()

            elapsed = time.time() - eyes_missing_since

            if elapsed >= 2:
                status = "WARNING: Eyes not detected!"

                if not alarm_played:
                    winsound.Beep(1000, 700)
                    alarm_played = True
            else:
                status = "Checking eyes..."

        # Step 7: Display status on screen
        cv2.putText(
            frame,
            status,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255) if "WARNING" in status
            else (0, 255, 0),
            2
        )

        cv2.imshow("Driver Drowsiness Detection", frame)

        # Press q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # Step 8: Release camera and close windows
    camera.release()
    cv2.destroyAllWindows()
    print("Camera band ho gaya.")
