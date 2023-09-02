import os
import random
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivymd.uix.label import label

Window.size = (400, 600)


def find_files(root_dir, file_format):
    matched_files = []

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(file_format):
                matched_files.append(os.path.join(root, file))

    return matched_files


class MusicPlayer(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.music_files = None
        self.play_button = None
        self.stop_button = None

    def build(self):
        self.root = MDRelativeLayout(md_bg_color=(0, 0, 0, 1))
        self.title = "Music Player"

        # getting the songs from the music folder
        self.music_files = find_files(".", ".mp3")
        print(self.music_files)

        self.play_button = MDIconButton(pos_hint={"center_x": 0.4, "center_y": 0.5},
                                        icon="play.jpeg",
                                        )
        self.root.add_widget(self.play_button)
        self.stop_button = MDIconButton(pos_hint={"center_x": 0.6, "center_y": 0.5},
                                        icon="stop.jpeg"
                                        )
        self.root.add_widget(self.stop_button)

        return self.root


if __name__ == '__main__':
    (MusicPlayer().run())
