from pathlib import Path

from re import error as ReError

from fidget.backend.QtWidgets import QHBoxLayout, QMessageBox

from fidget.widgets import FidgetQuestion, FidgetFilePath, FidgetStacked, inner_fidget, FidgetConfirmer, FidgetTuple, \
    FidgetSpin, FidgetConverter, FidgetLine, FidgetDirPath
from fidget.core import ParseError

from cerial.cerial_proj import Episode, FileEpisode, Marks
from cerial.widgets.__util__ import compile_pattern


class AddEpisodes(FidgetStacked):
    SELECTOR_CLS = 'radio'
    MAKE_TITLE = False
    MAKE_PLAINTEXT = False
    MAKE_INDICATOR = False
    LAYOUT_CLS = QHBoxLayout

    @inner_fidget()
    class Specific(FidgetConverter):
        @inner_fidget('select file')
        class _(FidgetTuple):
            @inner_fidget('path')
            class path(FidgetFilePath):
                MAKE_TITLE = True
                MAKE_INDICATOR = False

            @inner_fidget('show')
            class show(FidgetLine):
                MAKE_TITLE = True
                MAKE_INDICATOR = False

            @inner_fidget('season')
            class season(FidgetSpin):
                MINIMUM = 1
                MAXIMUM = 100
                MAKE_TITLE = True
                MAKE_INDICATOR = False

            @inner_fidget('episode')
            class episode(FidgetSpin):
                MINIMUM = 1
                MAXIMUM = 100
                MAKE_TITLE = True
                MAKE_INDICATOR = False

        def convert(self, v):
            return [FileEpisode(v.show, v.season, v.episode, file=v.path, marks=Marks())]

    @inner_fidget()
    class ByPattern(FidgetConverter):
        def convert(self, v):
            root: Path = v.root
            if not v.pattern:
                return []
            try:
                pattern = compile_pattern(v.pattern)
            except (ReError, LookupError) as e:
                raise ParseError from e
            ret = []
            for path in root.rglob('*'):
                match = pattern.search(str(path))
                if not match:
                    continue
                d = match.groupdict()
                show = d.get('show', v.default_show)
                season = d.get('season', v.default_season)
                episode = d.get('episode', v.default_episode)
                if None in (show, season, episode):
                    continue
                season = int(season)
                episode = int(episode)
                ret.append(FileEpisode(show, season, episode, file=path, marks=Marks()))
            QMessageBox.information(self, 'result', f'{len(ret)} episodes to be added')
            return ret

        @inner_fidget()
        class _(FidgetConfirmer):
            @inner_fidget('pattern')
            class _(FidgetTuple):
                @inner_fidget('root')
                class root(FidgetDirPath):
                    MAKE_TITLE = True
                    MAKE_INDICATOR = False

                @inner_fidget('pattern')
                class pattern(FidgetLine):
                    MAKE_TITLE = True
                    MAKE_INDICATOR = False

                @inner_fidget('default show')
                class show(FidgetLine):
                    MAKE_TITLE = True
                    MAKE_INDICATOR = False

                @inner_fidget('default season')
                class season(FidgetSpin):
                    MINIMUM = 1
                    MAXIMUM = 100
                    MAKE_TITLE = True
                    MAKE_INDICATOR = False

                @inner_fidget('default episode')
                class episode(FidgetSpin):
                    MINIMUM = 1
                    MAXIMUM = 100
                    MAKE_TITLE = True
                    MAKE_INDICATOR = False


if __name__ == '__main__':
    from qtalos.backend import QApplication

    app = QApplication([])
    w = FidgetQuestion(AddEpisodes('add episodes'), cancel_value=None)
    w.show()
    res = app.exec_()
    for e in w.value().value:
        print(e.location())
    exit(res)
