from pathlib import Path

from fidget.backend.QtWidgets import QWidget, QPushButton, QTreeWidget, QHBoxLayout, QVBoxLayout, QMenu, QToolButton, \
    QAction, QSizePolicy, QTreeWidgetItem, QFileDialog
from fidget.widgets import FidgetQuestion

from cerial.cerial_proj import CerialProject
from cerial.widgets.add_dialog import AddEpisodes


class OverviewWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.project: CerialProject = None
        self.tree: QTreeWidget = None

        self.add_dialog = None

        self.setup_ui()

    def setup_ui(self):
        master_layout = QHBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['item', '# of episodes', 'location'])

        master_layout.addWidget(self.tree)

        button_set = QVBoxLayout()
        save_btn = QToolButton()
        save_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        save_action = QAction('save')
        save_btn.setDefaultAction(save_action)
        save_menu = QMenu(parent=self)
        save_as_action = save_menu.addAction('save as')

        def save_project(proj: CerialProject, path: Path):
            with path.open('w') as w:
                proj.dump(w)
            proj.path = path

        def save_as(*a):
            filename, _ = QFileDialog.getSaveFileName(self, 'save as', filter='cerial project (*.cerl);; all files (*.*)')
            if not filename:
                return
            path = Path(filename)
            save_project(self.project, path)

        save_as_action.triggered.connect(save_as)

        @save_action.triggered.connect
        def save(*a):
            if self.project.path is None:
                save_as(*a)
            else:
                save_project(self.project, self.project.path)

        save_btn.setMenu(save_menu)
        save_btn.setPopupMode(QToolButton.MenuButtonPopup)

        add_btn = QPushButton('add episodes')
        add_btn.clicked.connect(self.show_add_dialog)
        play_btn = QPushButton('play...')
        stats_btn = QPushButton('statistics')

        button_set.addWidget(save_btn)
        button_set.addWidget(add_btn)
        button_set.addWidget(play_btn)
        button_set.addWidget(stats_btn)

        master_layout.addLayout(button_set)

        self.setLayout(master_layout)

        self.add_dialog = FidgetQuestion(AddEpisodes('add episodes'), cancel_value=None)

    def update_hierarchy(self):
        self.tree.clear()
        hierarchy = self.project.hierarchy()
        for i, show in enumerate(hierarchy.values()):
            items = []
            show_item = QTreeWidgetItem(None, [show.name, str(show.eps_count), str(show.location_prefix)])
            items.append(show_item)
            for _, season in sorted(show.seasons.items()):
                season_item = QTreeWidgetItem(show_item, [f'season {season.number}', str(season.eps_count),
                                              str(season.location_prefix)])
                items.append(season_item)
                for ep_num, episode in sorted(season.episodes.items()):
                    episode_item = QTreeWidgetItem(season_item, [f'episode {ep_num}', '', str(episode.location())])
                    items.append(episode_item)

            self.tree.insertTopLevelItems(i, items)

    def set_project(self, proj: CerialProject):
        self.project = proj
        self.update_hierarchy()

    def show_add_dialog(self):
        v = self.add_dialog.exec_()
        if not v.is_ok():
            return
        value = v.value
        if value is None:
            return
        self.project.episodes.extend(value)
        self.update_hierarchy()
