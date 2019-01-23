# USAGE
# python build_face_dataset.py --cascade haarcascade_frontalface_default.xml --output dataset/adrian

# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os
# additional imports
import asyncio

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
	help = "path to where the face cascade resides")
ap.add_argument("-o", "--output", required=True,
	help="path to output directory")
args = vars(ap.parse_args())

# load OpenCV's Haar cascade for face detection from disk
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream, allow the camera sensor to warm up,
# and initialize the total number of example faces written to disk
# thus far
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
total = 0

# Function that sets bool to false for 1.0/DUR seconds
async def false_for_dur(boolArr, DUR):
	boolArr[0] = False
	await asyncio.sleep(DUR)
	boolArr[0] = True

FREQUENCY = 1 # how many pictures we can take a second
boolArr = [True]
(x,y,w,h)=(0,0,0,0)

# Function that writes picture to new file
def write_square_bmp(BMP, x, y, w, h, i):
	#p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5)+"_"+str(i).zfill(2)+"a")])
	#cv2.imwrite(p, BMP[y:y+h,x:x+w])
	#p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5)+"_"+str(i).zfill(2)+"b")])
	p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5)+"_"+str(i).zfill(2))])
	cv2.imwrite(p, BMP[int(1.6*y):int(1.6*(y+h)),int(1.6*x):int(1.6*(x+w))])
	#print("pic {} with (x,y,w,h)=({},{},{},{})".format(str(total).zfill(5)+"_"+str(i).zfill(2),x,y,w,h))

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream, clone it, (just
	# in case we want to write it to disk), and then resize the frame
	# so we can apply face detection faster
	frame = vs.read()
	orig = frame.copy()
	#(L1,L2) = (len(orig),len(orig[0]))
	#orig2 = frame.copy()[0:L1//2,0:L2//2]
	frame = imutils.resize(frame, width=400)

	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(
		cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30))

	# loop over the face detections and draw them on the frame
	for (x, y, w, h) in rects:
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

	# if there is a face, take a picture
	try:
		bogus = rects[0]
		# at this point, a face was detected
		if boolArr[0]:
			asyncio.run(false_for_dur(boolArr, 1/FREQUENCY))
			#p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5))])
			#cv2.imwrite(p, orig)
			for i in range(len(rects)):
				write_square_bmp(orig, x, y, w, h, i)
			total += 1
	except:
		#print("no face") # DEBUG
		pass # no faces detected so rects is empty

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("f"): # DEBUG
		print(boolArr)
		#print(orig)
		(L1,L2,L3) = (len(orig),len(orig[0]),len(orig[0][0]))
		print("dim of orig is {}x{}x{}".format(len(orig), len(orig[0]), len(orig[0][0])))
		#print("dim of orig2 is {}x{}x{}".format(len(orig2), len(orig2[0]), len(orig[0][0])))
		#print("STUFF:",len(orig[0:len(orig)//2]),len(orig))
		#print("orig[0] is",orig[0])
		#BADprint("attrs of orig: src is {}; usePiCamera is {}; resolution is {}; framerate is {}".format(orig.src, orig.usePiCamera, orig.resolution, orig.framerate))
		#print("orig from 0 to half length:", orig[0:len(orig)/2])
		#orig2 = orig2[0:L1//2,0:L2//2]
		#orig2 = (orig2[0:L1//2])
		#for i in range(0,len(orig2)):
		#	print(i,",",end="")
		#	orig2[i] = orig2[i][0:L2//2]
		#print("dim of orig2 is {}x{}x{}".format(len(orig2), len(orig2[0]), len(orig[0][0])))
		print("(x,y,w,h)=({},{},{},{})".format(x,y,w,h))
		print()

# BELOW FUNCTIONALITY CHANGED BUT KEPT FOR DEBUG; SEE ABOVE

	# if the `k` key was pressed, write the *original* frame to disk
	# so we can later process it and use it for face recognition
	if key == ord("k"):
		# p = os.path.sep.join([args["output"], "{}.png".format(
		# 	str(total).zfill(5))])
		# cv2.imwrite(p, orig)
		# #q = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5)+"a")])
		# #cv2.imwrite(q, orig2)
		# total += 1
		p = os.path.sep.join([args["output"], "{}.png".format(str(total).zfill(5))])
		cv2.imwrite(p, orig)
		for i in range(len(rects)):
			write_square_bmp(orig, x, y, w, h, i)
		total += 1

	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# do a bit of cleanup
print("[INFO] {} face images stored".format(total))
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()