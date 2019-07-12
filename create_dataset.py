import numpy as np
import matlab.engine

import ImagePreProcessing as preprocess
import parametricMoDecoder as pmd
import semanticCodeVector as scv
import LandmarkDetection as ld
import FaceCropper as fc


def get_vectors(path, n):
    data = scv.SemanticCodeVector(path)
    cells = data.read_cells()

    x = data.sample_vector()

    vector = np.zeros(257, dtype=float)
    vector[0:80, ] = x['shape']
    vector[80:144, ] = x['expression']
    vector[144:224, ] = x['reflectance']
    vector[224:227, ] = x['rotation']
    vector[227:230, ] = x['translation']
    vector[230:257, ] = x['illumination']

    np.savetxt("./DATASET/semantic/x_%d.txt" % n, vector)

    vertices = data.calculate_coords(x)
    reflectance = data.calculate_reflectance(x)

    decoder = pmd.ParametricMoDecoder(vertices, reflectance, x, cells)

    formation = decoder.get_image_formation()
    # np.savetxt("./DATASET/color/color_%d.txt" % n, formation['color'])
    # np.savetxt("./DATASET/position/position_%d.tgxt" % n, formation['position'])

    cells_ordered = decoder.calculate_cell_depth()
    # np.savetxt("DATASET/cells/cells_%d.txt" % n, cells_ordered)

    return formation, cells_ordered


def prepare_images(n):
    image_path = ("./DATASET/images/im_%d.png" % n)
    cutout_path = ("./DATASET/images/cutout/im_%d.png" % n)
    cropped_image_path = ("./DATASET/images/cropped/image_%d.png" % n)

    prep = preprocess.ImagePreProcessing(n)
    prep.detect_crop_save()


def main():
    # Number of images to create
    N = 100
    path = './DATASET/model2017-1_bfm_nomouth.h5'
    eng = matlab.engine.start_matlab()

    for n in range(0, N):
        formation, cells = get_vectors(path, n)
        position = formation['position'].tolist()
        color = formation['color'].tolist()
        cells = cells.tolist()

        # create image
        image = eng.patch_and_show(position, color, cells)

        # get face mask without mouth interior
        cut = ld.LandmarkDetection()
        cutout_face = cut.cutout_mask_array(np.uint8(image))

        # crop and resize face
        cropper = fc.FaceCropper()
        cropper.generate(np.uint8(cutout_face), True, n)
        print(n)


main()