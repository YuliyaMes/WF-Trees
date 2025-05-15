
"""###Import библиотек"""

import time
import json
import pymorphy3

"""###Класс Word - слово из группы родственных слов"""

"""####Вспомогательные списки морфов для определения свойств слов"""

# суффиксы уменьшительно-ласкательных существительных
diminutive_nouns_suffs = ['еньк', 'оньк', 'ик', 'ек', 'к', 'ок', 'ец', 'иц', 'очк', 'ечк', 'ышк', 'ишк', 'ушк', 'юшк']
# суффиксы увеличительных существительных
magnifying_nouns_suffs = ['ищ', 'ин']
# суффиксы отвлечённых существительных
abstract_nouns_suffs = ['ость', 'ств', 'от', 'ени']
# суффиксы существительных, обозначающих названия лиц по действию
nouns_persons_by_action_suffs = ['тель', 'чик', 'ист']
# суффиксы уменьшительно-ласкательных прилагательных
diminutive_adjectives_suffs = ['еньк', 'оньк']
# суффиксы увеличительных прилагательных
magnifying_adjectives_suffs = ['ущ', 'ющ']
# суффиксы глаголов, обозначающих однократное действие
single_action_verbs_suffs = ['ну']
# суффиксы глаголов, обозначающих многократное действие
repeated_action_verbs_suffs = ['ива', 'ыва']
# приставки отрицания
negative_prefs = ['не', 'анти', 'недо']
# постфиксы возвратных глаголов, причастий и деепричастий
reflexive_postfix = ['ся', 'сь']
# интерфиксы глаголов
infixes = ['а', 'я', 'е', 'и', 'о']
# формообразующие суффиксы инфинитивов
form_suffs = ['ти', 'ть', 'чь']

suff_ant = {   #(часть речи производящего, часть речи производного): [допустимые суффиксы]
     ("ADJ","NOUN"): ['ив','тель','етель','итет','от','об','иль','ил','ач','яч','як','олаг','яг','яж','овь'],
     ("NOUN","NOUN"): ['ость','есть','ств','еств','к','ниц','щиц','ш','чиц','ын','ис','есс','арш','ышн',
          'ик','ок','ен','чик','очк','оч','ек','ушк','ечк','ыш','ул','уль','ишк','еж','ус',
          'иш','уш','енок','енк','онк','юш','юк','ах','еш','чонок','чук','ех','яшк','енц',
          'янк','чак','ин','ец','анин','ай','ист','ат','ан','ант','анд','он','еон','еч',
          'изм','азм','изн','езн','щик','щин','атор','ятор','ищ','ущ','енищ','ур','ер','ор',
          'арь','ырь','арн','иар','нич','няк','чин','ав','явк','ад','адь','ак','ань','ариан',
          'ас','оз','оид','екс','ио','мент','олог','отек','инк','их','еньк'],
     ("VERB","NOUN"): ['ани','ени','яни','ань','и','аци','ни','яци','уци','юци',
                       'ов','овл','ун','унь','ень','ент','отн','янт','ыш','овк','щик','щиц'],
     ("NOUN","VERB"): ['ир','из','изир','ств','еств','ествл','нич','нича'],
     ("ADJ","VERB"): ['ня','ни','не','ове','ови','ате','ати','ащи','аща'],
     ("VERB","VERB"): ['ну','ану','ва','ов','ова','ыва','ива','ева','ава'],
     ("NOUN","ADJ"): ['н','енн','ен','онн','ян','ин','инн','як','ок','вян','ич',
                      'оч','еч','яч','ач','иш','яж','ем','ент','ист','аль','ов',
                      'ев','ав','иль','чат','еб','об','ецк','ниц','ицк','ий','овит'],
     ("ADJ","ADJ"): ['ств','ск','еск','нич','оват','ес','еньк','юсеньк','ост','аст',
                     'айш','ейш','лив','ляв','люж','уч','няц','яц','сив','оньк','еньк','вит','ат'],
     ("VERB","ADJ"): ['ющ','ящ','нн','ущ','вш','ш','тель','ельн','ыва','ыв','абель','ив','чив']
 }

