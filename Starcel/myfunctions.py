import subprocess, sys, os, uuid
from panda3d.core import *  # LineStream

# TODO: Use FOAM3 to mirror these these function titles and relevant information into aliasfunctions(.csv) because it has strictly optional input fields.
# FOAM3 can interface with python files using mongodb and export into all other formats.
# In other words, for example, you can create a new entry which only has the inputs and outputs entered, and not the function name; input:wood output:chair.
# There is shared data between each function and new aliases can be quickly entered. The user doesn't have to learn new UI to change/shorten a command name.
# TODO: Quickswap of blend to bam, hdri, and startup image

    # cat=type $*
    # rm=del $*
    # mv=move $1 $2
    # cp=copy $1 $2
    # ps=tasklist $*
    # kill=taskkill /f /im $*
    # killall=taskkill /f /t /im $*
    # poweroff=shutdown /s /t 0 /f
    # reboot=shutdown /r /t 0 /f
    # whereis=where $*
    # grep=find /i $*
    # ifconfig=ipconfig
    # ll=dir /-b
    # ga=git add .
    # gc=git commit -a -m "$*"


class MyPythonCMDFuncs:
    def __init__(self):
        self.firstFrame = None
        self.recording_ready = True
        self.ffmpeg = None
        self.absolute_pipeline_path = os.path.abspath("../../")

    def set_background(self):
        images_location = self.absolute_pipeline_path + "data\default_cubemap\source\\0.png"
        print(subprocess.check_output(sys.executable + " " + self.absolute_pipeline_path + "data\generate_txo_files.py", shell=True, cwd=os.getcwd(), text=True))

    def set_startup_image(self):
        image_location = self.absolute_pipeline_path + "data\gui\loading_screen_bg.png"
        print(subprocess.check_output(sys.executable + " " + self.absolute_pipeline_path + "data\generate_txo_files.py", shell=True, cwd=os.getcwd(), text=True))

    def scenegraph(self):  # The scene "print" function
        lsb = LineStream()
        render.ls(lsb)
        text = ''
        while lsb.isTextAvailable():
            text += lsb.getLine() + '\n'
        return text

    def open_folder(self, folder):
        for root, dirs, files in os.walk(os.path.abspath(folder)):
            if root == os.path.abspath(folder):
                for dir in dirs:
                    Icon(os.path.join(root, dir), "ricegrain.glb")
            for file in files:
                if root == os.path.abspath(folder):
                    Icon(os.path.join(root, file), "ricegrainchrome.glb")


    def explorer(self):
        self.open_folder(os.getcwd())

    def desktop(self):
        print("running desktop")
        self.open_folder(os.path.expanduser("~/Desktop"))

    def auto_determine_function_name(self):  # This function handles aliases which are dialethia.
        # True contradictions occur when two functions share the same name and are equally valid. No particular function can take precedence.
        pass

    def auto_determine_undefined(self):  # This is the null pointer function. When any function is submitted and there is no valid function to call, send the undefined function as text to Recursion servers for analysis
        pass

    def ls(self, args=None):
        print("ls called")
        if args is None:
            print(subprocess.check_output("dir /b /ogn".split(" "), shell=True, cwd=os.getcwd(), text=True))
        else:
            print(subprocess.check_output("dir /b /ogn".split(" ").append(args), shell=True, cwd=os.getcwd(), text=True))

    def man(self):
        print((subprocess.run(["help"], shell=True, capture_output=True, text=True).stdout))

    def open(self, input):
        self.process = subprocess.Popen(
            [input],
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )

    def cwd(self, input):
        os.chdir(input)

    def getcwd(self):
        print(os.getcwd())

    def python(self, input):
        # print(subprocess.check_output(sys.executable + " " + input, shell=True, cwd=os.getcwd(), text=True))
        self.python = subprocess.Popen(
            [sys.executable, input],
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )

    def cmd(self, input):
        self.cmd = subprocess.Popen(
            ["cmd.exe", input],
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )

    def __get_exe_path(self, input):
        return sys.executable.replace("python-3.8.10.amd64\\python.exe","CLI Tools\\" + input)

    def search(self, input):
        if not "Everything.exe" in str(subprocess.check_output('tasklist')):
            self.everythingsearch_background_process = subprocess.Popen(
                self.__get_exe_path("Everything Search\\Everything-1.4.1.1024.x64\\Everything.exe"),
                stdin=subprocess.PIPE,
                bufsize=-1,
                shell=False,
            )

        self.everythingsearch_cli = subprocess.Popen(
            self.__get_exe_path("Everything Search\\ES-1.1.0.26\\es.exe") + " " + input,
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )


    def download_video(self, url):
        url = url.split("&")[0] if "youtu" in url else url
        cmdstring = [self.__get_exe_path("dlp.exe"), " -f \"bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best\" --no -mtime -o \"%(title)s-%(id)s.%(ext)s\"", url]  # Best video and audio
        self.dlp = subprocess.Popen(
            cmdstring,
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )

    def download_audio(self, url):
        url = url.split("&")[0] if "youtu" in url else url
        cmdstring = [self.__get_exe_path("dlp.exe"), " -f bestaudio --no-mtime --audio-format mp3 --extract-audio -o \"%(title)s-%(id)s.%(ext)s\"", url]  # Best Audio Only
        self.dlp = subprocess.Popen(
            cmdstring,
            stdin=subprocess.PIPE,
            bufsize=-1,
            shell=False,
        )

    def __recordTask(self, task):  # captures a shot for every frame and passes it over to ffmpeg for encoding
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
            self.__get_exe_path("ffmpeg-master-latest-win64-lgpl\\bin\\ffmpeg.exe") if sys.platform == 'win32' else 'ffmpeg',
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
            taskMgr.add(self.__recordTask, "ffmpegTask")
            self.recording_ready = False
        else:
            self.ffmpeg.stdin.close()  # close the pipe so that ffmpeg will close the file properly
            self.recording_ready = True


allicons = {}
import random
class Icon:
    def __init__(self, url, model):
        self.model = loader.loadModel("models/%s" % model)
        self.model.reparent_to(render)
        self.model.setPos(int(random.random()*10), int(random.random()*10), int(random.random()*10))
        self.uuid = str(uuid.uuid4())
        self.model_col = self.model.attachNewNode(CollisionNode('IconColNode' + self.uuid))
        self.model_col.node().addSolid(CollisionBox(self.model.getTightBounds()[0] - self.model.getPos(), self.model.getTightBounds()[1] - self.model.getPos()))
        self.url = url
        allicons['IconColNode' + self.uuid] = self

