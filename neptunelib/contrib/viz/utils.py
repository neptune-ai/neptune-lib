from itertools import product

import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt


def fig2pil(fig):
    fig.canvas.draw()

    w,h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)
    buf = np.roll(buf, 3, axis=2)

    w, h, d = buf.shape
    return Image.frombytes("RGBA", (w , h), buf.tostring())

        
def axes2fig(axes):
    try:
        shape = axes.shape
        fig = plt.figure(figsize=(shape[0]*3,shape[1]*3))
        for i,j in product(range(shape[0]), range(shape[1])):
            fig._axstack.add(fig._make_key(axes[i,j]), axes[i,j])
    except AttributeError:
        fig = plt.figure(figsize=(6,6))
        fig._axstack.add(fig._make_key(axes), axes)
        
    return fig