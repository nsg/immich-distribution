import cv2
import os
import sys

image_folder = "screenshots"
video_name = f"{image_folder}/screenshots.avi"
video = None

images = os.listdir(image_folder)
images = [image for image in images if image.endswith(".png")]
images.sort(key=lambda x: int(x.split(".")[0]))

for image in images:
    print(image)

    frame = cv2.imread(os.path.join(image_folder, image))

    if not video:
        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, 0, 0.5, (width, height))

    cv2.putText(
        frame,
        image,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )

    video.write(frame)

video.release()
