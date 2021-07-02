import time
import curses
import psutil
import os
win=curses.initscr()
lineno=0

def printl(line, highlight=False):
	global lineno
	try:
		if highlight:
			line += " " * (win.getmaxyx()[1] - len(line))
			win.addstr(lineno, 0, line, curses.A_REVERSE)
		else:
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
	row=int(rows)
	for i in range(4):
		printl(" ")
	for a in range(int(rows)):
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
			string+=char
		row-=1
		printl(string)
	win.refresh()
	lineno=0
def stat2num(mas,max):
	mas_tmp=[]
	for i in range(len(mas)):
		s=int(mas[i][0]/max*int(rows))
		r=int(mas[i][1]/max*int(rows))
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
	if len(mas)>int(columns):
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


if __name__=="__main__":
	setup()
	mas=[]
	max=0
	rows, columns = os.popen('stty size', 'r').read().split()
	inet=choose_inet()
	while True:
		rows, columns = os.popen('stty size', 'r').read().split()
		rows=str(int(rows)-7)
		try:
			mas,max=get_stat(mas,max)
			stat2num(mas,max)
		except:
			tear_down()
			print ("See you soon...")
			exit()
	tear_down()
