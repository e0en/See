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
    def __init__(self, image_list, queue_agent, queue_monitor=None):
        self.state = 0
        self.image_list = image_list
        image = Image.open(image_list[0]).convert('RGB')
        self.img_size = image.size
        self.image = image.tostring()

        self.queue_agent = queue_agent
        self.queue_monitor = queue_monitor

    def run(self):
        while 1:
            for i, image_path in enumerate(self.image_list):
                print image_path
                image = Image.open(image_path).convert('RGB')
                if image.size[0] > 600:
                    image = image.resize((600, int(1.0*image.size[1]/image.size[0]*600)), Image.ANTIALIAS)
                monitor_data = {'size': image.size, 'image_string': image.tostring(), 'id': i}

                if self.queue_agent.empty():
                    self.queue_agent.put(monitor_data)
                if self.queue_monitor != None:
                    if self.queue_monitor.empty():
                        self.queue_monitor.put(monitor_data)

                time.sleep(1) # give a "slideshow for agent
