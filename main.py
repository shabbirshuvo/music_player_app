import os
import random
import time

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from PIL import Image as PILImage
from kivy.uix.progressbar import ProgressBar

Window.size = (400, 600)


def find_files(root_dir, file_format):
    matched_files = []

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(file_format):
                matched_files.append(os.path.join(root, file))

    return matched_files


def resize_image(input_image_path, output_image_path, desired_size):
    try:
        with PILImage.open(input_image_path) as img:
            img = img.resize(desired_size, PILImage.ANTIALIAS)
            img.save(output_image_path)
        return True
    except Exception as e:
        print("Error:", e)
        return False


class MusicPlayer(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.location_label = None
        self.filechooser = None
        self.progress_bar = None
        self.music_dir = None
        self.select_button = None
        self.file_chooser = None
        self.now_playing_label = None
        self.previous_button = None
        self.volume_slider = None
        self.next_button = None
        self.current_song_index = 0
        self.elapsed_time = 0
        self.start_time = None
        self.current_time_label = None
        self.total_time_label = None
        self.album_image = None
        self.song_label = None
        self.play_image = None
        self.sound = None
        self.playing_song = None
        self.music_files = None
        self.play_button = None
        self.stop_button = None

    # def update_progress_bar(self, value):
    #     if self.progress_bar.value < 100:
    #         self.progress_bar.value += 1

    def update_location_label(self, dt):
        self.location_label.text = "    Current Location: " + self.music_dir

    def move_song_label(self, dt):
        text = self.location_label.text
        updated_text = text[1:] + text[0]
        self.location_label.text = updated_text

    def open_folder_dialog(self, instance):
        layout = BoxLayout(orientation='vertical', size_hint=(1, 1))

        # Note that we're using dirselect=True here.
        filechooser = FileChooserListView(path=os.getcwd(), dirselect=True)

        select_button = Button(text="Select", size_hint_y=None, height=30, on_release=self.select_folder)
        cancel_button = Button(text="Cancel", size_hint_y=None, height=30, on_release=self.dismiss_popup)

        layout.add_widget(filechooser)
        layout.add_widget(select_button)
        layout.add_widget(cancel_button)

        # Here we're creating a reference to the filechooser to be able to fetch the selection later.
        self.filechooser = filechooser

        self._popup = Popup(title="Choose Folder", content=layout, size_hint=(0.9, 0.9))
        self._popup.open()

    # def selected_directory(self, instance):
    #     selected_dir = self.file_chooser.path
    #     # Use the directory path for your purpose here
    #     print(f"Selected directory: {selected_dir}")
    #     self.music_dir = selected_dir

    def select_folder(self, instance):
        # Get the selected folder. If multiple directories can be selected,
        # this would return a list. Otherwise, it returns the current directory.
        folder = self.filechooser.path
        print("Selected folder:", folder)
        self.dismiss_popup(instance)
        self.music_dir = folder
        self.music_files = find_files(self.music_dir, ".mp3")
        if self.sound:
            self.stop_music(instance)
            self.play_music(instance)
        Clock.schedule_once(self.update_location_label, 0.1)

    def dismiss_popup(self, instance):
        self._popup.dismiss()

    def play_next_song(self, instance):
        self.current_song_index += 1
        if self.current_song_index >= len(self.music_files):
            self.current_song_index = 0  # Loop back to the start
        self.play_music(instance)

    def play_last_song(self, instance):
        self.current_song_index -= 1
        if self.current_song_index < 0:
            self.current_song_index = len(self.music_files) - 1  # Loop back to the last song
        self.play_music(instance)

    def update_progress_bar(self, value):
        if self.progress_bar.value < 100:
            elapsed_time = time.time() - self.start_time
            song_length = self.sound.length
            percentage = (elapsed_time / song_length) * 100
            self.progress_bar.value = percentage

    def update_song_label(self, dt):
        text = self.song_label.text
        updated_text = text[1:] + text[0]
        self.song_label.text = updated_text

    # def update_current_time_label(self, dt):
    #     current_time = time.strftime("%M:%S", time.gmtime(self.progress_bar.value))
    #     total_time = time.strftime("%M:%S", time.gmtime(self.sound.length))
    #     self.current_time_label.text = current_time
    #     self.total_time_label.text = total_time
    def update_current_time_label(self, dt):
        if self.sound.state == 'stop':
            # Unschedule the time update
            Clock.unschedule(self.update_current_time_label)

            # You can reset the progress bar or other UI components here if needed
            self.progress_bar.value = 0
            self.current_time_label.text = "00:00"
            self.play_button.disabled = False
            self.stop_button.disabled = True
            return

        # Increment the elapsed time
        self.elapsed_time += dt

        # Formatting the elapsed time and total duration to MM:SS format
        current_time = time.strftime("%M:%S", time.gmtime(self.elapsed_time))
        total_time = time.strftime("%M:%S", time.gmtime(self.sound.length))

        self.current_time_label.text = current_time
        self.total_time_label.text = total_time

        if current_time == total_time:
            self.play_next_song(self.next_button)

    # def play_music(self, instance):
    #     self.elapsed_time = 0
    #     self.play_button.disabled = True
    #     self.stop_button.disabled = False
    #     space_gap = "    "  # Adjust this to the number of spaces you want
    #     self.playing_song = random.choice(self.music_files)
    #     self.song_label.text = self.playing_song + space_gap + self.playing_song
    #     # self.playing_song = random.choice(self.music_files)
    #     self.sound = SoundLoader.load(self.playing_song)
    #     # self.song_label.text = self.playing_song + "    "
    #     self.start_time = time.time()
    #     self.sound.play()
    #
    #     Clock.schedule_interval(self.update_song_label, 0.1)
    #     Clock.schedule_interval(self.update_progress_bar, 0.1)
    #     Clock.schedule_interval(self.update_current_time_label, .1)

    def play_music(self, instance):
        if self.sound:
            self.sound.stop()

        # Unschedule previous events before scheduling new ones
        Clock.unschedule(self.update_song_label)
        Clock.unschedule(self.update_progress_bar)
        Clock.unschedule(self.update_current_time_label)

        self.elapsed_time = 0
        self.now_playing_label.opacity = 1
        self.play_button.disabled = True
        self.stop_button.disabled = False
        self.next_button.disabled = False
        self.previous_button.disabled = False

        self.playing_song = self.music_files[self.current_song_index]  # Update this line
        space_gap = "    "
        self.song_label.text = self.playing_song + space_gap + self.playing_song

        self.sound = SoundLoader.load(self.playing_song)
        self.start_time = time.time()
        self.sound.play()

        Clock.schedule_interval(self.update_song_label, 0.1)
        Clock.schedule_interval(self.update_progress_bar, 0.1)
        Clock.schedule_interval(self.update_current_time_label, .1)

    def stop_music(self, instance):
        self.sound.stop()
        self.now_playing_label.opacity = 0
        self.play_button.disabled = False
        self.stop_button.disabled = True
        self.next_button.disabled = True
        self.previous_button.disabled = True
        Clock.unschedule(self.update_song_label)
        Clock.unschedule(self.update_progress_bar)
        Clock.unschedule(self.update_current_time_label)
        self.current_time_label.text = "00:00"
        self.total_time_label.text = "00:00"
        self.progress_bar.value = 0
        self.volume_slider.value = 0.5

    def volume_changed(self, instance, value):
        self.sound.volume = self.volume_slider.value

    def build(self):
        self.root = MDRelativeLayout(md_bg_color=(0, 0, 0, 1))
        self.title = "Music Player"

        # getting the songs from the music folder
        if self.music_dir is None:
            self.music_dir = os.getcwd()
        self.music_files = find_files(self.music_dir, ".mp3")

        self.now_playing_label = Label(text="Now Playing", pos_hint={"center_x": 0.5, "center_y": 0.9},
                                       font_size=50, opacity=0)
        self.root.add_widget(self.now_playing_label)

        self.song_label = Label(text="", pos_hint={"center_x": 0.5, "center_y": 0.85}, font_size=40)
        self.root.add_widget(self.song_label)

        self.album_image = Image(source="album.png",
                                 pos_hint={"center_x": 0.5, "center_y": 0.55},
                                 size_hint=(0.7, 0.5))
        self.root.add_widget(self.album_image)
        self.progress_bar = ProgressBar(pos_hint={"center_x": 0.5, "center_y": 0.2},
                                        size_hint=(0.7, 0.5), max=100, value=0)
        self.current_time_label = Label(text="0:00", pos_hint={"center_x": 0.1, "center_y": 0.2})
        self.root.add_widget(self.current_time_label)
        self.total_time_label = Label(text="0:00", pos_hint={"center_x": 0.9, "center_y": 0.2})
        self.root.add_widget(self.total_time_label)

        self.root.add_widget(self.progress_bar)

        # self.play_image = "play.jpeg"
        # resize_image("play.jpeg", self.play_image, (1500, 1500))
        self.previous_button = MDIconButton(pos_hint={"center_x": 0.4, "center_y": 0.15},
                                            icon="previous.png",
                                            on_press=self.play_last_song,
                                            disabled=True
                                            )
        self.root.add_widget(self.previous_button)
        self.play_button = MDIconButton(pos_hint={"center_x": 0.5, "center_y": 0.15},
                                        icon="play.jpeg",
                                        on_press=self.play_music
                                        )
        self.root.add_widget(self.play_button)
        self.stop_button = MDIconButton(pos_hint={"center_x": 0.6, "center_y": 0.15},
                                        icon="stop.jpeg",
                                        disabled=True,
                                        on_press=self.stop_music
                                        )
        self.root.add_widget(self.stop_button)
        self.next_button = MDIconButton(pos_hint={"center_x": 0.7, "center_y": 0.15},
                                        icon="next.png",
                                        on_press=self.play_next_song,
                                        disabled=True
                                        )
        self.root.add_widget(self.next_button)
        self.volume_slider = Slider(min=0, max=1, value=0.5, pos_hint={"center_x": 0.2, "center_y": 0.15},
                                    size_hint=(0.35, 0.1))
        self.volume_slider.bind(value=self.volume_changed)
        self.root.add_widget(self.volume_slider)
        self.file_chooser = FileChooserListView(path='.', dirselect=True)

        self.select_button = Button(text="Select Directory", on_release=self.open_folder_dialog, size_hint=(.5, 0.05),
                                    pos_hint={"center_x": 0.5, "center_y": 0.09})
        self.root.add_widget(self.select_button)
        self.location_label = Label(text="    Current Location: " + self.music_dir,
                                    pos_hint={"center_x": 0.5, "center_y": 0.05})
        self.root.add_widget(self.location_label)

        Clock.schedule_interval(self.move_song_label, 0.2)

        return self.root


if __name__ == '__main__':
    (MusicPlayer().run())
