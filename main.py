import cv2
import sys
from djitellopy import Tello

TOLERANCE_X = 5
TOLERANCE_Y = 5
TOLERANCE_Z = 5
SLOWDOWN_THRESHOLD_X = 10
SLOWDOWN_THRESHOLD_Y = 30
SLOWDOWN_THRESHOLD_Z = 35
DRONE_SPEED_X = 15
DRONE_SPEED_Y = 22
DRONE_SPEED_Z = 30
SET_POINT_X = 960/3
SET_POINT_Y = 720/3


cascPath = "faceModel.xml"  # Path of the model used to reveal faces
faceCascade = cv2.CascadeClassifier(cascPath)
drone = Tello()  # declaring drone object
drone.connect()
drone.takeoff()


drone.streamon()  # start camera streaming


# video_capture = cv2.VideoCapture("udp://0.0.0.0:11111")  # raw video from drone streaming address
# video_capture = cv2.VideoCapture("rtsp://192.168.1.1")  #raw video from action cam Apeman
# video_capture = cv2.VideoCapture(0)  # raw video from webcam

while True:
    # loop through frames
    # ret, frame = video_capture.read()  # used to collect frame from alternative video streams

    frame = drone.get_frame_read().frame  # capturing frame from drone
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # turning image into gray scale

    faces = faceCascade.detectMultiScale(  # face detection
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    i = 0
    # Decorating image for debug purposes and looping through every detected face
    for (x, y, w, h) in faces:
        color = (255, 0, 0)
        if i != 0:
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 5)  # contour rectangle
        cv2.circle(frame, (int(x+w/2), int(y+h/2)), 12, (255, 0, 0), 1)  # face-centered circle
        # print(frame.shape)
        # cv2.line(frame, (int(x+w/2), int(720/2)), (int(960/2), int(720/2)), (0, 255, 255))

        cv2.circle(frame, (int(SET_POINT_X), int(SET_POINT_Y)), 12, (255, 255, 0), 8)  # setpoint circle
        i = i+1
        distanceX = x+w/2 - SET_POINT_X
        distanceY = y+h/2 - SET_POINT_Y
        
        area = (w * h)
        print(area)


        up_down_velocity = 0
        right_left_velocity = 0
        for_back_velocity = 0

        if area <= 7000:
            for_back_velocity = DRONE_SPEED_Z
            print("forward")
        elif area >= 7250:
            for_back_velocity = - DRONE_SPEED_Z
            print("backwards")
        else:
            for_back_velocity = 0
            print("still")
            
        if distanceX < -TOLERANCE_X:
            right_left_velocity = - DRONE_SPEED_X

        elif distanceX > TOLERANCE_X:
            right_left_velocity = DRONE_SPEED_X
        else:
            print("OK")

        if distanceY < -TOLERANCE_Y:
            up_down_velocity = DRONE_SPEED_Y
        elif distanceY > TOLERANCE_Y:
            up_down_velocity = - DRONE_SPEED_Y

        else:
            print("OK")

        if abs(distanceX) < SLOWDOWN_THRESHOLD_X:
            right_left_velocity = int(right_left_velocity / 2)
        if abs(distanceY) < SLOWDOWN_THRESHOLD_Y:
            up_down_velocity = int(up_down_velocity / 2)

        drone.send_rc_control(right_left_velocity, for_back_velocity, up_down_velocity, 0)

    cv2.imshow('Video', frame)  # mostra il frame sul display del pc

    if cv2.waitKey(1) & 0xFF == ord('q'):  # quit from script
        break

# rilascio risorse
# video_capture.release()
cv2.destroyAllWindows()
