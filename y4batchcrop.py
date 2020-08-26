# disable tensorflow log to console
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
print("loading YOLOv4...")

### IMPORT LIBRARIES ###
import sys
import glob
import traceback
import readline

try:
    import numpy as np
except ImportError:
    print("numpy is not installed -> 'pip install numpy'")
    sys.exit(1)
try:
    import cv2
except ImportError:
    print("CV2 is not installed -> (debian) 'apt install python3-opencv'")
    sys.exit(1)
try:
    from yolov4.tf import YOLOv4
except ImportError:
    print("yolov4 is not installed -> 'pip install yolov4'")
    sys.exit(1)

### GLOBAL VARIABLES ###
debug = False

namefile = "coco.names"
namefile_url = "https://pypi.org/project/yolov4/"
weightsfile = "yolov4.weights"
weightsfile_url = "https://pypi.org/project/yolov4/"

usage_txt = "Usage: "

### YOLOV4 SETUP ###
yolo = YOLOv4()
try:
    yolo.classes = namefile
except FileNotFoundError as e:
    print("{} not found -> download from {}".format(namefile, namefile_url))
    sys.exit(1)

yolo.make_model()

try:
    yolo.load_weights(weightsfile, weights_type="yolo")
except FileNotFoundError as e:
    print("{} not found -> download from {}".format(weightsfile, weightsfile_url))
    sys.exit(1)

# TODO enable full path completion
readline.parse_and_bind('tab: complete')

def crop(path, space, outpath):
    frame = cv2.imread(path)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    bboxes = yolo.predict(frame)
    
    objs = bboxes.tolist()
    if not objs:
        print("no objects from {} found: {}".format(namefile, os.path.basename(path)))
        return
    
    horse = []
    rider = [] 
    cropbox = [] # center_x, center_y, width, height

    # select horse with biggest screen area
    for h in objs:
        if h[4] == 17.0:
            if horse:
                hw =  horse[2]
                hh =  horse[3]
                if (hw * hh) < (h[2] * h[3]):
                    horse = h
            else:
                horse = h

    # are there any horses?
    if not horse:
        print("no horse found: {}".format(os.path.basename(path)))
        return

    # select rider with bbox intersecting horse bbox
    for r in objs:
        if r[4] == 0.0:
            rcx = r[0]
            rcy = r[1]
            rw =  r[2]
            rh =  r[3]

            hcx = horse[0]
            hcy = horse[1]
            hw =  horse[2]
            hh =  horse[3]

            if  ((rcx > (hcx - (hw/2))) and (rcx < (hcx + (hw/2)))) and (((rcy + (rh/2)) > (hcy - (hh/2)))):
                if rider:
                    if (rider[2] * rider[3]) < (rw * rh):
                        rider = r
                        #calc cropbox
                        cropbox = [hcx, (rcy + hcy) / 2, hw if hw > rw else rw, abs((hcy + (hh/2)) - (rcy - (rh/2))), 46.0, 1.0]
                else:
                    rider = r

                    #calc cropbox
                    cropbox = [hcx, (rcy + hcy) / 2, hw if hw > rw else rw, abs((hcy + (hh/2)) - (rcy - (rh/2))), 46.0, 1.0]

    if rider:
        if debug:
            print("H", horse)
            print("R", rider)
            print("CROP", cropbox)

        height, width, _ = frame.shape

        c = cropbox
        x1 = int((c[0] - (c[2]/2)) * width) - space
        x2 = int((c[0] + (c[2]/2)) * width) + space
        y1 = int((c[1] - (c[3]/2)) * height) - space
        y2 = int((c[1] + (c[3]/2)) * height) + space
        if x1 < 0: x1 = 0
        if x2 > width: x2 = width
        if y1 < 0: y1 = 0
        if y2 > height: y2 = height

        
        # set right colors
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if debug:
            ncropbox = np.array([cropbox])
            dbg_boxes = np.concatenate((bboxes, ncropbox))
            frame = yolo.draw_bboxes(frame, dbg_boxes)
        else:
            frame = frame[y1:y2, x1:x2]
        
        cv2.imwrite(outpath, frame)
    else:
        print("no horse with rider found: {}".format(os.path.basename(path)))
        return

while True:
    # exit via crtl+c and provide traceback on errors
    try:
        inp = input(">")
        if inp:
            if inp == "q":
                break
            if inp == "d":
                debug = not debug
                print("debug:",debug)
                continue
            try:
                il = inp.split(" ")
                path  = os.path.normpath(il[0])
                space = int(il[1])
                filenames = il[2]
            except:
                print("filepath (file or folder) space (px) filenames / q / d")
                continue
            if os.path.isdir(path):
                count = 1
                files = glob.glob(path + "/*.jpg")
                files.sort()
                filecount = len(files)
                os.makedirs(path + "/" + filenames, exist_ok=True)
                for img in files:
                    outpath = "{}/{}/{}".format(path, filenames, os.path.basename(img))
                    print("{}/{} {} -> {}".format(count, filecount, os.path.basename(img), outpath), end="\r")
                    count = count + 1

                    # allow aborting while cropping
                    try:
                        crop(img, space, outpath)
                    except KeyboardInterrupt:
                        print("\ncancelled")
                        break
                print()
            else:
                print("'{}' is not a directory".format(path))
    except KeyboardInterrupt:
        break
    except:
        print("ERROR")
        traceback.print_exc()
