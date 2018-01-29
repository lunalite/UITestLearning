import os
from glob import glob
from PIL import Image
from crawler.Config import Config

result = [y for x in os.walk(Config.screen_location) for y in glob(os.path.join(x[0], '*.png'))]
dimension_list = []

for f in result:
    try:
        with Image.open(f) as img:
            width, height = img.size
            dimension_list.append((f, width, height))
    except Exception:
        print(f)
        dimension_list.append((f, 'err', 'err'))

with open('./img_dimension_extract.txt', 'w') as f:
    for dim in dimension_list:
        f.write('%s\t%s\t%s' % (dim[0], dim[1], dim[2]))
        f.write('\n')
