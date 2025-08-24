import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time

# ==============================
# Button Class
# ==============================
class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        x, y = self.pos
        cv2.rectangle(img, (x, y), (x + self.width, y + self.height),
                      (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + self.width, y + self.height),
                      (255, 255, 255), 2)
        cv2.putText(img, self.value, (x + 35, y + 60),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    def checkClick(self, x, y):
        bx, by = self.pos
        # Check inside the button
        if bx < x < bx + self.width and by < y < by + self.height:
            # Only count if finger is inside the "center zone"
            margin = 20
            if (bx + margin < x < bx + self.width - margin and
                    by + margin < y < by + self.height - margin):
                return True
        return False


# ==============================
# Setup
# ==============================
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

# Bigger buttons (120x120 instead of 100x100)
buttonListValues = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', '.', '=', '+']
]

buttonList = []
for i in range(4):
    for j in range(4):
        xpos = 100 * j + 600
        ypos = 100 * i + 150
        buttonList.append(Button((xpos, ypos), 100, 100, buttonListValues[i][j]))

myEquation = ''
delayCounter = 0
lastButton = None
stableCounter = 0  # debounce counter


# ==============================
# Main Loop
# ==============================
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    # Draw buttons
    for button in buttonList:
        button.draw(img)

    # If hand is detected
    if hands:
        lmList = hands[0]['lmList']
        x, y, _ = lmList[8]  # index finger tip

        for button in buttonList:
            if button.checkClick(x, y):
                if lastButton == button.value:
                    stableCounter += 1
                else:
                    stableCounter = 0
                    lastButton = button.value

                # Register click only if finger is stable for 5 frames
                if stableCounter == 5:
                    if button.value == '=':
                        try:
                            myEquation = str(eval(myEquation))
                        except:
                            myEquation = "Error"
                    else:
                        myEquation += button.value
                    stableCounter = 0

    # Display the equation/result
    cv2.rectangle(img, (600, 70), (1000, 150), (50, 50, 50), cv2.FILLED)
    cv2.putText(img, myEquation, (610, 130),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    cv2.imshow("CalcWave", img)
    key = cv2.waitKey(1)
    if key == ord('c'):
        myEquation = ''  # clear equation
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

