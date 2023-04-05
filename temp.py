# display an image with plt
import matplotlib.pyplot as plt

img = plt.imread('Figures/space_pressed.png')
# axis off
plt.axis('off')
plt.imshow(img)
plt.show()






