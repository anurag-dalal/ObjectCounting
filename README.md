# ObjectCounting
This is an unique approach in which, without using any tracker or caffe model
moving objects are detected and, a log is created when the moving object 
cross a certain line(prespecified)

The camera used in the demo is **Logitech HD WebCam C525**
According to the camera specification the constants are defined

## Install Dependecies
```unix
$pip install numpy
$pip install opencv-python
```

## defining the constants
```python
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
```


## Helper function 1: appendListAsRow
```python
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
```

## Helper function 2: within
```python
# this function checks if box is present  within any of the boxes
# that is if  the box is completely enclosed under another box present in boxes
def within(box, boxes):
    for box_i in boxes:
        if(box_i[0]<box[0] and box_i[1]<box[1] and box_i[2]>box[2] and box_i[3]>box[3]):
            return True
```

## Helper function 3: isNear
```python
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
```

## Helper function 3: crossed
```python
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
```

