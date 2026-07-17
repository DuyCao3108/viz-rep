from numpy.polynomial import test

from plot.bar_1 import plot_bar
from src.custom.colors import COLOR_THEMES, plot_step_palette,get_color_code, make_step, plot_theme_palette

def test_color():
    save_path='./output/pal.png'
    print(plot_step_palette('tokyo',save_path=save_path))
    # print(plot_theme_palette('cate-55',save_path=save_path))

def plot():
    plot_bar()

if __name__=="__main__":
    plot()
