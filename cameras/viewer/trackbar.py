import cv2

from atlasbuggy.cameras.viewer import CameraViewer
from atlasbuggy.subscriptions import Update


class CameraViewerWithTrackbar(CameraViewer):
    def __init__(self, enabled=True, log_level=None, name=None):
        super(CameraViewerWithTrackbar, self).__init__(enabled, log_level, name)

        self.slider_name = "frame:"
        self.slider_ticks = 0
        self.num_frames = 0

        self.paused = False
        self.frame = None

        self.capture_tag = "capture"
        self.require_subscription(self.capture_tag, Update)

        self.capture = None
        self.capture_feed = None

    def take(self, subscriptions):
        self.take_capture(subscriptions)

    def take_capture(self, subscriptions):
        self.capture = subscriptions[self.capture_tag].stream
        self.capture_feed = subscriptions[self.capture_tag].queue

        self.num_frames = self.capture.num_frames
        self.slider_ticks = int(self.capture.capture.get(cv2.CAP_PROP_FRAME_WIDTH) // 3)

        if self.slider_ticks > self.num_frames:
            self.slider_ticks = self.num_frames

        cv2.createTrackbar(self.slider_name, self.name, 0, self.slider_ticks, self._on_slider)

        self.delay = 1 / self.capture.fps

    def _on_slider(self, slider_index):
        slider_frame_num = int(slider_index * self.num_frames / self.slider_ticks)
        if abs(slider_frame_num - self.current_frame_num()) > 5:
            self.set_frame(slider_frame_num)

            self.on_slider(slider_index)

    def on_slider(self, slider_index):
        pass

    def set_frame(self, frame_num):
        self.capture.set_frame(frame_num)

    def get_frame(self):
        self.update_slider_pos()
        if self.capture_feed.empty():
            return None
        else:
            return self.capture_feed.get()

    def current_frame_num(self):
        return self.capture.current_pos()

    def update_slider_pos(self):
        slider_pos = int(self.current_frame_num() * self.slider_ticks / self.num_frames)
        cv2.setTrackbarPos(self.slider_name, self.name, slider_pos)

    def show_frame(self):
        """
        Display the frame in the Capture's window using cv2.imshow
        :param frame: A numpy array containing the image to be displayed
                (shape = (height, width, 3))
        :return: None
        """
        self.key_pressed()

        if self.paused:
            frame = self.frame
        else:
            frame = self.get_frame()
            self.frame = frame

        if frame is None:
            return

        cv2.imshow(self.name, frame)

    def key_callback(self, key):
        if key == 'q':
            self.exit()
        elif key == ' ':
            self.paused = not self.paused
            self.capture.paused = self.paused
