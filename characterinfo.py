from itemmultipliers import equipmentMultipliers as equipMultipliers

levelMultiplier = {
  'hp': 3, 'sp': 0, 'atk': 2, 'def': 2, 'mag': 2, 'mnd': 2, 'spd': 2
}

statOrder = [
  'hp', 'sp', 'tp', 'atk', 'def', 'mag', 'mnd', 'spd', 'eva',
  'fir', 'cld', 'wnd', 'ntr', 'mys', 'spi'
]

def readAsInteger(f, nbytes):
  data = f.read(nbytes)
  result = 0
  for i, c in enumerate(data):
    power = nbytes - i - 1
    result += (256**power) * c
  return result

class Character:
  def __init__(self, name, growths, affinities):
    self.name = name
    self.filename = name
    if (name == "Meiling"): self.filename = "Meirin"
    elif (name == "Tenshi"): self.filename = "Tenko"
    elif (name == "Reisen"): self.filename = "Udonge"
    elif (name == "Rinnosuke"): self.filename = "KourinB"
    elif (name == "Maribel"): self.filename = "MaribelB"
    elif (name == "Shikieiki"): self.filename = "Eiki"
    self.growths = growths
    self.affinities = affinities
    self.computeMap = {
      "hp": self.computeHP,
      "sp": self.computeSP,
      "atk": self.computeATK,
      "def": self.computeDEF,
      "mag": self.computeMAG,
      "mnd": self.computeMND,
      "spd": self.computeSPD,
    }

  def computeStat(self, stat):
    if (stat in self.computeMap):
      return self.computeMap[stat]()
    return self.computeAffinity(stat)

  def computeHP(self):
    mult = self.computeMultiplier('hp')
    return int((((self.level + 6) * self.growths['hp']) + 12) * mult / 100)

  def computeSP(self):
    mult = self.computeMultiplier('sp')
    return int(((self.level * self.growths['sp'] / 8) + 100) * mult / 100)

  def computeATK(self):
    mult = self.computeMultiplier('atk')
    return int((((self.level + 4) * self.growths['atk']) + 3) * mult / 100)

  def computeDEF(self):
    mult = self.computeMultiplier('def')
    return int((((self.level + 4) * self.growths['def']) + 1) * mult / 100)

  def computeMAG(self):
    mult = self.computeMultiplier('mag')
    return int((((self.level + 4) * self.growths['mag']) + 2) * mult / 100)

  def computeMND(self):
    mult = self.computeMultiplier('mnd')
    return int((((self.level + 4) * self.growths['mnd']) + 1) * mult / 100)

  def computeSPD(self):
    mult = self.computeMultiplier('spd')
    return int((self.level * self.growths['spd'] / 32) * mult / 100) + 100

  def computeAffinity(self, name):
    base = self.affinities[name]
    equips = 0
    for i in range(3):
      if (self.equips[i] < 150 and name in equipMultipliers[self.equips[i]]):
        equips += equipMultipliers[self.equips[i]][name]
    return base + equips + (2 * self.bonus[name]) + (3 * self.skills[name])

  def computeMultiplier(self, stat):
    base = 100 if (self.name != 'Remilia' or stat != 'atk') else 84
    base += (self.level - 1) * levelMultiplier[stat]
    base += self.bonus[stat] * (2 if stat != 'sp' else 1)
    base += self.skills[stat] * (4 if stat != 'sp' else 1)
    for i in range(3):
      if (self.equips[i] < 150 and stat in equipMultipliers[self.equips[i]]):
        base += equipMultipliers[self.equips[i]][stat]
    return base

  def reverseStatBonus(self, multiplier, stat):
    base = 100 if (self.name != 'Remilia' or stat != 'atk') else 84
    base += (self.level - 1) * levelMultiplier[stat]
    base += self.skills[stat] * (4 if stat != 'sp' else 1)
    for i in range(3):
      if (self.equips[i] < 150 and stat in equipMultipliers[self.equips[i]]):
        base += equipMultipliers[self.equips[i]][stat]
    divider = 2 if (stat != 'sp') else 1
    return int((multiplier - base) / divider)

  def reverseAffinityBonus(self, multiplier, name):
    result = multiplier
    result -= self.affinities[name]
    result -= (3 * self.skills[name])
    for i in range(3):
      if (self.equips[i] < 150 and name in equipMultipliers[self.equips[i]]):
        result -= equipMultipliers[self.equips[i]][name]
    return int(result / 2)

  def loadSave(self, data):
    self.level = readAsInteger(data, 2)
    self.exp = readAsInteger(data, 4)
    self.tp = readAsInteger(data, 1)
    multipliers = [readAsInteger(data, 2) for i in range(8)]
    self.evaMultiplier = multipliers[5]
    affinities = [readAsInteger(data, 2) for i in range(6)]
    skills = [readAsInteger(data, 2) for i in range(15)]
    self.garbage = data.read(8)
    self.bp = readAsInteger(data, 2)
    self.sprec = readAsInteger(data, 1)
    self.resistances = data.read(5)
    self.equips = [readAsInteger(data, 1) for i in range(3)]
    self.skills = {}
    for i, s in enumerate(statOrder):
      self.skills[s] = skills[i] - 1
    self.bonus = {
      'hp': self.reverseStatBonus(multipliers[6], 'hp'),
      'sp': self.reverseStatBonus(multipliers[7], 'sp'),
      'atk': self.reverseStatBonus(multipliers[0], 'atk'),
      'def': self.reverseStatBonus(multipliers[1], 'def'),
      'mag': self.reverseStatBonus(multipliers[2], 'mag'),
      'mnd': self.reverseStatBonus(multipliers[3], 'mnd'),
      'spd': self.reverseStatBonus(multipliers[4], 'spd'),
      'fir': self.reverseAffinityBonus(affinities[0], 'fir'),
      'cld': self.reverseAffinityBonus(affinities[1], 'cld'),
      'wnd': self.reverseAffinityBonus(affinities[2], 'wnd'),
      'ntr': self.reverseAffinityBonus(affinities[3], 'ntr'),
      'mys': self.reverseAffinityBonus(affinities[4], 'mys'),
      'spi': self.reverseAffinityBonus(affinities[5], 'spi')
    }

  def saveSave(self, data):
    data.write(self.level.to_bytes(2, 'big'))
    data.write(self.exp.to_bytes(4, 'big'))
    data.write(self.tp.to_bytes(1, 'big'))
    multipliers = [
      self.computeMultiplier('atk'),
      self.computeMultiplier('def'),
      self.computeMultiplier('mag'),
      self.computeMultiplier('mnd'),
      self.computeMultiplier('spd'),
      self.evaMultiplier,
      self.computeMultiplier('hp'),
      self.computeMultiplier('sp'),
    ]
    for m in multipliers:
      data.write(m.to_bytes(2, 'big'))
    affinities = [
      self.computeAffinity('fir'),
      self.computeAffinity('cld'),
      self.computeAffinity('wnd'),
      self.computeAffinity('ntr'),
      self.computeAffinity('mys'),
      self.computeAffinity('spi'),
    ]
    for a in affinities:
      data.write(a.to_bytes(2, 'big'))
    for s in statOrder:
      data.write((self.skills[s] + 1).to_bytes(2, 'big'))
    data.write(self.garbage)
    data.write(self.bp.to_bytes(2, 'big'))
    data.write(self.sprec.to_bytes(1, 'big'))
    data.write(self.resistances)
    for e in self.equips:
      data.write(e.to_bytes(1, 'big'))

  def computeRemaining(self):
    remaining = self.level - 1
    for stat in self.bonus:
      remaining -= self.bonus[stat]
    return remaining

  def exportAsString(self):
    result = "===== {} =====\n".format(self.name)
    result += "Level: {}\n".format(self.level)
    result += "EXP: {}\n".format(self.exp)
    result += "BP: {}\n".format(self.bp)
    result += "Bonus HP: {}\n".format(self.bonus['hp'])
    result += "Bonus SP: {}\n".format(self.bonus['sp'])
    result += "Bonus ATK: {}\n".format(self.bonus['atk'])
    result += "Bonus DEF: {}\n".format(self.bonus['def'])
    result += "Bonus MAG: {}\n".format(self.bonus['mag'])
    result += "Bonus MND: {}\n".format(self.bonus['mnd'])
    result += "Bonus SPD: {}\n".format(self.bonus['spd'])
    result += "Bonus FIR: {}\n".format(self.bonus['fir'])
    result += "Bonus CLD: {}\n".format(self.bonus['cld'])
    result += "Bonus WND: {}\n".format(self.bonus['wnd'])
    result += "Bonus NTR: {}\n".format(self.bonus['ntr'])
    result += "Bonus MYS: {}\n".format(self.bonus['mys'])
    result += "Bonus SPI: {}\n".format(self.bonus['spi'])
    result += "Library HP: {}\n".format(self.skills['hp'] + 1)
    result += "Library SP: {}\n".format(self.skills['sp'] + 1)
    result += "Library ATK: {}\n".format(self.skills['atk'] + 1)
    result += "Library DEF: {}\n".format(self.skills['def'] + 1)
    result += "Library MAG: {}\n".format(self.skills['mag'] + 1)
    result += "Library MND: {}\n".format(self.skills['mnd'] + 1)
    result += "Library SPD: {}\n".format(self.skills['spd'] + 1)
    result += "Library FIR: {}\n".format(self.skills['fir'] + 1)
    result += "Library CLD: {}\n".format(self.skills['cld'] + 1)
    result += "Library WND: {}\n".format(self.skills['wnd'] + 1)
    result += "Library NTR: {}\n".format(self.skills['ntr'] + 1)
    result += "Library MYS: {}\n".format(self.skills['mys'] + 1)
    result += "Library SPI: {}\n".format(self.skills['spi'] + 1)
    result += "Equip 1: {}\n".format(self.equips[0])
    result += "Equip 2: {}\n".format(self.equips[1])
    result += "Equip 3: {}\n".format(self.equips[2])
    return result

