import Image, ImageOps
import random
import math
import numpy as np

def _rand(start, end):
    return random.random()*(end-start) + start

class Eye:
    def __init__(self, edge_sizes=[16,8,4,2,2], core_size=16):
        self.edge_sizes = edge_sizes
        self.core_size = core_size
        self.mask_size = core_size+2*sum(self.edge_sizes)
        self.diag_size = math.sqrt(2)*self.mask_size

        self.fovea_dim = 0
        m = self.mask_size
        for e in self.edge_sizes:
            self.fovea_dim += (m/e-1)*4
            m -= e*2
        del m
        self.fovea_dim += self.core_size**2

    def _getROI(self, img, pos, angle, scale):
        left = int(pos[0]-scale*self.diag_size/2)
        top = int(pos[1]-scale*self.diag_size/2)
        right = int(pos[0]+scale*self.diag_size/2)
        bottom = int(pos[1]+scale*self.diag_size/2)
        result = img.crop((left, top, right, bottom)).rotate(angle, Image.BICUBIC)

        left = int(self.diag_size*scale/2 - self.mask_size*scale/2)
        right = int(left + self.mask_size*scale)
        result = result.crop((left, left, right, right)).resize((self.mask_size, self.mask_size), Image.BICUBIC)
        return result


    def img2fovea(self, img, pos, angle, scale):
        img = img.convert('RGB')
        img_crop = self._getROI(img, pos, angle, scale)
        (w, h) = img_crop.size
        fovea = np.zeros((self.fovea_dim*3, ))
        arr = np.asarray(img_crop)

        i_fovea = 0
        for edge_size in self.edge_sizes:
            len_side = arr.shape[0]/edge_size - 1
            for channel in xrange(3):
                for k in xrange(len_side):
                    fovea[self.fovea_dim*channel+i_fovea+k] \
                            = arr[edge_size*k:edge_size*(k+1), :edge_size, channel].mean()
                    fovea[self.fovea_dim*channel+i_fovea+len_side+k] \
                            = arr[edge_size:, edge_size*k:edge_size*(k+1), channel].mean()
                    fovea[self.fovea_dim*channel+i_fovea+len_side*2+k] \
                            = arr[edge_size*(k+1):edge_size*(k+2), -edge_size:, channel].mean()
                    fovea[self.fovea_dim*channel+i_fovea+len_side*3+k] \
                            = arr[:edge_size, edge_size*(k+1):edge_size*(k+2), channel].mean()
            i_fovea += len_side*4

            arr = arr[edge_size:-edge_size, edge_size:-edge_size, :]

        for channel in xrange(3):
            fovea[self.fovea_dim*channel+i_fovea:self.fovea_dim*(channel+1)] \
                    = arr[:,:,channel].reshape((self.core_size**2,))

        # normalize
        fovea = (fovea-fovea.min())
        fovea = fovea/(fovea.max()+0.00001)

        self.fovea = fovea
        return fovea

    def fovea2img(self):
        arr = np.zeros((self.mask_size, self.mask_size, 3))

        i_fovea = 0
        margin = 0
        for edge_size in self.edge_sizes:
            len_side = (arr.shape[0]-margin*2)/edge_size - 1
            for channel in xrange(3):
                for k in xrange(len_side):
                    if margin == 0: end = self.mask_size
                    else: end = -margin
                    arr[margin+edge_size*k:margin+edge_size*(k+1), margin:(edge_size+margin), channel] \
                            = self.fovea[self.fovea_dim*channel+i_fovea+k]
                    arr[margin+edge_size:end, margin+edge_size*k:margin+edge_size*(k+1), channel]\
                            = self.fovea[self.fovea_dim*channel+i_fovea+len_side+k]
                    arr[margin+edge_size*(k+1):margin+edge_size*(k+2), -(edge_size+margin):end, channel] \
                            = self.fovea[self.fovea_dim*channel+i_fovea+len_side*2+k]
                    arr[margin:(edge_size+margin), margin+edge_size*(k+1):margin+edge_size*(k+2), channel] \
                            = self.fovea[self.fovea_dim*channel+i_fovea+len_side*3+k]
            i_fovea += len_side*4
            margin += edge_size

        for channel in xrange(3):
            start = self.fovea_dim*channel+i_fovea
            end = self.fovea_dim*(channel+1)
            arr[margin:-margin,margin:-margin,channel] \
                    = self.fovea[start:end].reshape((self.core_size,self.core_size))
        return Image.fromarray(np.uint8(arr*255))

if __name__ == '__main__':
    for i in [1,2,3,4,5,6]:
        fov = Fovea()
        img = Image.open('%d.jpg' % i)
        (w, h) = img.size
        pos = (_rand(0, w), _rand(0, h))
        angle = 0
        scale = 2**(_rand(-2,2))

        fov.img2fovea(img, pos, angle, scale)
        img_fovea = fov.fovea2img()
        img_fovea.save('%d_fovea.png' % i)
