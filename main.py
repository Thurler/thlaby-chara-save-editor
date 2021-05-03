from characterinfo import characterArray as characters
from PySide6 import QtCore, QtWidgets, QtGui

import os
import sys
import copy

def textWidget(text, pt, bold):
  label = QtWidgets.QLabel()
  label.setText(text)
  label.setAlignment(QtCore.Qt.AlignCenter)
  font = label.font()
  font.setPointSize(pt)
  font.setBold(bold)
  label.setFont(font)
  return label

def buttonWidget(text, func, pt=0):
  button = QtWidgets.QPushButton(text)
  button.setDefault(True)
  button.clicked.connect(func)
  if (pt > 0):
    font = button.font()
    font.setPointSize(pt)
    button.setFont(font)
  return button

class FileSelect(QtWidgets.QWidget):
  def __init__(self, charaFunc, dirCallback):
    super().__init__()
    layout = QtWidgets.QGridLayout()

    nameLabel = textWidget(
      "Touhou Labyrinth 1 Character Save Editor\nv1.0.0", 26, True
    )
    layout.addWidget(nameLabel, 1, 0, 1, 4)

    dirFunc = (lambda c=False: self.getDir(dirCallback))
    fileButton = buttonWidget(
      "Select a directory with a save file", dirFunc, 16
    )
    layout.addWidget(fileButton, 4, 1, 1, 2)

    self.pathLabel = textWidget("Directory selected: none", 14, False)
    layout.addWidget(self.pathLabel, 5, 0, 1, 4)

    startFunc = (lambda c=False: self.readDir() and charaFunc())
    self.startButton = buttonWidget("Use this save file", startFunc, 16)
    self.startButton.setEnabled(False)
    layout.addWidget(self.startButton, 8, 1, 1, 2)

    for i in range(10):
      layout.setRowStretch(i, 1)
    for i in range(4):
      layout.setColumnStretch(i, 1)

    self.setLayout(layout)

  def getDir(self, dirFunc):
    self.fullPath = dirFunc()
    result = "Directory selected: "
    result += self.fullPath
    try:
      self.readDir()
      self.startButton.setEnabled(True)
    except Exception as e:
      print(e)
      result += "\nError! Did not find a valid save file in directory."
      self.startButton.setEnabled(False)
    self.pathLabel.setText(result)

  def readDir(self):
    for i, character in enumerate(characters):
      pad = '0' if (i < 10) else ''
      fname = pad + str(i)
      with open(self.fullPath+"/C"+fname+".ngd", 'rb') as f:
        character.loadSave(f)
    return True

class CharaSelect(QtWidgets.QWidget):
  def __init__(self, backFunc, charaFunc):
    super().__init__()
    layout = QtWidgets.QGridLayout()

    for i, character in enumerate(characters):
      button = QtWidgets.QPushButton()
      fname = "img/Chara_" + character.filename + "_LFace.png"
      image = QtGui.QPixmap(fname)
      icon = QtGui.QIcon(image)
      button.setDefault(True)
      button.setIcon(icon)
      button.setIconSize(image.rect().size())
      layout.addWidget(button, i/8, i%8, 1, 1)
      button.clicked.connect(
        lambda c=False, name=character.name: charaFunc(name)
      )

    backCallback = (lambda c=False: backFunc())
    backButton = buttonWidget("Back to Save Select", backCallback)
    layout.addWidget(backButton, 5, 3, 1, 2)

    self.setLayout(layout)

class TextInput(QtWidgets.QWidget):
  def __init__(self, text, value, callback):
    super().__init__()
    layout = QtWidgets.QGridLayout()
    label = textWidget(text, 12, True)
    label.setAlignment(QtCore.Qt.AlignRight)
    layout.addWidget(label, 0, 0, 1, 1)
    self.edit = QtWidgets.QLineEdit()
    self.edit.setText(value)
    self.edit.textChanged.connect(lambda x: callback(x))
    self.edit.textEdited.connect(lambda x: callback(x))
    layout.addWidget(self.edit, 0, 1, 1, 1)
    self.setLayout(layout)

  def setText(self, text):
    self.edit.setText(text)

class BonusInput(QtWidgets.QWidget):
  def __init__(self, text, value, stat, callback):
    super().__init__()
    layout = QtWidgets.QGridLayout()
    self.label = textWidget(text, 12, False)
    self.label.setAlignment(QtCore.Qt.AlignLeft)
    layout.addWidget(self.label, 0, 1, 1, 1)
    self.edit = QtWidgets.QLineEdit()
    self.edit.setText(value)
    self.edit.setAlignment(QtCore.Qt.AlignRight)
    self.edit.textChanged.connect(lambda x, s=stat: callback(x, stat))
    self.edit.textEdited.connect(lambda x, s=stat: callback(x, stat))
    layout.addWidget(self.edit, 0, 0, 1, 1)
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 1)
    self.setLayout(layout)

  def setText(self, text):
    self.edit.setText(text)

  def setLabel(self, text, sheet):
    self.label.setText(text)
    self.label.setStyleSheet(sheet)

