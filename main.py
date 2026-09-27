import os
import threading
import yt_dlp

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock


DOWNLOAD_DIR = "/storage/emulated/0/Download"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class DownloaderApp(App):

    def build(self):
        self.title = "YouTube Downloader"

        layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        title = Label(
            text="تحميل فيديوهات YouTube",
            font_size=24,
            size_hint_y=None,
            height=50
        )

        layout.add_widget(title)

        self.url_input = TextInput(
            hint_text="ضع رابط الفيديو هنا",
            multiline=False,
            size_hint_y=None,
            height=50
        )

        layout.add_widget(self.url_input)

        self.check_button = Button(
            text="فحص الفيديو",
            size_hint_y=None,
            height=50
        )

        self.check_button.bind(on_press=self.check_video)
        layout.add_widget(self.check_button)

        self.info = Label(
            text="",
            size_hint_y=None,
            height=60
        )

        layout.add_widget(self.info)

        self.quality = Spinner(
            text="اختر الجودة",
            values=("أفضل جودة",),
            size_hint_y=None,
            height=50
        )

        layout.add_widget(self.quality)

        self.download_button = Button(
            text="تحميل",
            size_hint_y=None,
            height=50
        )

        self.download_button.bind(on_press=self.start_download)
        layout.add_widget(self.download_button)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=25
        )

        layout.add_widget(self.progress)

        self.status = Label(
            text="جاهز",
            size_hint_y=None,
            height=50
        )

        layout.add_widget(self.status)

        return layout

    def check_video(self, instance):
        url = self.url_input.text.strip()

        if not url:
            self.status.text = "ضع رابط الفيديو أولاً"
            return

        self.status.text = "جاري فحص الفيديو..."
        self.check_button.disabled = True

        threading.Thread(
            target=self.get_video_info,
            args=(url,),
            daemon=True
        ).start()

    def get_video_info(self, url):
        try:
            options = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "بدون عنوان")

            formats = info.get("formats", [])

            qualities = []

            for f in formats:
                height = f.get("height")

                if height and height not in qualities:
                    qualities.append(height)

            qualities = sorted(
                qualities,
                reverse=True
            )

            quality_text = ["أفضل جودة"]

            for q in qualities:
                quality_text.append(f"{q}p")

            def update_ui(dt):
                self.info.text = title[:70]

                self.quality.values = tuple(
                    quality_text
                )

                self.quality.text = "أفضل جودة"

                self.status.text = "تم العثور على الفيديو"
                self.check_button.disabled = False

            Clock.schedule_once(update_ui)

        except Exception as e:

            def error_ui(dt):
                self.status.text = f"خطأ: {str(e)[:100]}"
                self.check_button.disabled = False

            Clock.schedule_once(error_ui)

    def start_download(self, instance):

        url = self.url_input.text.strip()

        if not url:
            self.status.text = "ضع رابط الفيديو أولاً"
            return

        self.download_button.disabled = True
        self.progress.value = 0
        self.status.text = "جاري التحميل..."

        quality = self.quality.text

        threading.Thread(
            target=self.download_video,
            args=(url, quality),
            daemon=True
        ).start()

    def progress_hook(self, data):

        if data["status"] == "downloading":

            total = data.get("total_bytes") or data.get(
                "total_bytes_estimate"
            )

            downloaded = data.get(
                "downloaded_bytes",
                0
            )

            if total:
                percent = (
                    downloaded / total
                ) * 100

                Clock.schedule_once(
                    lambda dt: self.update_progress(
                        percent
                    )
                )

        elif data["status"] == "finished":

            Clock.schedule_once(
                lambda dt: self.update_progress(100)
            )

    def update_progress(self, value):
        self.progress.value = value
        self.status.text = f"جاري التحميل... {int(value)}%"

    def download_video(self, url, quality):

        try:

            if quality == "أفضل جودة":

                format_code = (
                    "bestvideo+bestaudio/"
                    "best"
                )

            else:

                height = quality.replace(
                    "p",
                    ""
                )

                format_code = (
                    f"bestvideo[height<={height}]"
                    "+bestaudio/"
                    f"best[height<={height}]"
                )

            options = {
                "format": format_code,

                "outtmpl": os.path.join(
                    DOWNLOAD_DIR,
                    "%(title)s.%(ext)s"
                ),

                "progress_hooks": [
                    self.progress_hook
                ],

                "noplaylist": True,

                "quiet": True,

                "no_warnings": True,

                "merge_output_format": "mp4"
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

            def success(dt):
                self.progress.value = 100
                self.status.text = (
                    "تم التحميل بنجاح\n"
                    "مجلد التنزيلات"
                )
                self.download_button.disabled = False

            Clock.schedule_once(success)

        except Exception as e:

            def error(dt):
                self.status.text = (
                    f"فشل التحميل: {str(e)[:120]}"
                )
                self.download_button.disabled = False

            Clock.schedule_once(error)


if __name__ == "__main__":
    DownloaderApp().run()
