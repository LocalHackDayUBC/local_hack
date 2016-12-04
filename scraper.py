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
