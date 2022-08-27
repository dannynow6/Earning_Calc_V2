# File name: main.py

from kivy.lang import Builder
from kivymd.app import MDApp


class EarningCalcApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"

        return Builder.load_file("ec.kv")


if __name__ == "__main__":
    EarningCalcApp().run()