"""#### Вспомогательные функции классификации"""

def search_pos(word, morph):
    all_poses = []
    tmp = morph.parse(word)
    for elem in tmp:
        all_poses.append(elem.tag.POS)
    if len(all_poses)>3: all_poses = all_poses[:3]
    if ("PRTF" in all_poses) or ("PRTS" in all_poses):
        # причастие
        return "PARTICIPLE"
    if "NUMR" in all_poses:
        # числительное
        return "NUMR"
    if "GRND" in all_poses:
        # деепричастие
        return "ADV PARTICIPLE"
    if ("ADJF" in all_poses) or ("ADJS" in all_poses):
        # прилагательное
        return "ADJ"
    if "NOUN" in all_poses:
        # существительное
        return "NOUN"
    if ("INFN" in all_poses) or ("VERB" in all_poses):
        # глагол
        return "VERB"
    # наречие в остальных случаях
    return "ADVERB"

pos_priority = {}
pos_priority["VERB"] = 1
pos_priority["NOUN"] = 2
pos_priority["ADJ"] = 3
pos_priority["PARTICIPLE"] = 3
pos_priority["ADVERB"] = 4
pos_priority["ADV PARTICIPLE"] = 4
pos_priority["NUMR"] = 5

def word_type(word):
    # уменьшительно-ласкательные существительные
    if (word.pos == 'NOUN') and (len(set(word.suff).intersection(diminutive_nouns_suffs)) > 0): return 'min_noun'
    # увеличительные существительные
    elif (word.pos == 'NOUN') and (len(set(word.suff).intersection(magnifying_nouns_suffs)) > 0): return 'max_noun'
    # уменьшительно-ласкательные прилагательные
    elif (word.pos == 'ADJ') and (len(set(word.suff).intersection(diminutive_adjectives_suffs)) > 0): return 'min_adj'
    # увеличительные прилагательные
    elif (word.pos == 'ADJ') and (len(set(word.suff).intersection(magnifying_adjectives_suffs)) > 0): return 'max_adj'
    # возвратные глаголы
    elif (word.pos == 'VERB') and (len(set(word.postfix).intersection(reflexive_postfix)) > 0): return 'reflex_verb'
    # возвратные деепричастия
    elif (word.pos == 'ADV PARTICIPLE') and (len(set(word.postfix).intersection(reflexive_postfix)) > 0): return 'reflex_adv_part'
    # возвратные причастия
    elif (word.pos == 'PARTICIPLE') and (len(set(word.postfix).intersection(reflexive_postfix)) > 0): return 'reflex_part'
    # глаголы несовершенного вида
    elif (word.pos == 'VERB') and (Word.MorphAnalyzer.parse(word.text)[0].tag.aspect == "impf"): return 'impf_verb'
    # глаголы, обозначающие однократное действие
    elif (word.pos == 'VERB') and (len(set(word.suff).intersection(single_action_verbs_suffs)) > 0): return 'single_act_verb'
    # глаголы, обозначающие многократное действие
    elif (word.pos == 'VERB') and (len(set(word.suff).intersection(repeated_action_verbs_suffs)) > 0): return 'rep_act_verb'
    # отвлечённые существительные
    elif (word.pos == 'NOUN') and (len(set(word.suff).intersection(abstract_nouns_suffs)) > 0): return 'abstract_noun'
    # существительные, обозначающие названия лиц по действию)
    elif (word.pos == 'NOUN') and (len(set(word.suff).intersection(nouns_persons_by_action_suffs)) > 0): return 'pers_act_noun'
    # существительные с префиксами отрицания
    elif (word.pos == 'NOUN') and (len(word.pref) > 0) and (word.pref[0] in negative_prefs): return 'no_noun'
    # прилагательные с префиксами отрицания
    elif (word.pos == 'ADJ') and (len(word.pref) > 0) and (word.pref[0] in negative_prefs): return 'no_adj'
    # глаголы с префиксами отрицания
    elif (word.pos == 'VERB') and (len(word.pref) > 0) and (word.pref[0] in negative_prefs): return 'no_verb'
    # деепричастия с префиксами отрицания
    elif (word.pos == 'ADV PARTICIPLE') and (len(word.pref) > 0) and (word.pref[0] in negative_prefs): return 'no_adv_part'
    # причастия с префиксами отрицания
    elif (word.pos == 'PARTICIPLE') and (len(word.pref) > 0) and (word.pref[0] in negative_prefs): return 'no_part'
    else: return 'other'

