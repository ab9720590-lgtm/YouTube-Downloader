[app]

title = YouTube Downloader Arabic
package.name = youtubedownloader
package.domain = org.ahmedali

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,txt

version = 1.0

requirements = python3,kivy,yt-dlp,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 35
android.minapi = 24

android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True

android.debug_artifact = apk

[buildozer]

log_level = 2
warn_on_root = 1
