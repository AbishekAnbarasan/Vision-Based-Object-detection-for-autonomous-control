from darkflow.net.build import TFNet
import pyrealsense2 as rs
import cv2
import numpy as np
import sys
from Project import*

# Create a pipeline
pipeline = rs.pipeline()

#Specify options
options = {"model": "cfg/tiny-yolo-voc-3c.cfg", "load": 3000, "threshold": 0.4}

tfnet = TFNet(options)


#Instantiate networf
tf=TFNet(options)

#Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)


def feed_result(self):
    temp=100
    try:
        frames = pipeline.wait_for_frames(temp)
        while True:
            try:
            # Wait for a coherent pair of frames: depth and color
                frames = pipeline.wait_for_frames(temp)
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                imgcv = cv2.imread(color_image)
                result = tfnet.return_predict(imgcv
                for i in range(len(result)):
                    x=result[i]['topleft'][0]
                    y=result[i]['topleft'][1]
                    w=result[i]['bottomright'][0]
                    h=result[i]['bottomright'][1]
                    label=result[i]['label']

                    if label == "person":
                        file = '/home/crl5/race_ws/way_point_new_person.txt'
                    elif label == "stopsign":
                        file = '/home/crl5/race_ws/way_point_new_stopsign.txt'
                    elif label == "trafficcone":
                        file = '/home/crl5/race_ws/way_point_new_trafficcone.txt'

                    main(x,y,w,h,file)


            except KeyboardInterrupt:
                print("Interrupted")
                sys.exit()

    except RuntimeError:
        print("uh ho, not working")
        temp+=50
        print("increasing feed")



            # Convert images to numpy arrays
