from OPENAI_API import chat
import pandas as pd
import pyttsx3
import json, requests
import random
import warnings
warnings.filterwarnings('error')

class study_on():
    def __init__(self, words_book):
        self.words_book = words_book
        self.chat = chat()
    def story(self, words, style = None):
        # content = "You are a senior language expert who can create interesting English stories using the new words from the list I provided. When the new word appear in the story,the new word should followed by its English pronunciation, part of speech, and Chinese meaning. Then you will list all the new words, provide their English pronunciation, part of speech, and Chinese meaning. Here is the list of new words I provided: "
        # for word in words:
        #     content += (word.word + " ")
        # message = [{"role": "user",
        #             "content": content}]
        # print(self.chat.send_message(message))
        print("this is a stroy")

    def learn(self, group=5, new= True, review=True):
        cmds = 'story'
        spelled = False
        while True:
            cmds = cmds.split(" ")
            cmd = cmds[0]
            arg = None if len(cmds) == 1 else cmds[1]
            if cmd == 'story':
                words_group = self.words_book.generate_group(group, new, review)
                self.story(words_group)
                cmds = input()
                continue
            if cmd == 'search':
                _word = self.words_book.search(arg)
                print(_word.translation)
                _word.read()
                cmds = input()
                continue
            if cmd == 'spell':
                self.spell_group(words_group)
                cmds = input()
                spelled = True
                continue
            if cmd == 'next':
                if spelled:
                    cmds = 'story'
                else:
                    print("You have not spell!!!")
                    cmds = input()
                continue
            if cmd == 'easy':
                _word = self.words_book.search(arg)
                _word.easy = True
                cmds = input()
                continue
            if cmd == 'quit':
                self.words_book.save()
                return
    
    def spell_group(self, group):
        lenth = len(group)
        passed = [False for _ in range(lenth)]
        count = 0
        while count < lenth:
            for i in range(lenth):
                if not passed[i]:
                    times = group[i].spell()
                    if times == 1:
                        passed[i] = True
                        count += 1


class word:
    def __init__(self, index, word, translation = None, times = 0, easy = False):
        self.index = index
        self.word = word
        self.translation = translation
        self.times = times
        self.easy = easy

    def read(self):
        pyttsx3.speak(self.word)	

    def translate(self):
        url = 'https://fanyi.baidu.com/sug'
        data = {'kw': self.word}
        res = requests.post(url, data=data).json()
        if len(res['data']) == 0:
            self.translation = "Unknown"
        else:
            self.translation = res['data'][0]['k'] +': ' + res['data'][0]['v']
        print(self.translation)
        return self.translation

    def spell(self):
        count = 0
        while True:
            print(self.translation.split(":")[1])
            my_spell = input("Input the English word: ")
            count += 1
            if my_spell == self.word:
                return count

class words_book():
    def __init__(self, words_list = None, name = "words_book", file = None):
        if file == None:
            self.file = file
            self.words = []
            translation = []
            lenth = len(words_list)
            for i in range(lenth):
                w = word(i, words_list[i])
                self.words.append(w)
                translation.append(w.translate())
                i+=1
                print(i + 1, '/', lenth)
            times = [0 for _ in range(lenth)]
            easy = [False for _ in range(lenth)]
            data = {'words': words_list[0:lenth], 'translation': translation, 'times': times, 'easy': easy}
            df = pd.DataFrame(data)
            df.to_excel('data\\' + name +'.xlsx')
            self.total_words = lenth
            self.learned = 0
        else:
            self.file = file
            self.words = []
            rf = pd.read_excel(file)
            _words = rf['words']
            _translation = rf['translation']
            _times = rf['times']
            _easy = rf['easy']
            self.total_words = len(_words)
            self.learned = 0
            for i in range(self.total_words):
                if _times[i] > 0:
                    self.learned += 1
                self.words.append(word(i, _words[i], _translation[i], _times[i], _easy[i]))

    def save(self):
        times = []
        easy = []
        w = pd.read_excel(self.file, usecols=[1, 2, 3, 4])
        for i in range(self.total_words):      
            w.loc[i, 'times'] = self.words[i].times 
            w.loc[i, 'easy'] = self.words[i].easy

        pd.DataFrame(w).to_excel(self.file)
    def search(self, word):
        for _word in self.words:
            if _word.word == word:
                return _word


    def generate_group(self, group=5, new= True, review=True):
        words_group = []
        if self.total_words == self.learned:
            new = False
            review = True
        if new and review:
            for i in range(group // 2):
                _word = self.words[random.randint(0, self.learned - 1)]
                _word.times += 1
                words_group.append(_word)
            for i in range(group // 2, group):
                _word = self.words[self.learned + i]
                _word.times += 1
                self.learned += 1
                words_group.append(_word)

        elif new:
            for i in range(group):
                _word = self.words[self.learned + i]
                _word.times += 1                
                words_group.append(_word)
            self.learned += group
        elif review:
            for i in range(group):
                _word = self.words[random.randint(0, self.learned - 1)]
                _word.times += 1
                words_group.append(_word)

        return words_group
    
    def status(self):
        print(self.learned, "/", self.total_words)
        


        

# words_list = []
# r = pd.read_excel('data\words_book.xlsx')
# for _word in r['单词']:
#     if _word != '单词':
#         words_list.append(_word)
        
# words_book(words_list=words_list, name="CET6-1500")
studying = study_on(words_book(file="data\CET6-1500.xlsx"))
studying.learn(group=2, review=False)




