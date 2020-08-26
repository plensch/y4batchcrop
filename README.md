# y4batchcrop
Crops all images in a directory  around an object using [yolov4](https://pypi.org/project/yolov4/) for object detection.
Margins are selectable.

Only crops around a horse with rider at the moment, as that is what i needed.

#### Install
Dependencies:
- yolov4
- tensorflow
- cv2 (opencv)
- numpy

The files `coco.names` and `yolov4.weights` from `yolov4` should be placed in the same directory as this script.

#### Usage
`python y4batchcrop.py` 
The script has its own small CLI.

Commands:
- `d` : toggles debug mode (only show detected objects and cropping borders)
- `[input directory] [margins (in pixels)] [output directory name]`
- `q` : quit

##### Make Options
- `make cli` -> `./echo3d_cli`
- `make gui` -> `./echo3d_gui`
