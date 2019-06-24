from __future__ import annotations

from typing import List, Dict, Tuple, Optional

from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering
from pathlib import Path
import json
from dataclasses import dataclass, field
from os.path import commonpath

from cerial.__data__ import __version__


class Mark(str):
    pass


seen = Mark('seen')
do_not_play = Mark('do not play')


class Marks(Dict[Mark, datetime]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notes: List[str] = []

    def add_mark(self, mark):
        self[mark] = datetime.now()


@total_ordering
class Episode(ABC):
    def __init__(self, marks: Marks):
        self.marks = marks

    @property
    @abstractmethod
    def season_episode(self) -> Tuple[int, int]:
        pass

    @property
    @abstractmethod
    def show(self) -> str:
        pass

    @property
    def title(self) -> str:
        s, e = self.season_episode
        return f'{self.show} S{s}E{e}'

    def location(self)->Optional[str]:
        return None

    @abstractmethod
    def play(self):
        pass

    def __lt__(self, other):
        if self.show != other.show:
            raise TypeError("can't compare episodes of different shows")
        return self.season_episode < other.season_episode


class FileEpisode(Episode):
    def __init__(self, show, season, episode, title=None, *, file: Path, marks: Marks):
        super().__init__(marks)
        self.show_ = show
        self.season = season
        self.episode = episode
        self.title_ = title
        self.file = file

    @property
    def season_episode(self):
        return self.season, self.episode

    @property
    def show(self):
        return self.show_

    @property
    def title(self):
        return self.title_ or super().title

    def play(self):
        raise NotImplementedError

    def location(self):
        return str(self.file)


class CerialProject:
    def __init__(self, name: str, path: Path = None):
        self.name = name
        self.episodes: List[Episode] = []
        self.path = path

    def _dump(self):
        ret = {'protocol': '0_0_1', 'build': __version__, 'name': self.name, 'episodes': []}
        for episode in self.episodes:
            if not isinstance(episode, FileEpisode):
                raise TypeError('cannot encode a non-file episode')
            ep = {'show': episode.show_, 'season': episode.season, 'episode': episode.episode, 'file': str(episode.file),
                  'marks': {'notes': episode.marks.notes,
                            'marks': {k: v.isoformat() for k, v in episode.marks.items()}}}
            if episode.title_:
                ep['title'] = episode.title_
            ret['episodes'].append(ep)
        return ret

    def dumps(self, *args, **kwargs):
        return json.dumps(self._dump(), *args, **kwargs)

    def dump(self, *args, **kwargs):
        return json.dump(self._dump(), *args, **kwargs)

    @classmethod
    def _load_0_0_1(cls, data):
        name = data['name']
        ret = cls(name)
        for ep_data in data['episodes']:
            marks = Marks((k, datetime.fromisoformat(v)) for k, v in ep_data['marks']['marks'])
            marks.notes.extend(ep_data['marks']['notes'])
            episode = FileEpisode(ep_data['show'], ep_data['season'], ep_data['episode'], ep_data.get('title'),
                                  file=Path(ep_data['file']), marks=marks)
            ret.episodes.append(episode)
        return ret

    @classmethod
    def _load(cls, data)->CerialProject:
        prot = data['protocol']
        try:
            loader = getattr(cls, '_load_' + prot)
        except AttributeError as e:
            raise NotImplementedError('no loader for protocol ' + prot) from e
        return loader(data)

    @classmethod
    def loads(cls, *args, **kwargs):
        return cls._load(json.loads(*args, **kwargs))

    @classmethod
    def load(cls, *args, **kwargs):
        return cls._load(json.load(*args, **kwargs))

    def __str__(self):
        return f'cerial project: {self.name}, {len(self.episodes)} episodes'

    @dataclass()
    class HierarchyShow:
        name: str
        seasons: Dict[int, CerialProject.HierarchySeason] = field(default_factory=dict)
        eps_count: int = 0
        location_prefix: str = None

    @dataclass()
    class HierarchySeason:
        number: int
        episodes: Dict[int, Episode] = field(default_factory=dict)
        eps_count: int = 0
        location_prefix: str = None

    def hierarchy(self):
        def mix_prefixes(prev, new):
            if prev is None:
                return new
            elif new is None:
                return ''
            else:
                return commonpath([prev, new])

        ret: Dict[str, CerialProject.HierarchyShow] = {}
        for e in self.episodes:
            show_name = e.show
            show = ret.get(show_name)
            if not show:
                show = ret[show_name] = self.HierarchyShow(show_name)

            season_num, episode_num = e.season_episode
            season = show.seasons.get(season_num)
            if not season:
                season = show.seasons[season_num] = self.HierarchySeason(season_num)

            season.episodes[episode_num] = e

            season.eps_count += 1
            season.location_prefix = mix_prefixes(season.location_prefix, e.location())

            show.eps_count += 1
            show.location_prefix = mix_prefixes(show.location_prefix, season.location_prefix)

        return ret
