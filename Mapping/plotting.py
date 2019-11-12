from matplotlib import pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageColor
X = [0,10,200,300,400]
Y = [0,19,245,31,144]

cube = Image.open("cube.jpg")
cube.thumbnail((45, 45))

map = Image.new('L', (420, 297))

for x in range(0,5):
    xcor = X[x]
    ycor = Y[x]
    map.paste(cube, (xcor, ycor))

map.show()