"""#### Класс Word"""

class Affix(str):
    # Список групп алломорфов (можно задать при создании класса или изменить позже)
    allom_groups = [
        ['оч','ок','к','еч','ч','ек'],
        ['енок','еноч'],
        ['ел','л'],
        ['ник','нич'],
        ['щик','щиц'],
        ['ец','ц'],
        ['ен','енн','ени'],
        ['як','яч'],
        ['ик','ич'],
        ['ова','ов'],
        ['раз','роз'],
        ['ушк','уш'],
        ['ак','ач'],
        ['юк','юч']
    ]

    _allom_map = {}

    @classmethod
    def _rebuild_allom_map(cls):
        cls._allom_map = {}
        for group in cls.allom_groups:
            group_set = frozenset(group)
            for item in group:
                cls._allom_map[item] = group_set

    @classmethod
    def add_allomorphes(cls, groups):
        cls.allom_groups.extend(groups)
        cls._rebuild_allom_map()


    def __new__(cls, value):
        instance = super().__new__(cls, value)
        cls._rebuild_allom_map()
        return instance

    def __eq__(self, other):
        if not isinstance(other, (str, Affix)):
            return NotImplemented

        if super().__eq__(other):
            return True

        self_str = str(self)
        other_str = str(other)

        return (self_str in self._allom_map and
                other_str in self._allom_map and
                self._allom_map[self_str] == self._allom_map[other_str])

    def __hash__(self):
        self_str = str(self)
        if self_str in self._allom_map:
            return hash(tuple(sorted(self._allom_map[self_str])))
        return super().__hash__()

    def __repr__(self):
        return f"Affix('{str(self)}')"

class Word:
  MorphAnalyzer = pymorphy3.MorphAnalyzer()

  def __init__(self, string):
    self.string = string
    #выделяем морфемы в слове и записываем в text слово без обозначений морфов
    self.pref = []
    self.suff = []
    self.root = []
    self.postfix = []
    self.text = ''
    self.morph_spl = ''

    temp = string.split("/")
    for morph in temp:
        morph_split = morph.split(":")
        self.text += morph_split[0]
        self.morph_spl += morph_split[0] + '-'
        if "PREF" in morph_split[1]:
            self.pref.append(Affix(morph_split[0]))
        if "ROOT" in morph_split[1]:
            self.root.append(morph_split[0])
        if "SUFF" in morph_split[1]:
            self.suff.append(Affix(morph_split[0]))
        if "POSTFIX" in morph_split[1]:
            self.postfix.append(morph_split[0])

    self.morph_spl = self.morph_spl[:-1]

    #задаем часть речи
    self.pos = search_pos(self.text, self.MorphAnalyzer)
    #приоритет части речи при выделении вершины дерева
    self.pos_priority = pos_priority[self.pos]

    self.infix = []
    #не учитываем формообразующие суффиксы у глаголов и последние в слове инфиксы, мягкий знак на конце суффикса
    to_delete = -1
    for i in range(0, (len(self.suff) - 1 if self.pos == 'ADVERB' else len(self.suff))):
      if (self.suff[i] in infixes) and (i != len(self.suff) - 1): to_delete = i
    if to_delete >= 0:
      self.infix.append(self.suff[to_delete])
      del self.suff[to_delete]
    if (self.pos == 'VERB') and (self.suff[-1] in form_suffs): del self.suff[len(self.suff)-1]
    for i in range(0, len(self.suff)):
      if self.suff[i][-1] == 'ь': self.suff[i] = self.suff[i][:-1]

    #количество букв в слове
    self.len = len(self.text.replace("-", "").replace("ь", "").replace("ъ", ""))
    #количество морфем в слове
    self.morph_len = len(self.pref) + len(self.root) + len(self.suff) + len(self.postfix)

    #Тип слова по части речи и образующим аффиксам
    self.word_type = word_type(self)

    #Для того, чтобы объекты класса могли служить узлами дерева, добавляем список дочерних вершин
    self.children = []

    self.alternation = 0

  def __eq__(self, other):
        if not isinstance(other, Word):
            return False
        return self.text == other.text

  def __str__(self) -> str:
    return self.morph_spl

  def __repr__(self):
    return self.morph_spl

  def to_string(self, space, string_type = ''):
    if string_type == 'morph-classified':
      s = space + self.string + "\n"
      for child in self.children:
        s += child.to_string(space + '        ', 'morph-classified')
    elif string_type == 'not-divided':
      s = space + self.text + "\n"
      for child in self.children:
        s += child.to_string(space + '    ', 'not-divided')
    else:
      s = space + self.morph_spl + "\n"
      for child in self.children:
        s += child.to_string(space + '    ', '')

    return s

