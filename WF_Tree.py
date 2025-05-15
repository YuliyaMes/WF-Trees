
import argparse
import json
import word
import time
import pymorphy3



"""###Nest - группа родственных слов типа Word
При построении дерева - список оставшихся нераспределенных слов

"""

import chardet

def detect_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        return result['encoding']

def Trees_to_file(file, WF_Tree_s, s=''):
  with open(file,'w') as f_out:
    for tree in WF_Tree_s:
      f_out.write(tree.print_tree(s))
      f_out.write('------------------------------------------------------\n')

def Nests_from_file(file):
  if '.txt' in file:
    with open(file,'r', encoding=detect_file_encoding(file)) as f_in:
      data = f_in.readlines()
      Nests = []
      Nest = []
      for line in data:
          if '---' in line:
            Nests.append(Nest)
            Nest = []
          else:
            if '\n' in line:
              line = line.replace('\n', '')
            word = Word(line)
            if not (word.pos == 'NUMR') and not (word in Nest) : Nest.append(word)
  elif '.json' in file:
    with open(file,'r', encoding=detect_file_encoding(file)) as f_in:
      data = json.load(in_file)
      Nests = []
      for group in data:
        Nest = []
        for word in group:
          word = Word(line)
          if not (word.pos == 'NUMR'): Nest.append(word)
        Nests.append(Nest)
  else:
    print('Wrong filename')
    return None
  return Nests

def Verts_from_file(file):
  Verts = []
  if '.txt' in file:
    with open(file,'r', encoding=detect_file_encoding(file)) as f_in:
      data = f_in.readlines()
      for line in data:
        if '\n' in line: line = line.replace('\n', '')
        Verts.append(Word(line))
  return Verts

"""###Класс WF_Tree - словообразовательное дерево
Упорядоченное в виде дерева множество слов и словообразовательных связей между ними

#### children_noun
"""

def children_noun(parent, Nest):
        new_words = []
        # 1. уменьшительно-ласкательные существительные
        candidates = [x for x in Nest if x.word_type == 'min_noun']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. увеличительные существительные
        candidates = [x for x in Nest if x.word_type == 'max_noun']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 3. существительные, образованные только с помощью суффиксов
        candidates = [x for x in Nest if (x.pos == 'NOUN') and not (x in new_words)]
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 4. а) прилагательные, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'ADJ') and (x.word_type != 'no_adj')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 4. б) прилагательные, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if x.word_type == 'no_adj']
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 4. в) остальные прилагательные
        candidates = [x for x in Nest if (x.pos == 'ADJ') and not (x in new_words)]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 5. наречия
        candidates = [x for x in Nest if (x.pos == 'ADVERB')]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 6. а) существительные, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'NOUN') and not (x in new_words) and (x.word_type != 'no_noun')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 6. б) существительные, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if not (x in new_words) and (x.word_type == 'no_noun')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 7. в) остальные глаголы
        candidates = [x for x in Nest if (x.pos == 'VERB') and not (x in new_words)]
        for candidate in candidates:
          if (parent.suff == candidate.suff) and (parent.pref == candidate.pref) and (parent.postfix == candidate.postfix):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # # 7. а) глаголы, образованные только с помощью приставок (кроме НЕ и АНТИ)
        # candidates = [x for x in Nest if (x.pos == 'VERB') and (x.word_type != 'no_verb') and not (x in new_words)]
        # for candidate in candidates:
        #   if diff_1_pref(parent, candidate):
        #     parent.children.append(candidate)
        #     Nest.remove(candidate)
        #     new_words.append(candidate)
        # # 7. б) глаголы, образованные только с помощью приставок НЕ и АНТИ
        # candidates = [x for x in Nest if (x.word_type == 'no_verb') and not (x in new_words)]
        # for candidate in candidates:
        #   if diff_1_pref(parent, candidate):
        #     parent.children.append(candidate)
        #     Nest.remove(candidate)
        #     new_words.append(candidate)
        return new_words

"""#### children_verb"""

