import random
import Image, StringIO
from eye import Eye
import gnumpy as gnp

class Agent:
    def __init__(self, queue_world, queue_monitor=None):
        self.queue_world = queue_world
        self.queue_monitor = queue_monitor

    def _init_model(self):
        self.eye = Eye()
        self.A = gnp.zeros((5000,5000))

    def run_model(self, input_data):
        d_x = random.randint(-16, 16)
        d_y = random.randint(-16, 16)
        d_angle = random.randint(-15, 15)
        d_scale = 2**random.uniform(-0.5, 0.5)
        return (d_x, d_y, d_angle, d_scale)

    def move_eye(self, output_data):
        d_x, d_y, d_angle, d_scale = output_data
        self.eye_pos = (self.eye_pos[0] + d_x*self.eye_scale, self.eye_pos[1] + d_y*self.eye_scale)
        self.eye_scale *= d_scale
        self.eye_angle += d_angle

        self.eye_pos = \
                (min(max(self.eye_pos[0], 0), self.world_size[0]-1),
                        min(max(self.eye_pos[1], 0), self.world_size[1]-1))
        self.eye_scale = min(self.eye_scale, 1.0*min(self.world_size[0], self.world_size[1])/self.eye.mask_size)
        self.eye_scale = min(max(self.eye_scale, 0.5), 4)
        self.eye_angle = min(max(self.eye_angle, -90), 90)

    def run(self):
        self._init_model()

        while 1:
            if not self.queue_world.empty():
                world_data = self.queue_world.get()
                self.world_image, self.world_size = world_data['image_string'], world_data['size']
                self.world_id = world_data['id']
                break
        self.eye_pos = (self.world_size[0]/2, self.world_size[1]/2)
        self.eye_angle = 0.0
        self.eye_scale = 1.0

        while 1:
            if not self.queue_world.empty():
                world_data = self.queue_world.get()
                self.world_image, self.world_size = world_data['image_string'], world_data['size']
                self.world_id = world_data['id']
            self.image = Image.fromstring("RGB", self.world_size, self.world_image)

            self.fovea = self.eye.img2fovea(self.image, self.eye_pos, self.eye_angle, self.eye_scale)

            self.move_eye(self.run_model(self.fovea))

            self.fovea_img = self.eye.fovea2img()

            if self.queue_monitor != None and self.queue_monitor.empty():
                monitor_data = {
                        'fovea_img': self.fovea_img.tostring(),
                        'fovea_size': self.fovea_img.size,
                        'eye_pos': self.eye_pos,
                        'eye_scale': self.eye_scale,
                        'eye_angle': self.eye_angle,
                        }

                self.queue_monitor.put(monitor_data)
