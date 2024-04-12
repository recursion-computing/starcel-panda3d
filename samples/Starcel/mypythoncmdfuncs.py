import subprocess
import sys

class MyPythonCMDFuncs:
    def __init__(self):
        self.firstFrame = None
        self.recording_ready = True
        self.ffmpeg = None
        pass

    def download_media(self, url):  # Might need to remove & from url
        cmdstring = ["dlp.exe -f mp4 --no-mtime -o \"Downloads\%(title)s-%(id)s.%(ext)s\"", url] # Basic Download
        cmdstring = ["dlp.exe -f bestvideo[ext=mp4] --no-mtime -o \"Downloads\%(title)s-%(id)s.%(ext)s\"", url]  # Best video
        cmdstring = ["dlp.exe -f bestaudio --no-mtime --audio-format mp3 --extract-audio -o \"Downloads\%(title)s-%(id)s.%(ext)s\"", url]  # Best Audio Only
        cmdstring = ["dlp.exe -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no -mtime -o \"Downloads\%(title)s-%(id)s.%(ext)s\"", url]  # Best video and audio

        self.dlp = subprocess.Popen(
            cmdstring,
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )

    def recordTask(self, task):  # captures a shot for every frame and passes it over to ffmpeg for encoding
        tex = base.win.getScreenshot()
        if tex is None:
            return task.cont
        if self.firstFrame:
            self.firstFrame = False  # Don't capture first empty frame
            return task.cont
        buf = tex.getRamImageAs("RGBA").getData()  # raw BGRA image data
        try:
            self.ffmpeg.stdin.write(buf)
        except:
            pass
        return task.cont

    def record_screen(self):
        cmdstring = [
            sys.executable.replace("python-3.8.10.amd64\\python.exe","CLI Tools\\ffmpeg-master-latest-win64-lgpl\\bin\\ffmpeg.exe") if sys.platform == 'win32' else 'ffmpeg',
            '-y',  # overwrite file
            '-r', '%f' % 15.0,  # frame rate of encoded video
            '-an',  # no audio
            '-analyzeduration', '0',  # skip auto codec analysis
            # # input params
            '-s', str(base.win.getXSize()) + "x" + str(base.win.getYSize()),  # window size
            '-f', 'rawvideo',  # RamImage buffer is raw buffer
            '-pix_fmt', 'rgba',  # format of panda texture RamImage buffer
            '-i', '-',  # this means a pipe
            '-vf', 'vflip',  # input is flipped upside down, flip it back up
            # output params
            # '-vcodec', 'libx264',  # encode into H.264
            'screencapture.gif'  # output filepath
        ]
        if self.recording_ready:
            self.ffmpeg = subprocess.Popen(
                cmdstring,
                stdin=subprocess.PIPE,
                bufsize=-1,
                shell=False,
            )
            taskMgr.add(self.recordTask, "ffmpegTask")
            self.recording_ready = False
        else:
            self.ffmpeg.stdin.close()  # close the pipe so that ffmpeg will close the file properly
            self.recording_ready = True
