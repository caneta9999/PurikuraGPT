import cv2
import threading
import time
import numpy as np
import imutils

class CameraDisplayThread(threading.Thread):
    def __init__(self, window_name, time_between_photos, photo_callback):
        super().__init__()
        self.window_name = window_name
        self.time_between_photos = time_between_photos
        self.countdown = time_between_photos
        self.camera = cv2.VideoCapture(0)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.color = (100, 100, 100, 128)  # Gray color with 50% opacity
        self.photo_callback = photo_callback
        self.is_running = True

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 600, 600)

        while self.is_running:
            _, frame = self.camera.read()
            cv2.imshow(self.window_name, frame)

            text = str(int(np.ceil(self.countdown)))
            (text_width, text_height) = cv2.getTextSize(text, self.font, 2, 2)[0]
            text_offset_x = int((frame.shape[1] - text_width) / 2)
            text_offset_y = int((frame.shape[0] + text_height) / 2)
            cv2.putText(frame, text, (text_offset_x, text_offset_y), self.font, 2, self.color, 2, cv2.LINE_AA)

            cv2.imshow(self.window_name, frame)

            time.sleep(0.1)

            self.countdown -= 0.1
            if self.countdown <= 0:
                self.countdown = self.time_between_photos
                self.photo_callback(self.camera)

            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()

    def release_camera(self):
        self.is_running = False
        self.camera.release()

def take_photos(time_between_photos):
    photos = []
    camera_thread = CameraDisplayThread("Purikura", time_between_photos, lambda camera: photos.append(camera.read()[1]))
    camera_thread.start()

    is_photos_taken = False

    while True:
        if len(photos) == 4 and not is_photos_taken:
            is_photos_taken = True
            camera_thread.release_camera()

        if is_photos_taken:
            grid = np.vstack([
                np.hstack([photos[0], photos[1]]),
                np.hstack([photos[2], photos[3]])
            ])

            grid_resized = imutils.resize(grid, width=1200, height=1200)
            cv2.imwrite("purikura_grid.jpg", grid_resized)

            cv2.imshow("Purikura", grid_resized)

            if cv2.waitKey(30 * 1000) == ord('q'):
                break

            break

        time.sleep(0.05)
        

    cv2.destroyAllWindows()

take_photos(10)