def children_verb(parent, Nest):
        new_words = []
        # 6. а) глаголы, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'VERB') and not (x in new_words) and (x.word_type != 'no_verb')]
        candidates = sorted(candidates, key=lambda word: word.text)
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 6. б) глаголы, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if (x.word_type == 'no_verb') and not (x in new_words)]
        candidates = sorted(candidates, key=lambda word: word.text)
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. глаголы несовершенного вида, образованные с помощью суффиксов
        candidates = [x for x in Nest if x.word_type == 'impf_verb']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 3. глаголы, обозначающие однократное действие
        candidates = [x for x in Nest if x.word_type == 'single_act_verb']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 4. глаголы, обозначающие многократное действие
        candidates = [x for x in Nest if x.word_type == 'rep_act_verb']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 5. остальные глаголы, образованные с помощью суффиксов
        candidates = [x for x in Nest if (x.pos == 'VERB') and not (x in new_words)]
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 1. возвратные глаголы
        candidates = [x for x in Nest if (x.word_type == 'reflex_verb') and not (x in new_words)]
        for candidate in candidates:
          if diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 7. причастия
        candidates = [x for x in Nest if x.pos == "PARTICIPLE"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 8. деепричастия
        candidates = [x for x in Nest if x.pos == "ADV PARTICIPLE"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 9. отвлечённые существительные
        candidates = [x for x in Nest if x.word_type == 'abstract_noun']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 10. существительные, обозначающие названия лиц по действию
        candidates = [x for x in Nest if x.word_type == 'pers_act_noun']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 11. остальные существительные
        candidates = [x for x in Nest if (x.pos == 'NOUN') and not (x in new_words)]
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 12. прилагательные
        candidates = [x for x in Nest if x.pos == "ADJ"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 13. наречия
        candidates = [x for x in Nest if x.pos == "ADVERB"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)

        return new_words

"""#### children_adj"""

def children_adj(parent, Nest):
        new_words = []
        # 1. уменьшительно-ласкательные прилагательные
        candidates = [x for x in Nest if x.word_type == 'min_adj']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. увеличительные прилагательные
        candidates = [x for x in Nest if x.word_type == 'max_adj']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 3. прилагательные, образованные только с помощью суффиксов
        candidates = [x for x in Nest if x.pos == 'ADJ']
        for candidate in candidates:
          if diff_1_suff(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 5. а) существительные, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'NOUN') and (x.word_type != 'no_noun')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 5. б) существительные, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if (x.pos == 'NOUN') and (x.word_type == 'no_noun')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 5. в) остальные существительные
        candidates = [x for x in Nest if (x.pos == 'NOUN') and not (x in new_words)]
        for candidate in candidates:
          if diff_1_pref(parent, candidate) or diff_1_suff(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 6. а) прилагательные, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'ADJ') and not (x in new_words) and (x.word_type != 'no_adj')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 6. б) прилагательные, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if (x.pos == 'ADJ') and not (x in new_words) and (x.word_type == 'no_adj')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 7. глаголы
        candidates = [x for x in Nest if x.pos == 'VERB']
        for candidate in candidates:
          if (parent.suff == candidate.suff) and (parent.pref == candidate.pref) and (parent.postfix == candidate.postfix):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 4. наречия
        candidates = [x for x in Nest if x.pos == 'ADVERB']
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        return new_words

"""#### children_adv_part"""

def children_adv_part(parent, Nest):
        new_words = []
        # 1. возвратные деепричастия
        candidates = [x for x in Nest if x.word_type == 'reflex_adv_part']
        for candidate in candidates:
          if diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. а) деепричастия, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'ADV PARTICIPLE') and (x.word_type != 'reflex_adv_part') and (x.word_type != 'no_adv_part')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. б) деепричастия, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if x.word_type != 'no_adv_part']
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        return new_words

"""#### children_part"""

def children_part(parent, Nest):
        new_words = []
        # 1. возвратные причастия
        candidates = [x for x in Nest if x.word_type == 'reflex_part']
        for candidate in candidates:
          if diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. а) причастия, образованные только с помощью приставок (кроме НЕ и АНТИ)
        candidates = [x for x in Nest if (x.pos == 'PARTICIPLE') and (x.word_type != 'reflex_part') and (x.word_type != 'no_part')]
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. б) причастия, образованные только с помощью приставок НЕ и АНТИ
        candidates = [x for x in Nest if x.word_type != 'no_part']
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        return new_words

"""#### children_adverb"""

