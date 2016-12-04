from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


html_doc = urlopen("https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&req=1&dept=CPSC")

soup = BeautifulSoup(html_doc, 'html.parser')

course_regex = '\w{4} \d{3}'
course_pattern = re.compile (course_regex)
course_regex2 = '\w{4}'
course_pattern2 = re.compile (course_regex2)
course_regex3 = '\d{3}'
course_pattern3 = re.compile (course_regex3)

courses = soup.find_all('a', text=course_pattern)

class Node:
    def __init__(self,name, prereqGroup):
        self.name = name
        self.prereqGroup = prereqGroup

class HashTable:

    table = [None] * 256
    def __init__(self):
        table = [None] * 256
        
    def get_value(self, key):
        total = 0
        for i in range(len(key)):
            total += ord(key[i]) * (7**i)
        return (len(key) * total) % 256

    def insert(self, key, value):
        key = self.get_value(key)
        if  self.table[key] == None:
            self.table[key] = value
        
    

    def delete(self, key):
        val = self.get_value(key)
        if self.table[val] != None:
            if type(self.table[val]) == list:
                i = self.table[val].index(key)
                self.table[val][i] = None
            else:
                self.table[val] = None
        else:
            KeyError()

    def lookup(self, key):
        found = False
        val = self.get_value(key)
        if type(self.table[val]) == list:
            found = key in self.table[val]
        else:
            found = self.table[val] == key
        return found

state = HashTable()
state.insert("CPSC221", True)
state.insert("CPSC110", True)
state.insert("CPSC121", True)
#for link in courses:
#    print(link.get_text())

targetCourse = "CPSC 340"

html_doc2 = None

prereq_regex = '.*Pre-reqs:.*'
prereq_pattern = re.compile (prereq_regex)

# ops
AND=0
OR1 = 1
OR2 = 2
#quantifiers
CC = 3
ALLOF = 4
ONEOF = 5

keywords = ['and', 'or1', 'or2', 'cc', 'allof', 'oneof']


class PrerequisiteGroup:
    list_of_course_groups = []
    list_of_operations = []
    def addCourseGroup(self, cg):
        self.list_of_course_groups.append(cg)
    def addOperation(self, op):
        self.list_of_operations.append(op)
    def print(self):
        i = 0
        while(i<len(self.list_of_course_groups)):
            print("Course group " + str(i+1) + ": " + keywords[self.list_of_course_groups[i].quantifier])
            self.list_of_course_groups[i].print()
            i+=1
        i =0
        while(i<len(self.list_of_operations)):
            print(" " + keywords[self.list_of_operations[i]])
            i+=1
    def evaluate(self):
        list_of_reduced_vals = []
        for group in self.list_of_course_groups:
            list_of_reduced_vals.append(group.evaluate())
        i = len(self.list_of_operations) - 1
        j = len(self.list_of_reduced_vals) - 1
        rsf = list_of_reduced_vals[j]
        j-=1
        rsf_temp = True
        while(i>=0):
            if(self.list_of_operations[i] == AND):
                rsf = rsf and list_of_reduced_vals[j]
                j-=1
            if(self.list_of_operations[i] == OR1):
                rsf = rsf or rsf_temp
                j-=1
            if(self.list_of_operations[i] == OR2):
                rsf_temp = rsf
            i-=1


class CourseGroup:
    quantifier = CC
    list_of_courses = []
    def __init__(self, quantifier_code, pg):
        self.quantifier = quantifier_code
        pg.addCourseGroup(self)
        self.list_of_courses=[]
    def addCourse(self, cc):
        self.list_of_courses.append(cc)
    def print(self):
        for c in self.list_of_courses:
            print(c + " ")
    def evaluate(self):
        for c in self.list_of_courses:
            if(quantifier == CC):
                return state.get(self.list_of_courses[0])
            if(quantifier == ALLOF):
                rsf = True
                for c in self.list_of_courses:
                    rsf = state.get(c) and rsf
                return rsf
            if(quantifier == ONEOF):
                rsf = True
                for c in self.list_of_courses:
                    rsf = state.get(c) or rsf
                return rsf

for link in courses:
    if(link.get_text()==targetCourse):
        html_doc2 = urlopen("https://courses.students.ubc.ca"+link.get('href'))
        s = BeautifulSoup(html_doc2, 'html.parser')
        paragraphs = s.find_all('p')
        paragraphs = filter(lambda p: (len(re.findall(prereq_pattern, p.text))) > 0, paragraphs)
        print("COURSE: " + link.get_text())
        for p in paragraphs:
            ltext = p.get_text().lower()[14:]
            ltext= re.sub('[,]', '', ltext)
            ltext = re.sub('[.]', ' .', ltext)
            words = ltext.split(' ')
            prev = ""

            pg = PrerequisiteGroup()
            currentCG = None
            lastQuantifier = -1
            lastOp = -1

            for word in words:
                #print("The word is " + word)
                #if(word=="."):
                #    print()
                if(word=="and"):
                    print("***Found and")
                    pg.addOperation(AND)
                    lastOp = AND
                    lastQuantifier = -1
                if(word=="(a)"):
                    print("***Found or1")
                    pg.addOperation(OR1)
                    lastOp = OR1
                    lastQuantifier = -1
                if(word=="(b)"):
                    print("***Found or2")
                    pg.addOperation(OR2)
                    lastOp = OR2
                    lastQuantifier = -1
                if(word=="of"):
                    if(prev=="one"):
                        print("***Found one of.")
                        currentCG = CourseGroup(ONEOF, pg)
                        lastQuantifier = ONEOF
                    if (prev=="all"):
                        print("***Found all of.")
                        currentCG = CourseGroup(ALLOF, pg)
                        lastQuantifier = ALLOF
                if((len(re.findall(course_pattern3, word)) > 0) and (len(re.findall(course_pattern2, prev)) > 0) and prev[0]!="("):
                    print("***Found course code.")
                    if(lastQuantifier==-1):
                        print("***Found CC")
                        currentCG = CourseGroup(CC, pg)
                        lastQuantifier = CC
                    currentCG.addCourse(prev + word)
                prev = word
            pg.print()
        print("---------------------")
