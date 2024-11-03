import cv2
import mediapipe as mp
import random
import time
import tkinter as tk
from tkinter import messagebox

# Initialize MediaPipe hands model
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize game options and scores
options = ["rock", "paper", "scissors"]
user1_score = 0
user2_score = 0
computer_score = 0
rounds = 0
round_count = 0
game_mode = ""

# Function to classify gesture based on landmarks
def classify_gesture(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    if (index_tip.y < landmarks[6].y and middle_tip.y < landmarks[10].y and
        ring_tip.y < landmarks[14].y and pinky_tip.y < landmarks[18].y):
        return "paper"
    elif (index_tip.y < landmarks[6].y and middle_tip.y > landmarks[10].y and
          ring_tip.y > landmarks[14].y and pinky_tip.y > landmarks[18].y):
        return "scissors"
    else:
        return "rock"

# Countdown before capturing gesture
def display_countdown(frame, countdown_time):
    cv2.putText(frame, f"Get Ready! {countdown_time}", (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 3)
    cv2.imshow("Rock Paper Scissors", frame)
    cv2.waitKey(1000)

# Function to start the game
def start_game():
    global user1_score, user2_score, computer_score, round_count, game_mode, rounds
    
    user1_score = 0
    user2_score = 0
    computer_score = 0
    round_count = 0

    try:
        rounds = int(round_entry.get())
        if rounds <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number of rounds.")
        return

    game_mode = mode_var.get()
    
    # Initialize hands processing only here to prevent errors
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while round_count < rounds:
        user_gesture = None
        user2_gesture = None
        computer_gesture = random.choice(options) if game_mode == "User vs Computer" else None
        result_text = ""

        for i in range(5, 0, -1):
            ret, frame = cap.read()
            if not ret:
                break
            display_countdown(frame, i)
        
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        if game_mode == "User vs Computer":
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = hand_landmarks.landmark
                    user_gesture = classify_gesture(landmarks)
                    
            if user_gesture:
                if (user_gesture == "rock" and computer_gesture == "scissors") or \
                   (user_gesture == "paper" and computer_gesture == "rock") or \
                   (user_gesture == "scissors" and computer_gesture == "paper"):
                    user1_score += 1
                    result_text = "You Win!"
                elif user_gesture == computer_gesture:
                    result_text = "It's a Tie!"
                else:
                    computer_score += 1
                    result_text = "Computer Wins!"
                    
        elif game_mode == "User vs Human":
            for i in range(5, 0, -1):
                ret, frame = cap.read()
                if not ret:
                    break
                display_countdown(frame, i)
            
            ret, frame = cap.read()
            if not ret:
                break
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = hand_landmarks.landmark
                    if user_gesture is None:
                        user_gesture = classify_gesture(landmarks)
                    else:
                        user2_gesture = classify_gesture(landmarks)
            
            if user_gesture and user2_gesture:
                if (user_gesture == "rock" and user2_gesture == "scissors") or \
                   (user_gesture == "paper" and user2_gesture == "rock") or \
                   (user_gesture == "scissors" and user2_gesture == "paper"):
                    user1_score += 1
                    result_text = "User 1 Wins!"
                elif user_gesture == user2_gesture:
                    result_text = "It's a Tie!"
                else:
                    user2_score += 1
                    result_text = "User 2 Wins!"

        cv2.putText(frame, f"Round {round_count + 1}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        if user_gesture:
            cv2.putText(frame, f"User 1 gesture: {user_gesture}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if computer_gesture:
            cv2.putText(frame, f"Computer gesture: {computer_gesture}", (300, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if user2_gesture:
            cv2.putText(frame, f"User 2 gesture: {user2_gesture}", (300, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if result_text:
            cv2.putText(frame, result_text, (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        
        cv2.imshow("Rock Paper Scissors", frame)
        cv2.waitKey(3000)
        round_count += 1

    if user1_score > max(user2_score, computer_score):
        final_result = "User 1 is the Champion!"
    elif user2_score > max(user1_score, computer_score):
        final_result = "User 2 is the Champion!"
    else:
        final_result = "Computer is the Champion!" if game_mode == "User vs Computer" else "It's a Draw!"
    
    messagebox.showinfo("Game Over", f"Final Score:\nUser 1: {user1_score}\n" +
                                    (f"User 2: {user2_score}" if game_mode == "User vs Human" else f"Computer: {computer_score}") +
                                    f"\n{final_result}")
    cap.release()
    cv2.destroyAllWindows()
    hands.close()  # Only close hands after the game loop completes

# Setup Tkinter GUI
root = tk.Tk()
root.title("Rock Paper Scissors Game")
root.geometry("300x250")

mode_var = tk.StringVar(value="User vs Computer")
tk.Label(root, text="Select Game Mode:").pack(pady=5)
tk.Radiobutton(root, text="User vs Computer", variable=mode_var, value="User vs Computer").pack()
tk.Radiobutton(root, text="User vs Human", variable=mode_var, value="User vs Human").pack()

tk.Label(root, text="Enter Number of Rounds:").pack(pady=5)
round_entry = tk.Entry(root)
round_entry.pack(pady=5)

start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack(pady=20)

root.mainloop()
