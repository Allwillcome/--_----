# 打开数据文件和新文件
with open('test.sto', 'r') as f1, open('new.sto', 'w') as f2:
	for line in f1:
		new_line = line.split(',')
		print(new_line)
		str_new = ''
		index = 0
		for i in new_line:
			if index % 4 == 0:
				str_new = str_new + i.strip() + '\t'
			else:
				str_new = str_new + i.strip() + ','
			index = index + 1
		f2.write(str_new.strip()+'\n')