"""#### Признаки словообразовательной связи"""

def diff_1_suff(p, c):
  p_s = set(p.suff)
  c_s = set(c.suff)

  if (p.pref == c.pref) and (p.postfix == c.postfix) and (len(p_s - c_s) == 0) and (len(c_s - p_s) <= 1) and ((p.infix == [])or(c.infix == [])or(p.infix == c.infix)):
    if (len(c_s - p_s) == 1) and ((p.pos, c.pos) in suff_ant.keys()) and ((c_s - p_s).pop() not in suff_ant[(p.pos, c.pos)]): return None
    if p.alternation == 1:
      if (p.root != c.root): return None
      else: c.alternation = 1
    else:
      if (p.root != c.root): c.alternation = 1
    return True
  else: return None

def diff_1_pref(p, c):
  if (len(c.pref) > 0) and ((p.pref == c.pref[1:]) or (p.pref == c.pref)) and (p.postfix == c.postfix) and (p.suff == c.suff) and ((p.infix == [])or(c.infix == [])or(p.infix == c.infix)):
    if p.alternation == 1:
      if (p.root != c.root): return None
      else: c.alternation = 1
    else:
      if (p.root != c.root): c.alternation = 1
    return True
  else: return None

def diff_1_postfix(p, c):
  if (p.pref == c.pref) and (p.postfix == c.postfix[:-1]) and (p.suff == c.suff) and (p.root == c.root) and ((p.infix == [])or(c.infix == [])or(p.infix == c.infix)):
    if p.alternation == 1: c.alternation = 1
    return True
  else: return None

def diff_2_lite(parent, candidate):
  d = 0
  p = set(parent.suff)
  c = set(candidate.suff)

  if (len(candidate.pref) > 0) and (parent.pref == candidate.pref[1:]): d += 1
  elif parent.pref != candidate.pref:
    return None

  if (p < c) and (len(c - p) == 1): d += 1
  elif parent.suff != candidate.suff:
    return None

  if (len(candidate.postfix) > 0) and (parent.postfix == candidate.postfix[:-1]): d += 1
  elif parent.postfix != candidate.postfix:
    return None

  if d <= 2:
    if parent.alternation == 1: candidate.alternation = 1
    if (parent.root != candidate.root): candidate.alternation = 1
    return True
  return None

def diff_2(p, c):
  if diff_2_lite(p, c) and ((p.infix == [])or(c.infix == [])or(p.infix == c.infix)) and ((p.pos == 'VERB') or (c.pos != 'VERB')):
    if p.alternation == 1:
      if (p.root != c.root):
        c.alternation = 0
        return None
      else: c.alternation = 1
    else:
      if (p.root != c.root): c.alternation = 1
    return True
  else:
    c.alternation = 0
    return None
