# %%
import os
import pandas as pd
import matplotlib.pyplot as plt

# %%
# 更改当前路径
path = input("请输入文件所在文件夹：")
os.chdir(path)
print("当前路径为:{}".format(os.getcwd()))

# %%
# 新建plot 储存图片
plot_dir_name = "plot"
if not os.path.exists(plot_dir_name):
    os.mkdir(plot_dir_name)

print(os.listdir())

# %%
# 读取 Xsens MVN 数据
Xsens_file = "20230413跺脚走6步路测试-XsensMVN.xlsx"

# 相较于 pd.readexcel(), 
# pd.ExcelFile()只读取Excel 元数据
# 当处理大批量数据时，更加的高效
# 此处如果读取全部数据，用时大约 1 分钟读取速度较慢
Xsens_excel_file =  pd.ExcelFile(Xsens_file)
Xsens_sheetnames = Xsens_excel_file.sheet_names
print(Xsens_sheetnames)

# %%
# 读取数据
Xsens_df = pd.read_excel(Xsens_file, sheet_name="Sensor Free Acceleration")
# 查看基本信息
Xsens_df.info()

# %%
# 查看所有列的名称
Xsens_df.columns

# %%
# 绘制图片
fig, axs = plt.subplots(1,3,figsize=(12,3),sharey=True)

# 设置第一幅图标题
axs[0].set_title("x")
Xsens_df["Left Foot x"].plot(ax=axs[0],color="r")

# 设置第二副图标题
axs[1].set_title("y")
Xsens_df["Left Foot y"].plot(ax=axs[1],color="g")

# 设置第三副图标题
axs[2].set_title("z")
Xsens_df["Left Foot z"].plot(ax=axs[2],color="b")

# 显示中文
plt.rcParams['font.sans-serif'] = ['Heiti TC']
plt.rcParams['font.family'] = ['Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

# 设置总标题
plot_file_name = "Xsens 左脚x y z方向自由加速度变化"
plot_file_path = os.path.join(plot_dir_name,plot_file_name)
plt.suptitle(plot_file_name,y=1)
plt.savefig(plot_file_path)

# %%
# 尊悦小蓝块IMU数据分析
zy_file = "20230413跺脚走 6 步路测试-zyIMU.csv"
zy_df = pd.read_csv(zy_file)
print(zy_df.info)

# %%
#浏览数据
print(zy_df.info())
#查看前 3 行代码
zy_df.head(3)

# %%
# 查看所有列的名称
zy_df.columns

# %%
# 筛选出左脚的传感器，编号为2
zy_df_filterd = zy_df[zy_df["SensorId"]==2]
zy_df_filterd.head(3)

# %%
# 查看所有列的数据
zy_df_filterd.columns

# %%
# 绘图
fig, axs = plt.subplots(1,3, figsize=(12,3), sharey=True)

# 绘制第一幅图
axs[0].set_title("x")
zy_df_filterd[" LinAccX (g)"].plot(ax=axs[0],color="r")

# 绘制第二副子图
axs[1].set_title("y")
zy_df_filterd[" LinAccY (g)"].plot(ax=axs[1],color="g")

# 绘制第三副子图
axs[2].set_title("z")
zy_df_filterd[" LinAccZ (g)"].plot(ax=axs[2],color="b")

# 命名并保存
# 设置总标题
plot_file_name = "尊悦 左脚x y z方向线性加速度变化"
plot_file_path = os.path.join(plot_dir_name,plot_file_name)
plt.suptitle(plot_file_name,y=1)
plt.savefig(plot_file_path)

# %%



