import Image, StringIO, time
from v4lcam import Cam

def image2pixbuf(img):
    file1 = StringIO.StringIO()
    img.save(file1, "ppm")
    contents = file1.getvalue()
    file1.close()
    loader = GdkPixbuf.PixbufLoader()
    loader.write(contents)
    pixbuf = loader.get_pixbuf()
    loader.close()
    return pixbuf

class World:
    def __init__(self, queue_agent, queue_monitor=None):
        self.state = 0
        self.img_size = (640, 480)
        self.cam = Cam(*self.img_size)
        self.image = self.cam.read()

        self.queue_agent = queue_agent
        self.queue_monitor = queue_monitor

    def run(self):
        while 1:
            self.state += 1
            self.image = self.cam.read(as_string=True)
            monitor_data = {'size': self.img_size, 'image_string': self.image, 'id': 0}

            if self.queue_agent.empty():
                self.queue_agent.put(monitor_data)
            if self.queue_monitor != None:
                if self.queue_monitor.empty():
                    self.queue_monitor.put(monitor_data)
            time.sleep(0.01) # to prevent Queue getting full