characterArray = [
  Character(
    'Reimu',
    {'hp': 12, 'sp': 20, 'atk': 8, 'def': 6, 'mag': 9, 'mnd': 9, 'spd': 8},
    {'fir': 110, 'cld': 106, 'wnd': 114, 'ntr': 105, 'mys': 77, 'spi': 148}
  ),
  Character(
    'Marisa',
    {'hp': 9, 'sp': 26, 'atk': 3, 'def': 5, 'mag': 13, 'mnd': 12, 'spd': 11},
    {'fir': 89, 'cld': 95, 'wnd': 96, 'ntr': 93, 'mys': 167, 'spi': 144}
  ),
  Character(
    'Remilia',
    {'hp': 19, 'sp': 8, 'atk': 16, 'def': 10, 'mag': 4, 'mnd': 9, 'spd': 12},
    {'fir': 121, 'cld': 122, 'wnd': 128, 'ntr': 125, 'mys': 96, 'spi': 77}
  ),
  Character(
    'Sakuya',
    {'hp': 15, 'sp': 14, 'atk': 11, 'def': 8, 'mag': 5, 'mnd': 7, 'spd': 10},
    {'fir': 110, 'cld': 110, 'wnd': 110, 'ntr': 110, 'mys': 110, 'spi': 110}
  ),
  Character(
    'Patchouli',
    {'hp': 6, 'sp': 30, 'atk': 2, 'def': 2, 'mag': 16, 'mnd': 17, 'spd': 5},
    {'fir': 132, 'cld': 136, 'wnd': 138, 'ntr': 134, 'mys': 173, 'spi': 102}
  ),
  Character(
    'Chen',
    {'hp': 8, 'sp': 5, 'atk': 8, 'def': 4, 'mag': 4, 'mnd': 4, 'spd': 13},
    {'fir': 98, 'cld': 51, 'wnd': 96, 'ntr': 97, 'mys': 105, 'spi': 103}
  ),
  Character(
    'Meiling',
    {'hp': 17, 'sp': 6, 'atk': 7, 'def': 9, 'mag': 4, 'mnd': 6, 'spd': 7},
    {'fir': 136, 'cld': 144, 'wnd': 138, 'ntr': 140, 'mys': 105, 'spi': 103}
  ),
  Character(
    'Cirno',
    {'hp': 11, 'sp': 15, 'atk': 8, 'def': 5, 'mag': 8, 'mnd': 4, 'spd': 9},
    {'fir': 35, 'cld': 176, 'wnd': 114, 'ntr': 105, 'mys': 95, 'spi': 91}
  ),
  Character(
    'Minoriko',
    {'hp': 10, 'sp': 16, 'atk': 3, 'def': 3, 'mag': 8, 'mnd': 9, 'spd': 7},
    {'fir': 50, 'cld': 56, 'wnd': 163, 'ntr': 196, 'mys': 100, 'spi': 104}
  ),
  Character(
    'Youmu',
    {'hp': 16, 'sp': 5, 'atk': 12, 'def': 9, 'mag': 2, 'mnd': 2, 'spd': 7},
    {'fir': 110, 'cld': 106, 'wnd': 114, 'ntr': 105, 'mys': 84, 'spi': 132}
  ),
  Character(
    'Alice',
    {'hp': 12, 'sp': 22, 'atk': 6, 'def': 7, 'mag': 12, 'mnd': 10, 'spd': 8},
    {'fir': 118, 'cld': 114, 'wnd': 117, 'ntr': 113, 'mys': 126, 'spi': 112}
  ),
  Character(
    'Rumia',
    {'hp': 9, 'sp': 16, 'atk': 4, 'def': 5, 'mag': 9, 'mnd': 7, 'spd': 6},
    {'fir': 96, 'cld': 102, 'wnd': 103, 'ntr': 99, 'mys': 192, 'spi': 67}
  ),
  Character(
    'Wriggle',
    {'hp': 14, 'sp': 16, 'atk': 10, 'def': 7, 'mag': 6, 'mnd': 7, 'spd': 8},
    {'fir': 61, 'cld': 73, 'wnd': 145, 'ntr': 157, 'mys': 110, 'spi': 109}
  ),
  Character(
    'Yuugi',
    {'hp': 16, 'sp': 7, 'atk': 17, 'def': 12, 'mag': 1, 'mnd': 3, 'spd': 7},
    {'fir': 138, 'cld': 72, 'wnd': 136, 'ntr': 75, 'mys': 137, 'spi': 73}
  ),
  Character(
    'Aya',
    {'hp': 12, 'sp': 16, 'atk': 13, 'def': 7, 'mag': 6, 'mnd': 6, 'spd': 14},
    {'fir': 102, 'cld': 104, 'wnd': 201, 'ntr': 106, 'mys': 77, 'spi': 80}
  ),
  Character(
    'Iku',
    {'hp': 13, 'sp': 16, 'atk': 6, 'def': 6, 'mag': 11, 'mnd': 11, 'spd': 7},
    {'fir': 114, 'cld': 112, 'wnd': 181, 'ntr': 109, 'mys': 101, 'spi': 102}
  ),
  Character(
    'Komachi',
    {'hp': 28, 'sp': 10, 'atk': 14, 'def': 3, 'mag': 3, 'mnd': 2, 'spd': 8},
    {'fir': 87, 'cld': 82, 'wnd': 84, 'ntr': 90, 'mys': 126, 'spi': 141}
  ),
  Character(
    'Suwako',
    {'hp': 9, 'sp': 11, 'atk': 14, 'def': 6, 'mag': 14, 'mnd': 6, 'spd': 9},
    {'fir': 71, 'cld': 141, 'wnd': 68, 'ntr': 142, 'mys': 102, 'spi': 98}
  ),
  Character(
    'Sanae',
    {'hp': 10, 'sp': 21, 'atk': 4, 'def': 5, 'mag': 12, 'mnd': 8, 'spd': 7},
    {'fir': 123, 'cld': 133, 'wnd': 101, 'ntr': 94, 'mys': 84, 'spi': 146}
  ),
  Character(
    'Nitori',
    {'hp': 11, 'sp': 15, 'atk': 10, 'def': 5, 'mag': 4, 'mnd': 7, 'spd': 8},
    {'fir': 75, 'cld': 169, 'wnd': 113, 'ntr': 167, 'mys': 104, 'spi': 72}
  ),
  Character(
    'Ran',
    {'hp': 14, 'sp': 18, 'atk': 10, 'def': 8, 'mag': 13, 'mnd': 10, 'spd': 10},
    {'fir': 173, 'cld': 66, 'wnd': 165, 'ntr': 170, 'mys': 61, 'spi': 192}
  ),
  Character(
    'Reisen',
    {'hp': 12, 'sp': 16, 'atk': 4, 'def': 6, 'mag': 10, 'mnd': 4, 'spd': 9},
    {'fir': 118, 'cld': 125, 'wnd': 84, 'ntr': 90, 'mys': 198, 'spi': 50}
  ),
  Character(
    'Eirin',
    {'hp': 15, 'sp': 19, 'atk': 9, 'def': 9, 'mag': 13, 'mnd': 10, 'spd': 8},
    {'fir': 147, 'cld': 150, 'wnd': 151, 'ntr': 145, 'mys': 101, 'spi': 168}
  ),
  Character(
    'Tenshi',
    {'hp': 11, 'sp': 14, 'atk': 10, 'def': 12, 'mag': 6, 'mnd': 12, 'spd': 6},
    {'fir': 118, 'cld': 125, 'wnd': 119, 'ntr': 114, 'mys': 126, 'spi': 124}
  ),
  Character(
    'Mokou',
    {'hp': 14, 'sp': 14, 'atk': 4, 'def': 7, 'mag': 12, 'mnd': 7, 'spd': 9},
    {'fir': 176, 'cld': 71, 'wnd': 140, 'ntr': 136, 'mys': 89, 'spi': 92}
  ),
  Character(
    'Flandre',
    {'hp': 16, 'sp': 16, 'atk': 22, 'def': 5, 'mag': 14, 'mnd': 1, 'spd': 11},
    {'fir': 342, 'cld': 28, 'wnd': 61, 'ntr': 54, 'mys': 90, 'spi': 46}
  ),
  Character(
    'Rin',
    {'hp': 10, 'sp': 17, 'atk': 11, 'def': 5, 'mag': 9, 'mnd': 10, 'spd': 11},
    {'fir': 180, 'cld': 52, 'wnd': 102, 'ntr': 60, 'mys': 99, 'spi': 160}
  ),
  Character(
    'Kaguya',
    {'hp': 7, 'sp': 20, 'atk': 4, 'def': 6, 'mag': 14, 'mnd': 11, 'spd': 7},
    {'fir': 149, 'cld': 156, 'wnd': 151, 'ntr': 146, 'mys': 158, 'spi': 155}
  ),
  Character(
    'Suika',
    {'hp': 16, 'sp': 10, 'atk': 16, 'def': 6, 'mag': 6, 'mnd': 10, 'spd': 9},
    {'fir': 69, 'cld': 165, 'wnd': 159, 'ntr': 162, 'mys': 160, 'spi': 60}
  ),
  Character(
    'Yuyuko',
    {'hp': 14, 'sp': 17, 'atk': 4, 'def': 5, 'mag': 12, 'mnd': 13, 'spd': 6},
    {'fir': 73, 'cld': 168, 'wnd': 75, 'ntr': 151, 'mys': 99, 'spi': 234}
  ),
  Character(
    'Yukari',
    {'hp': 14, 'sp': 21, 'atk': 6, 'def': 9, 'mag': 13, 'mnd': 12, 'spd': 7},
    {'fir': 87, 'cld': 144, 'wnd': 149, 'ntr': 143, 'mys': 89, 'spi': 181}
  ),
  Character(
    'Rinnosuke',
    {'hp': 16, 'sp': 16, 'atk': 16, 'def': 10, 'mag': 12, 'mnd': 10, 'spd': 11},
    {'fir': 163, 'cld': 169, 'wnd': 165, 'ntr': 166, 'mys': 167, 'spi': 69}
  ),
  Character(
    'Renko',
    {'hp': 13, 'sp': 11, 'atk': 4, 'def': 6, 'mag': 5, 'mnd': 7, 'spd': 9},
    {'fir': 102, 'cld': 105, 'wnd': 100, 'ntr': 101, 'mys': 107, 'spi': 108}
  ),
  Character(
    'Maribel',
    {'hp': 11, 'sp': 16, 'atk': 7, 'def': 5, 'mag': 11, 'mnd': 8, 'spd': 8},
    {'fir': 78, 'cld': 132, 'wnd': 135, 'ntr': 132, 'mys': 65, 'spi': 156}
  ),
  Character(
    'Utsuho',
    {'hp': 12, 'sp': 15, 'atk': 8, 'def': 8, 'mag': 14, 'mnd': 8, 'spd': 10},
    {'fir': 282, 'cld': 54, 'wnd': 187, 'ntr': 76, 'mys': 186, 'spi': 61}
  ),
  Character(
    'Kanako',
    {'hp': 13, 'sp': 16, 'atk': 8, 'def': 9, 'mag': 13, 'mnd': 9, 'spd': 8},
    {'fir': 112, 'cld': 123, 'wnd': 238, 'ntr': 145, 'mys': 100, 'spi': 126}
  ),
  Character(
    'Yuuka',
    {'hp': 14, 'sp': 14, 'atk': 11, 'def': 10, 'mag': 14, 'mnd': 7, 'spd': 8},
    {'fir': 76, 'cld': 78, 'wnd': 142, 'ntr': 254, 'mys': 176, 'spi': 120}
  ),
  Character(
    'Mystia',
    {'hp': 12, 'sp': 14, 'atk': 10, 'def': 6, 'mag': 4, 'mnd': 6, 'spd': 10},
    {'fir': 90, 'cld': 91, 'wnd': 143, 'ntr': 127, 'mys': 76, 'spi': 88}
  ),
  Character(
    'Keine',
    {'hp': 15, 'sp': 19, 'atk': 11, 'def': 8, 'mag': 7, 'mnd': 7, 'spd': 9},
    {'fir': 133, 'cld': 133, 'wnd': 129, 'ntr': 131, 'mys': 140, 'spi': 139}
  ),
  Character(
    'Shikieiki',
    {'hp': 15, 'sp': 15, 'atk': 14, 'def': 5, 'mag': 14, 'mnd': 10, 'spd': 7},
    {'fir': 108, 'cld': 171, 'wnd': 105, 'ntr': 112, 'mys': 125, 'spi': 169}
  ),
]
