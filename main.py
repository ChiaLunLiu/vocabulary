import sqlite3
import sys
import ImageTk, Image
import Tkinter
import tkFont
from functools import partial
def color_config(widget,color,event):
	for i in widget.winfo_children():
		i.configure(bg=color)
	widget.configure(bg=color)

class MyEntry:
	def __init__(self,parent):
		self.frame = Tkinter.Frame(parent)
		self.frame.config(bg="black")
		self.var = Tkinter.StringVar()
		self.entry = Tkinter.Entry(self.frame,textvariable=self.var,font=("Purisa",12))
		self.var.set("add new word")
		self.entry.configure(fg="white",bg="#696969",)
		self.entry.config(highlightthickness=0)  # no border line
		self.entry.place(relx=0.005,rely = 0.05,relwidth=0.99,relheight=0.90)
		# set event
		self.frame.bind("<Enter>", partial(self.enter_event, self.frame, "#BEBEBE"))
		self.frame.bind("<Leave>", partial(self.leave_event, self.frame, "black"))
	def resize(self,relx,rely,relwidth,relheight):
		self.frame.place(relx=relx,rely=rely,relwidth=relwidth,relheight=relheight)
	def enter_event(self,widget,color,event):
		widget.config(bg=color)
	def leave_event(self,widget,color,event):
		widget.config(bg=color)
class GUI:
	def __init__(self):
		self.wd = Wordbase('word')
		self.row = 0
		self.initGUI()
	def initGUI(self):
		self.top = Tkinter.Tk()
		self.height = self.top.winfo_screenheight()-150 # GUI height
		self.width = self.top.winfo_screenwidth()-150  # GUI width
		self.top.title("My vocabulary")
		self.top.geometry('+0+0')
		self.mainFrame = Tkinter.Frame(self.top,  height=self.height, width=self.width)
		self.C = Tkinter.Frame(self.mainFrame,bg="white")
		self.var = Tkinter.StringVar()
		self.topFrame = Tkinter.Frame(self.top,bg="white")
		self.labelNum = Tkinter.Label(self.topFrame,text="word")
		self.entryWord = Tkinter.Entry(self.topFrame,bd=5)
		self.labelNum.pack(side=Tkinter.LEFT)
		self.entryWord.pack(side=Tkinter.LEFT)
		self.button_add = Tkinter.Button(self.topFrame, text ="add", command = self.addEvent)
		self.button_add.pack(side = Tkinter.LEFT)
		self.button_search = Tkinter.Button(self.topFrame, text ="search", command = self.searchEvent)
		self.button_search.pack(side=Tkinter.LEFT)
		self.label = Tkinter.Label(self.top,textvariable=self.var)
