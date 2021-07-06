import time
import curses
import psutil
import os
win=curses.initscr()
lineno=0

def printl(line):
	global lineno
	try:
		win.addstr(lineno, 0, line, 0)
	except curses.error:
		lineno = 0
		win.refresh()
		raise
	else:
		lineno += 1

def setup():
	win.keypad(1)
	curses.start_color()
	curses.use_default_colors()
	for i in range(0, curses.COLORS):
		curses.init_pair(i + 1, i, -1)
	curses.endwin()
	win.nodelay(1)

def tear_down():
	win.keypad(0)
	curses.nocbreak()
	curses.echo()
	curses.endwin()

def find_max(mas,max):
	m_new=0
	for i in mas:
		for ii in i:
			if ii>m_new:
				m_new=ii
	if m_new!=max:
		max=m_new
	return max

def print_num(mas):
	global lineno
	row=rows
	for i in range(4):
		printl(" ")
	for _ in range(rows):
		string=""
		for i in mas:
			s=False
			r=False
			if i[0]>=row:
				s=True
			if i[1]>=row:
				r=True
			if s and r:
				char="@"
			elif s and not r:
				char="#"
			elif r and not s:
				char="$"
			else:
				char=" "
			string+=char*2
		row-=1
		printl(string)
	for i in range(3):
		printl(" "*(columns-1)*2)
	win.refresh()
	lineno=0

def stat2num(mas,max):
	mas_tmp=[]
	for i in range(len(mas)):
		if max==0:
			s=0
			r=0
		else:
			s=mas[i][0]/max*rows
			r=mas[i][1]/max*rows
		mas_tmp.append([s,r])
	print_num(mas_tmp)

def get_stat(mas,max):
	global inet
	sended_a=psutil.net_io_counters(pernic=True)[inet].packets_sent
	recv_a=psutil.net_io_counters(pernic=True)[inet].packets_recv
	time.sleep(2)
	recv_b=psutil.net_io_counters(pernic=True)[inet].packets_recv
	sended_b=psutil.net_io_counters(pernic=True)[inet].packets_sent
	mas.append([sended_b-sended_a,recv_b-recv_a])
	if len(mas)>columns:
		mas.pop(0)
	max=find_max(mas,max)
	return mas,max

def choose_inet():
	global lineno
	inets=[]
	status=[]
	now=0
	max=0
	for i in psutil.net_if_addrs():
		if len(i)>max:
			max=len(i)
		inets.append(i)
		status.append(" ")
	while 1:
		key=win.getch()
		if key==curses.KEY_DOWN and now<len(inets)-1:
			now+=1
		elif key==curses.KEY_UP and now>0:
			now-=1
		elif key==curses.KEY_ENTER or key==10 or key==13:
			for i in inets:
				printl(" "*(max+4))
			lineno=0
			return inets[now]
		for inet in range(len(inets)):
			stat=status[inet]
			if inet==now:
				stat="*"
			printl("[{}] {}".format(stat,inets[inet]))
		win.refresh()
		lineno=0

def getSize():
	rows,columns=os.popen('stty size', 'r').read().split()
	rows=int(rows)
	columns=int(columns)
	while columns%2!=0:
		columns-=1
	return rows,int(columns/2)

if __name__=="__main__":
	mas=[]
	max=0
	setup()
	rows,columns=getSize()
	inet=choose_inet()
	while True:
		rows,columns=getSize()
		rows=rows-7
		try:
			mas,max=get_stat(mas,max)
			stat2num(mas,max)
		except:
			tear_down()
			print ("See you soon...")
			exit()
