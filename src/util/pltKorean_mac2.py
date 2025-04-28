import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


class Fontmanager:
    def __init__(self, fonts_dir="/Library/Fonts"):
        self.cwd = os.getcwd()
        self.fonts_dir = fonts_dir
        self.ttf_paths = [
            os.path.join(fonts_dir, f)
            for f in os.listdir(fonts_dir)
            if f.lower().endswith(".ttf")
        ]
        self.n = 0

        if not self.ttf_paths:
            raise ValueError("No .ttf fonts found")
        self.ttf_path = self.ttf_paths[self.n]
        print("Using font : {self.ttf_path}")

    def set_font(self):
        font_name = fm.FontProperties(fname=self.ttf_path).get_name()
        plt.rc("font", family=font_name)
        print(f"Set font to: {font_name}")

    def get_current_font_path(self):
        return self.ttf_path

    def next_font(self):
        self.n = (self.n + 1) % len(self.ttf_paths)  # 자동 순환
        self.ttf_path = self.ttf_paths[self.n]
        self.set_font()
        print(f"Font {self.n + 1}/{len(self.ttf_paths)}: {self.ttf_path}")
