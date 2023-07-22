import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QVBoxLayout, QHBoxLayout, QTextEdit, QInputDialog, QMessageBox, QDialog, QDialogButtonBox, QFileDialog,QAbstractItemView, QScrollArea, QComboBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QRect
from TreeOfLife import *

class LifeHeirarchi(QWidget):
    default_font = QFont("B Nazanin", 12)
    


    class Dialog(QDialog):
        def __init__(self, windowTitle : str ,parent=None):
            super().__init__(parent)
            self.setWindowTitle(windowTitle)
            self.setModal(True)
            self.adjustSize()

        def text_dialog(self, input_txt):
            vbox = QVBoxLayout()
            label = QLabel(input_txt)
            label.setFont(LifeHeirarchi.default_font)
            vbox.addWidget(label)
            self.setLayout(vbox)

        def searchDialog(self):
            self.vbox = QVBoxLayout()

            superSet_hbox = QHBoxLayout()
            superSet_text = QLabel("Enter Super-Group (optional):")
            superSet_text.setFont(LifeHeirarchi.default_font)
            superSet = QLineEdit()
            superSet.setFont(LifeHeirarchi.default_font)
            superSet_hbox.addWidget(superSet_text)
            superSet_hbox.addWidget(superSet)

            self.vbox.addLayout(superSet_hbox)

            query_hbox = QHBoxLayout()

            query_text = QLabel("Search Query (optional): ")
            query_text.setFont(LifeHeirarchi.default_font)
            query = QLineEdit()
            query.setFont(LifeHeirarchi.default_font)
            query_hbox.addWidget(query_text)
            query_hbox.addWidget(query)


            combo_hbox = QHBoxLayout()
            combo_txt = QLabel("Choose Matching Type : ")
            combo_txt.setFont(LifeHeirarchi.default_font)
            combo_hbox.addWidget(combo_txt)

            combo_box = QComboBox()
            combo_box.setFont(LifeHeirarchi.default_font)
            combo_box.addItem("inclusive")
            combo_box.addItem("exact")
            combo_box.addItem("regular expression")
            combo_box.setCurrentIndex(0)
            combo_hbox.addWidget(combo_box)

            self.vbox.addLayout(combo_hbox)
            

            self.vbox.addLayout(query_hbox)


            self.filter_box = QVBoxLayout()
            self.vbox.addLayout(self.filter_box)
            self.filterNum = 0

            self.filters = dict()
            def addfilter():
                self.filterNum
                self.filterNum += 1
                vbox = QVBoxLayout()
                filterlabel = QLabel(f"-Filter{self.filterNum}----------------")
                filterlabel.setFont(LifeHeirarchi.default_font)
                vbox.addWidget(filterlabel)

                hbox1 = QHBoxLayout()
                label1 = QLabel("Attribute Name : ")
                label1.setFont(LifeHeirarchi.default_font)
                attr = QLineEdit()
                attr.setFont(LifeHeirarchi.default_font)
                hbox1.addWidget(label1)
                hbox1.addWidget(attr)
                vbox.addLayout(hbox1)


                hbox2 = QHBoxLayout()
                label2 = QLabel("Operation : ")
                label2.setFont(LifeHeirarchi.default_font)

                combo_box = QComboBox()
                combo_box.setFont(LifeHeirarchi.default_font)
                combo_box.addItem("exact")
                combo_box.addItem("range")
                combo_box.addItem("lt")
                combo_box.addItem("lte")
                combo_box.addItem("gt")
                combo_box.addItem("gte")
                combo_box.setCurrentIndex(0)
                hbox2.addWidget(combo_box)
                vbox.addLayout(hbox2)


                hbox3 = QHBoxLayout()
                label3 = QLabel("Value : ")
                label3.setFont(LifeHeirarchi.default_font)
                val = QLineEdit()
                val.setFont(LifeHeirarchi.default_font)
                hbox3.addWidget(label3)
                hbox3.addWidget(val)
                vbox.addLayout(hbox3)                


                self.filters[self.filterNum] = [attr, combo_box, val]

                self.filter_box.addLayout(vbox)
                self.adjustSize()




            add_filter_btn = QPushButton("Add New Filter")
            add_filter_btn.setFont(LifeHeirarchi.default_font)
            add_filter_btn.clicked.connect(addfilter)
            self.vbox.addWidget(add_filter_btn)

            search_btn = QPushButton("Search")
            search_btn.setFont(LifeHeirarchi.default_font)
            self.vbox.addWidget(search_btn)

            self.table = QTableWidget()
            self.table.setFont(LifeHeirarchi.default_font)


            self.search_results = dict()
            def search():
                filters = dict()
                for val in self.filters.values():
                    filters[val[0]] = (val[1], val[2])
                self.search_results = Group.advancedSearch(superSet.text(), query.text(), combo_box.currentText(), filters)
                row = 0
                self.table.setColumnCount(2)
                self.table.setRowCount(len(self.search_results.keys()))
                self.table.setHorizontalHeaderLabels(["Type", "Name"])
                for type, name in self.search_results.keys():
                    self.table.setItem(row, 0, QTableWidgetItem(type))
                    self.table.setItem(row, 1, QTableWidgetItem(name))
                    row += 1
                self.adjustSize()

            search_btn.clicked.connect(search)



            def clicked_on_item(item):
                row = item.row()
                txt = LifeHeirarchi.Dialog("Item Info", self)
                key = (self.table.item(row, 0).text(), self.table.item(row, 1).text())
                instance = self.search_results[key]
                txt.text_dialog(instance.info)
                txt.exec()

            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            
            self.table.itemClicked.connect(clicked_on_item)

            scroll_area = QScrollArea()
            scroll_area.setWidget(self.table)

            layout = QVBoxLayout()
            layout.addWidget(scroll_area)
            self.vbox.addLayout(layout)
            self.setLayout(self.vbox)

            self.adjustSize()
            self.setMaximumHeight(460)
    
        def addDialog(self):
            self.vbox = QVBoxLayout()
            input_text = QTextEdit()
            input_text.setFont(LifeHeirarchi.default_font)
            input_text.setPlaceholderText('Enter the new group:\nformat : (type="...", name="...", superSet=("type", "name"), age=..., weight=..., size=..., info="...", extraAttr=(key="value")')
            self.vbox.addWidget(input_text)

            def clicked_on():
                Group.createNew(input_text.toPlainText())
                self.close()

            btn = QPushButton("Add")
            btn.setFont(LifeHeirarchi.default_font)
            btn.clicked.connect(clicked_on)
            self.vbox.addWidget(btn)
            
            self.setLayout(self.vbox)
        
        def editDialog(self):
            self.vbox = QVBoxLayout()
            self.setLayout(self.vbox)
            group_combo = QComboBox()
            group_combo.setFont(LifeHeirarchi.default_font)
            attr_combo = QComboBox()
            attr_combo.setFont(LifeHeirarchi.default_font)
            
            for instance in Group._instances.keys():
                group_combo.addItem(str(instance))
            group_combo.setCurrentIndex(0)

            group_btn = QPushButton("Choose Group")
            group_btn.setFont(LifeHeirarchi.default_font)
            def group_clicked():
                attr_combo.clear()
                instance = Group._instances[list(Group._instances.keys())[group_combo.currentIndex()]]
                try:
                    for attr in instance.attributes.keys():
                        attr_combo.addItem(attr)
                except:
                    pass
            group_btn.clicked.connect(group_clicked)
            
            h1 = QHBoxLayout()
            h1.addWidget(group_combo)
            h1.addWidget(group_btn)

            replace = QLineEdit()
            replace.setPlaceholderText("Enter the new value for attribute:")
            replace.setFont(LifeHeirarchi.default_font)

            btn = QPushButton("Edit")
            btn.setFont(LifeHeirarchi.default_font)

            def edit():
                instance = Group._instances[list(Group._instances.keys())[group_combo.currentIndex()]]
                newData= (attr_combo.currentText(), replace.text())
                instance.info = newData
                self.close()

            btn.clicked.connect(edit)


            self.vbox.addLayout(h1)
            self.vbox.addWidget(attr_combo)
            self.vbox.addWidget(replace)
            self.vbox.addWidget(btn)

            self.adjustSize()
            self.setFixedWidth(530)
        
        def deleteDialog(self):
            self.vbox = QVBoxLayout()
            self.setLayout(self.vbox)
            group_combo = QComboBox()
            group_combo.setFont(LifeHeirarchi.default_font)
            
            for instance in Group._instances.keys():
                group_combo.addItem(str(instance))
            group_combo.setCurrentIndex(0)

            del_btn = QPushButton("Choose Group")
            del_btn.setFont(LifeHeirarchi.default_font)
            def delete_group():
                ins = list(Group._instances.keys())[group_combo.currentIndex()]
                Group.delete(ins[0], ins[1])
                self.close()
            del_btn.clicked.connect(delete_group)

            self.vbox.addWidget(group_combo)
            self.vbox.addWidget(del_btn)

            self.adjustSize()
            self.setFixedWidth(350)





    def __init__(self):
        super().__init__()
        self.mainPage()

    def mainPage(self):
        self.setWindowTitle("Life Heirarchi")

        tree_font = QFont("Times New Roman", 18)
        self.tree_label = QLabel('Life\n└── Domain\n    └── Kingdom\n        └── Phylum\n            └── Class\n                └── Order\n                    └── Family\n                        └── Genus\n                            └── Species\n')
        self.tree_label.setFont(tree_font)

        input_layout = QHBoxLayout() 

        file_button = QPushButton("Read From Text File")
        file_button.setFont(self.default_font)
        file_button.clicked.connect(self.fileDialog)
        input_layout.addWidget(file_button)


        edit_layout = QHBoxLayout()

        add_group_btn = QPushButton("Add Group")
        add_group_btn.setFont(self.default_font)
        add_group_btn.clicked.connect(self.addGroup) 
        edit_layout.addWidget(add_group_btn)

        edit_group_btn = QPushButton("Edit Group")
        edit_group_btn.setFont(self.default_font)
        edit_group_btn.clicked.connect(self.editGroup)
        edit_layout.addWidget(edit_group_btn)

        del_group_btn = QPushButton("Delete Group")
        del_group_btn.setFont(self.default_font)
        del_group_btn.clicked.connect(self.removeGroup)
        edit_layout.addWidget(del_group_btn)


        search_btn = QPushButton("Search")
        search_btn.setFont(self.default_font)
        search_btn.clicked.connect(self.search)


        
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tree_label)
        self.main_layout.addLayout(input_layout)
        self.main_layout.addLayout(edit_layout)
        self.main_layout.addWidget(search_btn)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a central widget and set the main layout
        self.setLayout(self.main_layout)
        self.adjustSize()
        self.setFixedSize(self.size().width(), self.size().height())

    def fileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Text Files (*.txt)")

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
            file = selected_file
            Group.readFromFile(file)
        if Group._instances:
            self.tree_label.setText(str(Group.fullTreeView()))
        else:
            self.tree_label.setText('Life\n└── Domain\n    └── Kingdom\n        └── Phylum\n            └── Class\n                └── Order\n                    └── Family\n                        └── Genus\n                            └── Species\n')

    

    def addGroup(self):
        dialog = self.Dialog("Add Group", self)
        dialog.addDialog()
        dialog.exec()
        if Group._instances:
            self.tree_label.setText(str(Group.fullTreeView()))
        else:
            self.tree_label.setText('Life\n└── Domain\n    └── Kingdom\n        └── Phylum\n            └── Class\n                └── Order\n                    └── Family\n                        └── Genus\n                            └── Species\n')

    def editGroup(self):
        dialog = self.Dialog("Delete", self)
        dialog.editDialog()
        dialog.exec()
        if Group._instances:
            self.tree_label.setText(str(Group.fullTreeView()))
        else:
            self.tree_label.setText('Life\n└── Domain\n    └── Kingdom\n        └── Phylum\n            └── Class\n                └── Order\n                    └── Family\n                        └── Genus\n                            └── Species\n')

    def removeGroup(self):
        dialog = self.Dialog("Delete", self)
        dialog.deleteDialog()
        dialog.exec()
        if Group._instances:
            self.tree_label.setText(str(Group.fullTreeView()))
        else:
            self.tree_label.setText('Life\n└── Domain\n    └── Kingdom\n        └── Phylum\n            └── Class\n                └── Order\n                    └── Family\n                        └── Genus\n                            └── Species\n')

    def search(self):
        dialog = self.Dialog("Search", self)
        dialog.searchDialog()
        dialog.exec()
        if Group._instances:
            self.tree_label.setText(str(Group.fullTreeView()))
        else:
            self.tree_label.setText('Life\n└── Domain\n    └── Kingdom\n        └── Phylum\n            └── Class\n                └── Order\n                    └── Family\n                        └── Genus\n                            └── Species\n')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LifeHeirarchi()
    window.show()

    sys.exit(app.exec())