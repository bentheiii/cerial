from socket import create_connection
from time import sleep
from typing import Optional, Tuple

from pathlib import Path
from subprocess import Popen, PIPE, DEVNULL

import winreg

from cerial.video.video_interface import VideoInterface


def guess_vlc_path():
    for pkey, path in [(winreg.HKEY_CURRENT_USER, r'SOFTWARE\VideoLAN\VLC'),
                       (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\VideoLAN\VLC')]:
        try:
            key = winreg.OpenKey(pkey, path)
        except OSError:
            continue

        return Path(winreg.QueryValueEx(key, None)[0])

    raise OSError('vlc installation could not be found')

print(guess_vlc_path())

class VlcInterface(VideoInterface):
    cmd_options = ['--control', 'rc:pause_click', '--rc-host', 'localhost:11235']

    def __init__(self):
        super().__init__()
        self.instance: Optional[Popen] = None
        self.connection = None

    def play(self, file: Path):
        if not self.instance:
            self.instance = Popen([str(guess_vlc_path()), *self.cmd_options], stdin=None, stdout=None, stderr=PIPE)
            try:
                self.connection = create_connection(('localhost', 11235))
            except:
                print('err')
                input()
                print(self.instance.stderr.read().decode('utf-8'))
                self.instance.kill()
                raise

        self.connection.send(b'clear\nadd ' + str(file).encode('utf-8') + b'\n')

    def status(self) -> Optional[Tuple[Path, float, float]]:
        return None

    def close(self):
        return None

    def __del__(self):
        if self.instance and self.instance.poll() is None:
            self.instance.kill()


v = VlcInterface()
v.play(Path(
    r'"M:\Harbor\tv\Seinfeld.Complete.Series-720p.WEBrip.AAC.EN-SUB.x264-[MULVAcoded]\Season 7\Seinfeld.S07E08.The.Pool.Guy.720p.WEBrip.AAC.EN-SUB.x264-[MULVAcoded].mkv"'))
v.instance.wait()
