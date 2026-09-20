import cv2
import mediapipe as mp
import pyautogui
import time
import math
mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hands = mp_hands.Hands(False, 1, 1, 0.7, 0.5)
screen_w,screen_h=pyautogui.size()
print("\n hand mouse cantrol.")
prev_screen_x, prev_screen_y=0,0

cap=cv2.VideoCapture(0)

click_start_time=None
click_times=[]
click_cooldown=0.5
scroll_mode=False
freeze_cursor=False
screenshot_cooldown=2
last_screenshot_time=0
last_fist = False

if not cap.isOpened():
    print("Can not open camera")
    exit()
while True:8
    ret,frame=cap.read()
    if not ret:
        print("can't receive frame")
        break
    frame=cv2.flip(frame,1)
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    result=hands.process(rgb)
    fingers = []
    if result.multi_hand_landmarks:
        for hands_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame,hands_landmarks,mp_hands.HAND_CONNECTIONS)

            #get finger tip
        thumb_tip=hands_landmarks.landmark[4]
        index_tip=hands_landmarks.landmark[8]
        middle_tip=hands_landmarks.landmark[12]
        ring_tip=hands_landmarks.landmark[16]
        pinky_tip=hands_landmarks.landmark[20]

        fingers=[
            1 if hands_landmarks.landmark[tip].y<hands_landmarks.landmark[tip-2].y else 0
            for tip in [8,12,16,20]
        ]
            #distance btwn thumb and index
        thumb_tip = hands_landmarks.landmark[4]
        index_tip = hands_landmarks.landmark[8]

        dist = math.hypot(
            thumb_tip.x - index_tip.x,
            thumb_tip.y - index_tip.y
        )
        if dist<0.06:
            if not freeze_cursor:
                freeze_cursor=True
                click_times.append(time.time())

                #double click check
                if len(click_times)>=2 and click_times[-1]-click_times[-2]<0.4:
                    cv2.putText(frame,"Double Click",(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)
                    click_times=[]
                else:
                    pyautogui.click()
                    cv2.putText(frame,"Single click",(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2)
        else:
            if freeze_cursor:
                 time.sleep(0.1)
            freeze_cursor=False

        #move cursor by index finger
        if not freeze_cursor:
            screen_x=int(index_tip.x *screen_w)
            screen_y=int(index_tip.y *screen_h)
            pyautogui.moveTo(screen_x,screen_y,duration=0.05)
            prev_screen_x,prev_screen_y=screen_x,screen_y

         #scroll mode
        if sum(fingers)==4:
            scroll_mode=True
        else:
            scroll_mode=False

        #scroll sction
        if scroll_mode:
            if index_tip.y<0.4:
                pyautogui.scroll(60)
                cv2.putText(frame,"Scroll up",(10,90),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            elif index_tip.y>0.6:
                pyautogui.scroll(-60)
                cv2.putText(frame,"Scroll down",(10,90),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    # Screenshot gesture
    fist_detected = (
        result.multi_hand_landmarks
        and sum(fingers) == 0
    )

    if fist_detected and not last_fist:
        pyautogui.screenshot(
            f"screenshot_{int(time.time())}.png"
        )

        cv2.putText(
         frame,
            "Screenshot Taken!",
            (10, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        last_fist = bool(fist_detected)
            
        
    
    cv2.imshow("live video",frame)
    if cv2.waitKey(1)==ord('q'):
        break
cap.release()
cv2.destroyAllWindows()