def children_adverb(parent, Nest):
        new_words = []
        # 1. прилагательные
        candidates = [x for x in Nest if x.pos == "ADJ"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 2. наречия
        candidates = [x for x in Nest if x.pos == "ADVERB"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 3. существительные
        candidates = [x for x in Nest if x.pos == "NOUN"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate) or diff_1_postfix(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        # 4. глаголы
        candidates = [x for x in Nest if x.pos == "VERB"]
        for candidate in candidates:
          if diff_1_suff(parent, candidate) or diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        return new_words

"""#### children_name"""

def children_name(parent, Nest):
        if parent.pos not in ('NOUN', 'ADJ'): return None
        new_words = []
        candidates = [x for x in Nest if x.pos == 'VERB']
        for candidate in candidates:
          if diff_1_pref(parent, candidate):
            parent.children.append(candidate)
            Nest.remove(candidate)
            new_words.append(candidate)
        return new_words

"""#### class WF_Tree"""

# @title
class WF_Tree:
  def __init__(self, Nest, Verts):

    self.vert = None
    for word in Verts:
      if word in Nest:
        self.vert = word  # если вершина задана вручную, то ее и оставляем
        break
    if self.vert is None: # а если не задана, то смотрим на три приоритета
                          # 1) количество морфем
                          # 2) количество букв
                          # 3) часть речи

      self.vert = sorted(Nest,  key=lambda word: (word.morph_len, word.len, word.pos_priority, word.text))[0]

    self.all_words = []
    self.all_words.append(self.vert)
    Nest.remove(self.vert)



  def Add_by_one_morph(self, parent, Nest):
            #здесь присоединяем к слову leaf в дереве wf_tree все,
            #что может быть присоединено через один аффикс
            #Тут же оно удаляется из Nest
    new_words = []

    match parent.pos:
      case 'NOUN':
        new_words = children_noun(parent, Nest)
      case 'VERB':
        new_words = children_verb(parent, Nest)
      case 'ADJ':
        new_words = children_adj(parent, Nest)
      case 'ADVERB':
        new_words = children_adverb(parent, Nest)
      case 'ADV PARTICIPLE':
        new_words = children_adv_part(parent, Nest)
      case 'PARTICIPLE':
        new_words = children_part(parent, Nest)

    #Присоединенные слова в порядке присоединения добавляем в self.all_words
    if new_words:
      for word in new_words: self.all_words.append(word)
    #Функция возвращает список присоединенных слов
    return new_words




  def Add_by_two_morph(self, candidate, s=None):
            #здесь присоединяем одно слово,
            #которое может быть присоединено через два аффикса
            #Тут же оно удаляется из Nest
    parents = [x for x in self.all_words if x.pos in ("NOUN", "ADJ", "VERB")][::-1] #закидываем в список на проверку как производящие все слова в дереве
    if len(parents) > 0:
      #не можем так присоединять возвратные глаголы, странно, проверить
      for parent in parents:
        if diff_2(parent, candidate) or (s and diff_2_lite(parent, candidate)):
          parent.children.append(candidate)
          Nest.remove(candidate)
          self.all_words.append(candidate)
          return candidate #Функция возвращает присоединенное слово
      return None
    else: return None


  def Add_by_name(self, candidates):
    new_words = []
    for candidate in candidates:
      parents = [x for x in self.all_words if x.pos in ("NOUN", "ADJ")][::-1] #закидываем в список на проверку как производящие все слова в дереве
      for parent in parents:
        if diff_1_pref(parent, candidate):
          parent.children.append(candidate)
          Nest.remove(candidate)
          self.all_words.append(candidate)
          new_words.append(candidate)
          break




  def WF_Tree_Construction(self, Nest, vert):
            #Функция возвращает слово, присоединенное на 3 этапе алгоритма,
            #или None, если на 3 этапе присоединить слово не удалось.
            #Если на 3 этапе слов присоединено не было, то в дерево добавлены
            #все слова, образованные при помощи 1-2 аффиксоов

    Leaves = [] #список слов, которые надо рассмотреть как производящие
    Leaves.append(vert) #изначально это только указанная вершина

    while len(Leaves) > 0:
      leaf = Leaves.pop(0)
      #print('2: ', leaf)
      new_words = self.Add_by_one_morph(leaf, Nest)
      if new_words:
        for word in new_words: Leaves.append(word)
            #присоединенные слова теперь могут рассматриваться как
            #производящие, но после всех присоединенных ранее, в конце списка
    #если закончились слова в Leaves, больше присоединить по одному морфу не получится.

    self.Add_by_name([x for x in Nest if x.pos == 'VERB'])

    candidates = sorted(Nest,  key=lambda word: (word.morph_len, word.pos_priority, word.text))
    #print('cand 2 ', candidates)
    new_word = None
    while (new_word is None) and (len(candidates) > 0):
      candidate = candidates.pop(0)
      new_word = self.Add_by_two_morph(candidate)

    if new_word is None:
      candidates = sorted(Nest,  key=lambda word: (word.morph_len, word.pos_priority, word.text))
      #print('cand 2 lite ', candidates)
      new_word = None
      while (new_word is None) and (len(candidates) > 0):
        candidate = candidates.pop(0)
        new_word = self.Add_by_two_morph(candidate, 'lite')

    #print('3: ', new_word)

    return new_word


  def Add_all(self, Nest, s=None):
            #здесь присоединяем к дереву wf_tree что-то одно,
            #что не получилось присоединить через 1-2 аффикса
            #Тут же оно удаляется из Nest
            #Присоединенные слова в порядке присоединения добавляем в self.all_words
    candidate = sorted(Nest,  key=lambda word: (word.morph_len, word.pos_priority, word.text))[0]
    parents = []
    parent = self.vert
    parents.append(self.vert)
    while len(parents) > 0:
      word = parents.pop(0)
      if (word.pref == candidate.pref[(len(candidate.pref) - len(word.pref)):]) and (set(word.suff) <= set(candidate.suff)) and (set(word.postfix) <= set(candidate.postfix)) and ((word.alternation == 0) or (word.root == candidate.root)):
        for child in word.children: parents.append(child)
        parent = word
    candidate.alternation = parent.alternation if parent.root == candidate.root else 1
    parent.children.append(candidate)
    Nest.remove(candidate)
    self.all_words.append(candidate)
    return candidate

  def print_tree(self, s=''):
        return self.vert.to_string('', s)

"""### Метод построения словообразовательного дерева"""


def main():
    parser = argparse.ArgumentParser(description="Построение словообразовательных деревьев")
    parser.add_argument("nest_file", type=str, help="txt-файл с группами слов одного корня")
    parser.add_argument("vert_file", type=str, help="txt-файл с вершинами деревьев (можно оставить пустым)")
    parser.add_argument("word_format", type=str, help="формат вывода слов в словообразовательных деревьях: morph-classified, morph-divided, not-divided")
    args = parser.parse_args()

    nest_file = args.nest_file
    vert_file = args.vert_file

    start_time = time.time()

    Nests = Nests_from_file(nest_file)
    Verts = Verts_from_file(vert_file)

    WF_Tree_s = []

    for Nest in Nests:
      t = sorted(Nest,  key=lambda word: (word.morph_len, word.len, word.pos_priority, word.text))
      Nest = t
      # 1 этап метода: ищем вершину
      wf_tree = WF_Tree(Nest,Verts) #инициализатор класса дерева. Тут определяется и добавляется вершина, плюс она удаляется из Nest

      # 2 и 3 этапы метода: добавление слов, образованных при помощи 1 и 2 аффиксов (и удаление их из Nest)
      # Выполняются в цикле, пока могут быть добавлены новые слова
      vert = wf_tree.vert #vert - последнее добавленное слово, изначально - вершина дерева
      while vert is not None:
        vert = wf_tree.WF_Tree_Construction(Nest, vert)

        # 4 этап метода: если остались нераспределенные слова,
        # выбираем из них одно и присоединяем к имеющему наиболее совпадающий морфемный состав
        if (vert is None) and (len(Nest) > 0):
           vert = wf_tree.Add_all(Nest)

      WF_Tree_s.append(wf_tree)

    Trees_to_file('wf_trees.txt', WF_Tree_s, args.word_format)

    print("--- %s seconds ---\n" % (time.time() - start_time))

    print('Всего деревьев - ', len(WF_Tree_s))


if __name__ == '__main__':
    main()