class CharaStats(QtWidgets.QWidget):
  def validateTwoBytes(self, text, minimum=0):
    result = ""
    for c in text[:5]:
      if c in "0123456789":
        result += c
    if (result == "" or int(result) < minimum):
      result = str(minimum)
    if (int(result) > 32767):
      result = "32767"
    result = str(int(result)) # Remove leading zeros
    return result

  def validateLevel(self, text):
    result = self.validateTwoBytes(text, 1)
    self.edited.level = int(result)
    self.updateStats()
    if (result != text):
      self.level.setText(result)

  def validateBP(self, text):
    result = self.validateTwoBytes(text)
    self.edited.bp = int(result)
    if (result != text):
      self.bp.setText(result)

  def validateEXP(self, text):
    result = ""
    for c in text[:10]:
      if c in "0123456789":
        result += c
    if (result == ""):
      result = "0"
    if (int(result) > 2147483647):
      result = "2147483647"
    result = str(int(result)) # Remove leading zeros
    self.edited.exp = int(result)
    if (result != text):
      self.exp.setText(result)

  def validateBonus(self, text, stat):
    result = self.validateTwoBytes(text)
    self.edited.bonus[stat] = int(result)
    self.updateStats()
    if (result != text):
      self.bonus[stat].setText(result)
    diff, sheet = self.createDiffInfo(int(result), self.character.bonus[stat])
    self.bonus[stat].setLabel(diff, sheet)

  def validateLibrary(self, text, stat):
    result = self.validateTwoBytes(text, 1)
    self.edited.skills[stat] = int(result) - 1
    self.updateStats()
    if (result != text):
      self.library[stat].setText(result)
    diff, sheet = self.createDiffInfo(
      int(result) - 1, self.character.skills[stat]
    )
    self.library[stat].setLabel(diff, sheet)

  def updateStats(self):
    remaining = str(self.edited.computeRemaining())
    self.remainLabel.setText("Remaining bonus: "+remaining)
    if (int(remaining) < 0):
      self.remainLabel.setStyleSheet("QLabel { color: red; }")
    else:
      self.remainLabel.setStyleSheet("QLabel { color: black; }")
    for stat in self.stats:
      value = self.edited.computeStat(stat)
      diff, sheet = self.createDiffInfo(value, self.character.computeStat(stat))
      newValue = str(value) + " " + diff
      self.stats[stat].setText(newValue)
      self.stats[stat].setStyleSheet(sheet)

  def createDiffInfo(self, new, old):
    diff = new - old
    if (diff > 0):
      return ["(+"+str(diff)+")", "QLabel { color: blue; }"]
    elif (diff < 0):
      return ["("+str(diff)+")", "QLabel { color: red; }"]
    else:
      return ["("+str(diff)+")", "QLabel { color: black; }"]

  def resetChanges(self):
    self.edited = copy.deepcopy(self.character)
    self.level.setText(str(self.edited.level))
    self.bp.setText(str(self.edited.bp))
    self.exp.setText(str(self.edited.exp))
    for stat in self.stats:
      self.bonus[stat].setText(str(self.character.bonus[stat]))
      self.library[stat].setText(str(self.character.skills[stat]+1))

  def __init__(self, name, backFunc, charaFunc, saveFunc):
    super().__init__()
    self.character = next((c for c in characters if c.name == name))
    self.edited = copy.deepcopy(self.character)
    layout = QtWidgets.QGridLayout()

    nameLabel = textWidget(name, 26, True)
    layout.addWidget(nameLabel, 0, 0, 1, 15)

    level = str(self.character.level)
    self.level = TextInput("Level:", level, self.validateLevel)
    layout.addWidget(self.level, 2, 0, 1, 2)

    exp = str(self.character.exp)
    self.exp = TextInput("EXP:", exp, self.validateEXP)
    layout.addWidget(self.exp, 2, 2, 1, 2)

    bp = str(self.character.bp)
    self.bp = TextInput("BP:", bp, self.validateBP)
    layout.addWidget(self.bp, 2, 4, 1, 2)

    statsLabel = textWidget("Stat Value", 14, True)
    layout.addWidget(statsLabel, 2, 6, 1, 3)

    statsLabel = textWidget("Level Bonus", 14, True)
    layout.addWidget(statsLabel, 2, 9, 1, 3)

    statsLabel = textWidget("Library Level", 14, True)
    layout.addWidget(statsLabel, 2, 12, 1, 3)

    fname = "img/Chara_" + self.character.filename + "_Stand.png"
    image = QtGui.QPixmap(fname)
    imageLabel = QtWidgets.QLabel()
    imageLabel.setPixmap(image)
    imageLabel.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(imageLabel, 3, 0, 12, 5)

    stats = ["hp", "sp", "atk", "def", "mag", "mnd", "spd"]
    affinities = ["fir", "cld", "wnd", "ntr", "mys", "spi"]

    self.stats = {}
    self.bonus = {}
    self.library = {}
    for i, stat in enumerate(stats+affinities):
      statLabel = textWidget(stat.upper(), 12, True)
      layout.addWidget(statLabel, 3+i, 5, 1, 1)
      value = str(self.character.computeStat(stat))
      statValue = textWidget(value + " (0)", 12, False)
      layout.addWidget(statValue, 3+i, 6, 1, 3)
      self.stats[stat] = statValue
      bonus = str(self.character.bonus[stat])
      bonusValue = BonusInput("(0)", bonus, stat, self.validateBonus)
      layout.addWidget(bonusValue, 3+i, 9, 1, 3)
      self.bonus[stat] = bonusValue
      library = str(self.character.skills[stat] + 1)
      libraryValue = BonusInput("(0)", library, stat, self.validateLibrary)
      layout.addWidget(libraryValue, 3+i, 12, 1, 3)
      self.library[stat] = libraryValue

    remaining = str(self.character.computeRemaining())
    self.remainLabel = textWidget("Remaining bonus: "+remaining, 12, True)
    layout.addWidget(self.remainLabel, 15, 0, 1, 5)

    backCallback = (lambda c=False: backFunc())
    backButton = buttonWidget("Back to Save Select", backCallback)
    layout.addWidget(backButton, 17, 2, 1, 2)

    charaCallback = (lambda c=False: charaFunc())
    charaButton = buttonWidget("Back to Character Select", charaCallback)
    layout.addWidget(charaButton, 17, 5, 1, 2)

    undoCallback = (lambda c=False: self.resetChanges())
    undoButton = buttonWidget("Undo Changes", undoCallback)
    layout.addWidget(undoButton, 17, 8, 1, 2)

    saveCallback = (lambda c=False, name=name: saveFunc(name, self.edited))
    saveButton = buttonWidget("Save This Character", saveCallback)
    layout.addWidget(saveButton, 17, 11, 1, 2)

    for i in range(18):
      layout.setRowStretch(i, 1)
    for i in range(15):
      layout.setColumnStretch(i, 1)
    self.setLayout(layout)

