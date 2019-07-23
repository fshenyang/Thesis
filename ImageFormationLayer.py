import numpy as np
import matlab.engine
import matplotlib.pyplot as plt

import SemanticCodeVector as scv
import ParametricMoDecoder as pmd
import LandmarkDetection as ld
import FaceCropper as fc
import ImagePreprocess as preprocess
import time

class ImageFormationLayer(object):

    def __init__(self, vector):
        self.vector = vector
        self.path = './DATASET/model2017-1_bfm_nomouth.h5'
        self.preprocess = preprocess.ImagePreprocess()

    def get_vertices_and_reflectance(self):
        semantic = scv.SemanticCodeVector(self.path)
        vertices = semantic.calculate_coords(self.vector)
        reflectance = semantic.calculate_reflectance(self.vector)

        # read average face cells
        cells = semantic.read_cells()

        return vertices, reflectance, cells

    def get_reconstructed_image(self):
        vertices, reflectance, cells = self.get_vertices_and_reflectance()
        decoder = pmd.ParametricMoDecoder(vertices, reflectance, self.vector, cells)

        formation = decoder.get_image_formation()
        cells = decoder.calculate_cell_depth()

        position = formation['position']
        color = formation['color']

        # draw image
        # start = time.time()
        image = self.preprocess.patch(position, color, cells)
        # print("time for patch : ", time.time() - start)

        # get face mask without mouth interior
        cut = ld.LandmarkDetection()
        cutout_face = cut.cutout_mask_array(np.uint8(image), False)

        # crop and resize face
        cropper = fc.FaceCropper()
        cropped_face = cropper.generate(np.uint8(cutout_face), False, None)

        return cropped_face


def main():
    show_result = True
    n = 10
    vector_path = ("./DATASET/semantic/x_%d.txt" % n)
    vector = np.loadtxt(vector_path)

    x = {
        "shape": vector[0:80, ],
        "expression": vector[80:144, ],
        "reflectance": vector[144:224, ],
        "rotation": vector[224:227, ],
        "translation": vector[227:230, ],
        "illumination": vector[230:257, ]
    }

    formation = ImageFormationLayer(x)
    image = formation.get_reconstructed_image()

    if show_result:
        plt.imshow(image)
        plt.show()


# main()
