import cv2
import mediapipe as mp

# Initialize MediaPipe hands model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def classify_gesture(landmarks):
    # Using landmarks to classify gestures:
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Determine gesture based on finger positions
    if (index_tip.y < landmarks[6].y and middle_tip.y < landmarks[10].y and
        ring_tip.y < landmarks[14].y and pinky_tip.y < landmarks[18].y):
        return "paper"  # All fingers open
    elif (index_tip.y < landmarks[6].y and middle_tip.y > landmarks[10].y and
          ring_tip.y > landmarks[14].y and pinky_tip.y > landmarks[18].y):
        return "scissors"  # Only index and middle fingers open
    else:
        return "rock"  # All fingers closed

# Start capturing video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert frame color to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Classify gesture based on landmarks
            landmarks = hand_landmarks.landmark
            gesture = classify_gesture(landmarks)
            
            # Display the gesture
            cv2.putText(frame, f"Gesture: {gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show the video with gesture label
    cv2.imshow("Rock Paper Scissors Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
hands.close()

