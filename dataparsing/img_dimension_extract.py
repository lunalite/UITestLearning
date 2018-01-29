import os
from glob import glob
from PIL import Image
from crawler.Config import Config

result = [y for x in os.walk(Config.screen_location) for y in glob(os.path.join(x[0], '*.png'))]
print(result)

dimension_list = []

for f in result:
    with Image.open(f) as img:
        width, height = img.size
        dimension_list.append((f, width, height))

print(dimension_list)