class MainWidget(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.fileSelect = None
    self.charaSelect = None
    self.charaStats = None
    self.layout = QtWidgets.QStackedLayout()
    self.loadSelectScreen()
    self.loadCharaScreen()
    self.setLayout(self.layout)

  def getDirFunc(self):
    dialog = QtWidgets.QFileDialog()
    dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
    dialog.exec()
    self.fullPath = dialog.directory().absolutePath()
    return self.fullPath

  def loadSelectScreen(self):
    if (self.fileSelect):
      self.layout.setCurrentIndex(0)
      return
    self.fileSelect = FileSelect(self.loadCharaScreen, self.getDirFunc)
    self.layout.addWidget(self.fileSelect)

  def loadCharaScreen(self):
    if (self.charaSelect):
      self.layout.setCurrentIndex(1)
      return
    self.charaSelect = CharaSelect(
      self.loadSelectScreen,
      self.loadCharacter,
    )
    self.layout.addWidget(self.charaSelect)

  def loadCharacter(self, name):
    if (self.charaStats):
      self.layout.removeWidget(self.charaStats)
      self.charaStats = None
    self.charaStats = CharaStats(
      name,
      self.loadSelectScreen,
      self.loadCharaScreen,
      self.saveOneCharacter,
    )
    self.layout.addWidget(self.charaStats)
    self.layout.setCurrentIndex(2)

  def saveOneCharacter(self, name, edited):
    i, character = next(
      ((i, c) for i, c in enumerate(characters) if c.name == name)
    )
    print(edited.level)
    character = copy.deepcopy(edited)
    pad = '0' if (i < 10) else ''
    paddedIndex = pad + str(i)
    with open(self.fullPath+"/C"+paddedIndex+".ngd", 'wb') as f:
      try:
        character.saveSave(f)
        print("Saved successfully!")
      except OverflowError as e:
        print("Some of the stats overflowed! Please revise your settings!")

if __name__ == "__main__":
  app = QtWidgets.QApplication([])
  widget = MainWidget()
  widget.show()
  sys.exit(app.exec_())
