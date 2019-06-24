from fidget.backend.QtWidgets import QHBoxLayout, QMessageBox, QWidget, QStackedWidget

from cerial.cerial_proj import CerialProject

from cerial.widgets.make_project import MakeProjectWidget
from cerial.widgets.overview_widget import OverviewWidget


class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stacked = None
        self.make_project = None
        self.overview = None

        self.current_project = None

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        self.stacked = QStackedWidget()

        self.make_project = MakeProjectWidget()

        @self.make_project.on_change.connect
        def make_project_changed():
            v = self.make_project.value()
            if not v.is_ok():
                QMessageBox.critical(self, 'error', v.details)
            else:
                self.switch_to_overview(v.value)

        self.stacked.addWidget(self.make_project)

        self.overview = OverviewWidget()

        self.stacked.addWidget(self.overview)

        layout.addWidget(self.stacked)

        self.setLayout(layout)

    def switch_to_overview(self, proj: CerialProject):
        self.overview.set_project(proj)
        self.stacked.setCurrentWidget(self.overview)


if __name__ == '__main__':
    from qtalos.backend import QApplication

    app = QApplication([])
    w = MainWidget()
    w.show()
    res = app.exec_()
    exit(res)
