import os
import pynmea2
import re
import numpy as np
import math
from tkinter import *
from tkinter.constants import *
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import datetime



north = 0
south = 180
east = 90
west = 270
RMC = GGA = GSA = GSV = 0
gsvnum = count = 0
Latitude = 0.0
longitude = 0.0

def duTodfm(x):
	tmp = ""
	data1 = int(float(x))
	data2 = float(float('0.'+x.split('.')[1])*60)
	data3 = int(data2)
	data4 = float('0.'+str(data2).split('.')[1])*60
	data5 = '%.2f'% float(data4)
	data6 = int(float(data5))

	tmp = str(data1) + "°" + str(data3) + "\'" + str(data5) + "\""
	return tmp

def RMCparse(line):
	global RMC,GGA,GSA,GSV,gsvnum,count
	global Latitude,longitude
	GGA = GSA = GSV = gsvnum = count = 0
	record = re.split('[,*]',line)
	if len(record) < 7:
		return

	if record[2] == 'A':			#if data is valid
		RMC = 1
	else:
		return

	Latitude = str(float(record[3])/100)
	longitude = str(float(record[5])/100)



def GSVparse(line,sat):
	global RMC,GGA,GSA,GSV,gsvnum,count
	satinfo = re.split('[,*]',line)
	if RMC == 0:
		return
	if gsvnum is not int(satinfo[2])-1:
		gsvnum = count = 0
		return


	if satinfo[2] =='1':			#第二個參數
		num_sat_inview = satinfo[3]

	i = int(satinfo[2]) - 1			#代表第幾句GSV
	a = 4
	#print(satinfo)
	for j in range(4):
		if count >= int(satinfo[3]):
			break
		for k in range(4):
			if satinfo[a].isdigit():
				sat[j+4*i][k] = int(satinfo[a])  #[[4,5,6,7][8,9,10,11][12,13,14,15][16,17,18,19]] -> 一行GSV有3組衛星資訊
			elif satinfo[a] == '':
				sat[j+4*i][k] = 0
			else:
				GSV = 0	  #無效資料
				continue
			a+=1
		count+=1
	gsvnum += 1
	return sat


