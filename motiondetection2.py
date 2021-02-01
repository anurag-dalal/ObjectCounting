# defining constants
#for row, column and channels
H, W, C = 480, 640, 3
# the midpoint of the row
M = int(H/2)
# how much near to the mid point the object has to be, to be counted as it has crossed the line
MID_THRES = int(M*0.98) 
# minimum eucledian distance between mid point of two box
DIST_FRAME_THRESH = 100
# used in opencv dilate
SMOOTHING_FACTOR = 7
# minimum are of the bound box so as to detec it as viable object
# it reduces the noise
THREDHOLD_AREA = (H*W)/50
# the name of the log file created
LOG_FILE_NAME = 'log.csv'
#imports the necessary modules
import cv2
import numpy as np
from csv import writer
import time

# this function is used to write to a csv which is used as a log file
# it contain the unix timestamp of the detected image crossing the line
# input is a filename and a list which elements are to be added at the 
# end of csv file
def appendListAsRow(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)
        

# this function checks if box is present  within any of the boxes
# that is if  the box is completely enclosed under another box present in boxes
def within(box, boxes):
    for box_i in boxes:
        if(box_i[0]<box[0] and box_i[1]<box[1] and box_i[2]>box[2] and box_i[3]>box[3]):
            return True
        
def getMid(box):
    return (int((box[0]+box[2])/2),int((box[1]+box[3])/2))

def distEuc(box1, box2):
    m1 = getMid(box1)
    m2 = getMid(box2)
    return ((m1[0]-m2[0])**2+(m1[1]-m2[1])**2)**0.5


# This function checks if the box is near to any of the box defined
# in boxes, and change the box in boxes if it is near the box
# or else the box is appended at the last, meaning it is consided as a new detection
def isNear(box, boxes):
    for i, box_i in enumerate(boxes):
        if(distEuc(box, box_i)<DIST_FRAME_THRESH):
            if(getMid(box)[1]<M):
                boxes[i] = box
            else:
                boxes.pop(i)
            return True, boxes
    if(getMid(box)[1]<100):
        boxes.append(box)
    return False, boxes

# this function checks if any of thedetected  box crossed the predifined line
# and also if the distance of detected boxes and previous boxes is less than
# predefined level

def crossed(boxesa, boxesb, frame):
    index = []
    
    for i,box_i in enumerate(boxesa):
        f = False
        for box_j in boxesb:
            if f:
                continue
            if(distEuc(box_i, box_j)<DIST_FRAME_THRESH and getMid(box_j)[1]>MID_THRES):
                print('found')
                t = int(time.time())
                msg = 'Object passed through gate'
                imgname = "logged/img"+str(t)+".jpg"
                cv2.imwrite(imgname, frame)
                row_contents = [t, msg]
                appendListAsRow(LOG_FILE_NAME, row_contents)
                #index.append(i)
                boxesa.pop(i)
                f = True
                continue
    return boxes
    
#loads the video - this can also be a from a network source or webcam
cap = cv2.VideoCapture(0)

#getting the height and width of the image
frame_width = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height =int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))

#This is optional to write the detected video with bound box in a file
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
#out = cv2.VideoWriter("output.avi", fourcc, 5.0, (1280,720))

#reads the first 2 frames from the input file
ret, frame1 = cap.read()

count = 0
#This runs a loop frame by frame until the frames are exhausted
boxes = []
while cap.isOpened():
    ret, frame2 = cap.read()
    #Process the image
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=SMOOTHING_FACTOR)
    #find contours where difference is observed
    contours, jkk = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #How many detected?
    detected = 0
    boxesb  =[]
    #for all the detected contours
    for contour in contours:
        #form a bounding rectangle
        box = (x, y, w, h) = cv2.boundingRect(contour)
        #Checks for a threshold to disble very small detections
        if cv2.contourArea(contour) < THREDHOLD_AREA:
            continue
        else:
            boxesb.append(box)
            if(len(boxes)>0):
                boxes = crossed(boxes, boxesb, frame1)
            if not within(box, boxes):
                ret, boxes = isNear(box, boxes)
                #Draws the rectangle onto the frame
            cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #increse the number of detected
            detected+=1
    #if detected>0 then show a status in frame of how many detected
    if(detected>0):
        fname = 'images/image'+str(count)+'.png'
        cv2.imwrite(fname,frame2)
        cv2.putText(frame1, "Status: {} {}".format('Detected',detected), (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 1)
        count+=1
    #cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2)
    
    #optional write to a file
    # image = cv2.resize(frame1, (1280,720))
    #out.write(image)
    #showing the frame in a cv2 window
    frame1 = cv2.line(frame1, (0, M), (W, M), (0, 255, 255), 2)
    cv2.imshow("feed", frame1)
    #update the frame1 and 2
    frame1 = frame2
    
    
    #esc key for stopping the process    
    if cv2.waitKey(40) == 27:
        break

cv2.destroyAllWindows()
cap.release()
#out.release()