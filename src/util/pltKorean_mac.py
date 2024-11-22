import os

cwd = os.getcwd()
fonts_path= '/Library/Fonts'
os.chdir(fonts_path)
osList = os.listdir()

for i in osList:
        if i.endswith('.ttf'):
            ttfPath = os.path.join(fonts_path, i)
            print(f"Using font: {ttfPath}")
            break

def set_font_manager():
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    font_name = fm.FontProperties(fname=ttfPath).get_name()
    plt.rc('font',family= font_name)
    os.chdir(cwd)

def get_ttfPath():
    os.chdir(cwd)
    return ttfPath