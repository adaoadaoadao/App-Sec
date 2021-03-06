# -*-coding:utf-8-*-
from PIL import Image

def cut(str):
    im = Image.open(str)
    # the width and height of the image
    img_size = im.size
    print("The wight and height of the image is{}".format(img_size))
    w, h = img_size
    if w < h:
        min = w
    else:
        min = h
    # print (min)
    '''
    cut
    x means the distance from left side
    y means the distance from right side
    w and h means the size of resized image
    '''

    x = int(w / 2 - min / 2)
    y = int(h / 2 - min / 2)
    # print(x, y)
    w = min
    h = min
    # print(x, y, x+w, y+h)
    region = im.crop((x, y, x + w, y + h))
    region_size = region.size
    # region.show()
    print("The wight and height of the new image is{}".format(region_size))
    region = region.convert("RGB")
    region.save(str)