#		for r in range(3):
#			for c in range(4):
#				Tkinter.Label(self.C, text='R%s/C%s'%(r,c),foreground="purple",
#					borderwidth=1 ).grid(row=r,column=c)
		#self.initAddWordPanel()
		self.panel = None
		self.C.place(relwidth=1.0,relheight=1.0)
		self.topFrame.pack()
		self.mainFrame.pack()
		self.label.pack()
		self.top10()
	def initAddWordPanel(self):
		if self.panel != None: self.panel.destroy()
		self.panel = Tkinter.Frame(self.mainFrame,bg="#4F4F4F")		
		self.newword = MyEntry(self.panel)
		self.newword.resize(relx=0.1,rely=0.1,relwidth=0.3,relheight=0.05)
		self.panel.place(relx=0.2,rely=0,relwidth=0.8,relheight=1.0)
	def clear(self):
		self.row = 0
		self.C.destroy()   # delete all widgets
		self.C = Tkinter.Frame(self.mainFrame,bg="white")
		self.C.place(relheight=1.0,relwidth=1.0)
		self.initAddWordPanel()
	def top10(self):
		self.clear()
		cur = self.wd.top10()
		for i in cur:
			self.addEntry(i[0],i[1],i[2])
	def addEntry(self,word,refcount,desc):
		lineHeight=  0.003
		CellHeight = 0.1 - lineHeight
		relyLine = 0.1*(self.row)
		rely = 0.1*(self.row)+lineHeight
		txtCnt = ("%d" % (refcount))
		t = Tkinter.Label(self.C,bg="gray")
		t.place(rely=relyLine,relx=0.0,relheight=lineHeight,relwidth=1.0)

		my = Tkinter.Frame(self.C)
		my.place(rely = rely,relx=0.0,relheight=CellHeight,relwidth=1.0)
		colorblue = "#00BFFF"
		my.bind("<Enter>", partial(color_config, my, colorblue))
		my.bind("<Leave>", partial(color_config, my, "white"))
		font = tkFont.Font(family="Helvetica", size=12)

		t = Tkinter.Label(my,text= word,foreground="black",bg="white",font = font)
		t.place(rely=0,relx=0.0,relheight=1.0,relwidth=0.40)
		t = Tkinter.Label(my,text= txtCnt,foreground="black",bg="white",font = font)
		t.place(rely=0,relx=0.4,relheight=1.0,relwidth=0.20)
		t= Tkinter.Label(my,text= desc,foreground="black",bg="white",font = font)
		t.place(rely=0,relx=0.6,relheight=1.0,relwidth=0.40)
		self.row = self.row +1
	def addEvent(self):
		print ("call addEvent")
		keyword = self.entryWord.get()
		ret = self.wd.getOrCreateWord(keyword)
		self.addEntry(ret[0],ret[1],ret[2])
	def searchEvent(self):
		#print "called searchEvent"
		self.clear()
		keyword = self.entryWord.get()
		ret = self.wd.search( keyword )
		if ret != None:
			ret[1] = ret[1]+1
			self.wd.update(ret)
			self.addEntry(ret[0],ret[1],ret[2])
class Wordbase:
	def __init__(self,dbname):
		self.con = sqlite3.connect(dbname)
		self.createIndexTable()
	def dbcommit(self):
		self.con.commit()
	def createIndexTable(self):
		self.con.execute('create table if not exists Wordbase(word,refcount integer,desc)')
		self.dbcommit()
	def getOrCreateWord(self,word):
		cur = self.con.execute("select * from Wordbase where word='%s'" % (word)).fetchone()
		if cur ==None:
			cur = self.con.execute("insert into Wordbase (word,refcount,desc) values('%s',0,'')" %(word))
			self.dbcommit()
			cur = self.con.execute("select * from Wordbase where word='%s'" % (word)).fetchone()
		return [i for i in cur]
	def update(self,row):
		self.con.execute("update Wordbase set word='%s',refcount=%d,desc='%s' where word='%s'" %(row[0],row[1],row[2],row[0]))
		self.dbcommit()
	def top10(self):
		return self.con.execute("select * from Wordbase order by refcount Desc limit 10").fetchall()
	def search(self,keyword):
		cur = self.con.execute("select * from Wordbase where word='%s' "%( keyword)).fetchone()
		if cur ==None :
			return None
		return [ i for i in cur]
	def getAll(self):
		cur = self.con.execute("select * from Wordbase")
		ret=[]
		for i in cur :
			t = [ j for j in i]
			ret.append(t)
		return ret
def main():
	#print "hi"
	gui = GUI()
	#base = Wordbase('word')
	while 1:
		#print "next\n"
		k = int(raw_input())
		if k == 1:
		#	print "getorCreateWord"
			wd = raw_input()
			cur = gui.wd.getOrCreateWord(wd)
		#	print cur
		else:
			#print "getAll"
			cur = gui.wd.getAll()
			for i in cur:
				gui.addEntry(i[0],i[1],i[2])
		#		gui.addEntry(i[0],i[1],i[2])
			#	print i
if __name__ == "__main__":
	sys.exit(main())