import cv2
import time
import winsound

# Face and eye detection models
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)

camera = cv2.VideoCapture(0)

eyes_missing_since = None
alarm_played = False

while True:
    success, frame = camera.read()

    if not success:
        print("Camera frame nahi mil raha!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray, 1.3, 5
    )

    eyes_detected = False

    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame, (x, y), (x + w, y + h),
            (0, 255, 0), 2
        )

        face_gray = gray[y:y + h, x:x + w]
        face_color = frame[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(
            face_gray, 1.1, 5
        )

        if len(eyes) >= 1:
            eyes_detected = True

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(
                face_color, (ex, ey),
                (ex + ew, ey + eh),
                (255, 0, 0), 2
            )

    if eyes_detected:
        eyes_missing_since = None
        alarm_played = False
        status = "Eyes Detected"

    else:
        if eyes_missing_since is None:
            eyes_missing_since = time.time()

        duration = time.time() - eyes_missing_since

        if duration >= 2:
            status = "WARNING: Possible Drowsiness!"

            if not alarm_played:
                winsound.Beep(1000, 700)
                alarm_played = True
        else:
            status = "Checking Eyes..."

    cv2.putText(
        frame, status, (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
        (0, 0, 255) if "WARNING" in status
        else (0, 255, 0), 2
    )

    cv2.imshow("Driver Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()