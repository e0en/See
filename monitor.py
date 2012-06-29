from multiprocessing import Process, Queue
import Image, StringIO, os
import cairo, array
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf

from agent import Agent
from world_images import World as ImageWorld
from world import World as CamWorld

GObject.threads_init()

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

class Monitor:
    def __init__(self, queue_world, queue_agent):
        self.queue_world = queue_world
        self.queue_agent = queue_agent

        self.window = Gtk.Window(title="Sequential, Unsupervised, Foveal RBM")
        self.image = Gtk.Image()
        self.world_area = Gtk.DrawingArea()
        self.fovea_image = Gtk.Image()

        self.box = Gtk.Box()
        self.window.add(self.box)
        self.fovea_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.box.add(self.world_area)
        self.box.add(self.fovea_box)

        self.fovea_box.add(Gtk.Label("Fovea"))
        self.fovea_box.add(self.fovea_image)
        self.window.show_all()

        GObject.idle_add(self.on_idle)
        self.window.connect("delete-event", self.destroy)

        self.agent_data = None
        self.world_data = None

    def destroy(self, window, event):
        Gtk.main_quit()

    def on_idle(self):
        cairo_context = self.world_area.get_property('window').cairo_create()

        if not self.queue_world.empty():
            self.world_data = self.queue_world.get()

        if not self.queue_agent.empty():
            self.agent_data = self.queue_agent.get()
            pixbuf = image2pixbuf(Image.fromstring("RGB", self.agent_data['fovea_size'], self.agent_data['fovea_img']))
            self.fovea_image.set_from_pixbuf(pixbuf)

        # draw an image using cairo
        if self.world_data != None:
            image_size = self.world_data['size']
            world_image = self.world_data['image_string']
            w, h = image_size
            self.world_area.set_size_request(w,h)
            self.window.resize_to_geometry(w, h)

            rgba_string = Image.fromstring("RGB", image_size, world_image).convert('RGBA').tostring()
            image_buffer = array.array('B', rgba_string)
            image_buffer[0::4], image_buffer[2::4] = image_buffer[2::4], image_buffer[0::4] # RGBA to BGRA (reversed ARGB)
            stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
            cairo_surface = cairo.ImageSurface.create_for_data(image_buffer, cairo.FORMAT_ARGB32, w, h, stride)

            cairo_context.set_source_surface(cairo_surface, 0, 0)
            cairo_context.paint()

        if self.agent_data != None:
            cairo_context.translate(*self.agent_data['eye_pos'])
            cairo_context.rotate(self.agent_data['eye_angle']*3.14/180)
            cairo_context.scale(self.agent_data['eye_scale'], self.agent_data['eye_scale'])
            square_size = self.agent_data['fovea_size'][0]*self.agent_data['eye_scale']
            cairo_context.rectangle(-square_size/2, -square_size/2, square_size, square_size)
            cairo_context.set_source_rgba(0, 0, 0, 0.5)
            cairo_context.fill()
            cairo_context.rectangle(-square_size/2, -square_size/2, square_size, square_size)
            cairo_context.set_source_rgba(1, 1, 1, 0.5)
            cairo_context.stroke()

        return True

    def run(self):
        app = self
        Gtk.main()

if __name__ == '__main__':
    try:
    #if True:
        q_world_agent = Queue()
        q_world_monitor = Queue()
        q_agent_monitor = Queue()

        '''
        image_list = [os.path.join('images/', x) for x in os.listdir('images/')]
        world = ImageWorld(image_list, q_world_agent, q_world_monitor)
        '''

        world = CamWorld(q_world_agent, q_world_monitor)
        agent = Agent(q_world_agent, q_agent_monitor)
        monitor = Monitor(q_world_monitor, q_agent_monitor)

        p_world = Process(target=world.run)
        p_agent = Process(target=agent.run)
        p_monitor = Process(target=monitor.run)

        p_world.start()
        p_agent.start()
        p_monitor.start()

        p_world.join()
        p_agent.join()
        p_monitor.join()
    except:
        print 'program terminated'
        p_monitor.terminate()
        p_world.terminate()
        p_agent.terminate()
