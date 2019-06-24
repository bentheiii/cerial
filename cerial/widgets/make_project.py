from typing import Union

from pathlib import Path
import json

from fidget.backend.QtWidgets import QHBoxLayout

from fidget.core import ParseError, ValidationError
from fidget.widgets import FidgetStacked, FidgetFilePath, inner_fidget, FidgetConverter, FidgetDict, FidgetLine, \
    FidgetConfirmer

from cerial.cerial_proj import CerialProject


class MakeProjectWidget(FidgetConverter[Union[str, Path], CerialProject]):
    @inner_fidget()
    class _(FidgetConfirmer):
        @inner_fidget('make widgets')
        class _(FidgetStacked[Union[str, Path]]):
            @inner_fidget('open')
            class Open(FidgetFilePath):
                MAKE_PLAINTEXT = MAKE_TITLE = MAKE_INDICATOR = False

                EXIST_COND = True

                DIALOG = {'filter': 'cerial project (*.cerl);; all files (*.*)'}

            @inner_fidget()
            class New(FidgetConverter[dict, str]):
                @inner_fidget('new')
                class New(FidgetDict):
                    @inner_fidget('name', pattern='.+')
                    class Name(FidgetLine):
                        MAKE_TITLE = True

                def convert(self, v: dict):
                    return v['name']

            SELECTOR_CLS = 'radio'
            LAYOUT_CLS = QHBoxLayout

            def validate(self, v):
                super().validate(v)
                if v == '':
                    raise ValidationError('a name must be provided')

    def convert(self, v):
        if isinstance(v, Path):
            try:
                with v.open('r') as stream:
                    ret = CerialProject.load(stream)
            except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
                raise ParseError from e
            else:
                ret.path = v
                return ret
        return CerialProject(v)