files = os.listdir("D:\碩一\下學期\無線感測技術\GPSdata")
for file in files:		
	if '.txt' not in file:	
		continue		
	f = open(file,'r',encoding='utf-8')
	line = f.readline()

	degree = 45
	countt = 0
	space = []
	totalangle = []
	totalup = []
	for  ii in range(int(360 / degree)):
		space.append([])
		totalangle.append([])
		totalup.append([])
	#totalangle = []

	while line:
	#for l in range(15):
	#print(line)
		line = f.readline()


		if line.startswith('$GPRMC'):
			RMCparse(line)

		if line.startswith('$GPGGA'):
			GSA = GSV = gsvnum = count = 0
			if GGA == 0 and RMC == 1:
				GGA = 1
			else:
				print("GGA no use")
				continue

			#satforloc = line.split(',')[7]		#定位用到的衛星數量

		if line.startswith('$GPGSA'):
			GSV = gsvnum = count = 0
			if GSA == 0 and RMC == 1 and GGA == 1:
				GSA = 1
			else:
				print("GSA no use")
				continue
			
			satnum = line.split(',')		#用來定位的那些衛星編號
			satnum = satnum[3:15]
			#print(satnum)

		if line.startswith('$GPGSV'):
			
			satinfo = re.split('[,*]',line)
			if len(satinfo) < 7:
				RMC = GGA = GSA = GSV = 0
				print("GSV no use0")
				continue
			if satinfo[2] =='1':			#第二個參數
				#print('Number of Satellites in View:', satinfo[3])	#第三個參數，可見衛星數量
				num_sat_inview = satinfo[3]
				sat = [[0]*4 for i in range(int(num_sat_inview))]
			sat = GSVparse(line,sat)
			if gsvnum == int(satinfo[1]):
				GSV = 1

		if RMC+GGA+GSA+GSV == 4:			#每個參數為一，代表都有讀到值，是一筆完整的資料
			RMC = GGA = GSA = GSV = gsvnum = count = 0
			#print(sat)
			sat_after_sort = sorted(sat, key = lambda s: s[3])  #依照SNR從小到大排序
			print(sat_after_sort)
			print(file)
			
			angle_of_position = []
			angle_of_up = []
			snr = []
			#snr = np.array([]) 
			for i in range(len(sat_after_sort)):
				if sat_after_sort[i][3] != 0:
					snr.append(sat_after_sort[i][3])

			if len(snr) == 0:
				continue
			#去掉0，剩下的SNR算平均值跟標準差
			array = np.array(snr)
			snr_mean = np.mean(array, axis=0)
			snrstd = np.std(array)  #SD of with axis along column
			#snrbasic = np.max(array) - 2*snrstd
			snrbasic = snr_mean - snrstd
			print("snrstd:",snrstd)
			print("snrbasic:",snrbasic)

			#snr = np.array([]) 
			for i in range(len(sat_after_sort)):
				if sat_after_sort[i][3] < snrbasic:
					angle_of_position.append(sat_after_sort[i][2])
					angle_of_up.append(sat_after_sort[i][1])
			angle = np.array(angle_of_position)		#過濾完的方位角

			countt += 1		#計算總共資料有幾筆
			tmpSpace = []
			for ii in range(int(360 / degree)):
				tmpSpace.append([])

			for ii in range(len(angle)):
				tmpSpace[int(angle[ii] / degree)].append(angle)
				print("方位角:" + str(angle[ii]) + "有障礙物")
				totalangle[int(angle[ii] / degree)].append(angle[ii])
				totalup[int(angle[ii] / degree)].append(angle_of_up[ii])
				#print(totalangle)

			for ii in range(int(360 / degree)):
				if len(tmpSpace[ii]) > 0:
					space[ii].append(tmpSpace[ii][0])



			
	f.close()

	#print(totalangle)
	#print(space)
	print("\n---------------\n")
	percent = countt*0.3
	xpt = []
	ypt = []
	for ii in range(int(360 / degree)):
		if(len(space[ii]) > 0) and len(space[ii]) > percent:
			print("Space " + str(ii * degree) + "~" + str((ii + 1) * degree - 1) + "度 有障礙物(" + str(len(space[ii])) + "/" + str(countt) + ")")
			for i in range(len(totalangle[ii])):
				xpt.append(totalangle[ii][i]*np.pi/180)
				ypt.append(100)
				#ypt.append(totalup[ii][i])

	#print(xpt)
	x_array = np.array(xpt)
	y_array = np.array(ypt)


	
	ax = plt.subplot(111, projection='polar')
	ax.set_facecolor('#CAFFFF')
	ax.set_theta_zero_location('N')
	ax.set_theta_direction(-1)
	#projection为画图样式，除'polar'外还有'aitoff', 'hammer', 'lambert'等
	c = ax.scatter(x_array, y_array, marker = "*", s = 50, c = '#D9006C')

	#ax.scatter为绘制散点图函数
	#plt.title(file)
	file = os.path.splitext(file)[0]
	plt.savefig('./pic/'+file+'_up.jpg', dpi=1200, bbox_inches='tight')
	plt.close()
	#plt.show()


window = Tk()
window.title("Group 1")
window.minsize(width=500, height=500)
window.resizable(width=False, height=False)
window.configure(bg='white')



label = Label(text="Latitude: "+ duTodfm(Latitude) + "N Longitude: "+ duTodfm(longitude) + "E", font=("Arial", 10, "bold"), padx=0, pady=5, bg="white", fg="black")
label.pack(anchor=NW)

loc_dt = datetime.datetime.today() 
loc_dt_format = loc_dt.strftime("%Y/%m/%d %H:%M:%S")
#print(loc_dt_format)

label = Label(text=loc_dt_format, font=("Arial", 10, "bold"), padx=0, pady=5, bg="white", fg="black")
label.pack(anchor=NW)

#print(Latitude)
#print(longitude)

img = Image.open('D:\璽智\網路(下)\GPSdata\pic\e5_up.jpg')
img_re = img.resize((500, 500))
tk_img = ImageTk.PhotoImage(img_re)

label = Label(window, image=tk_img, width=500, height=500, anchor=NW)  # 設定 anchor
label.pack()

window.mainloop()



