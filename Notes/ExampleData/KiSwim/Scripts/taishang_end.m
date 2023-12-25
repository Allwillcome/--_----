filename = importdata('/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/电压数据/LIST.TXT');
filename_1 = importdata('/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/力值数据/LIST.TXT');%读取还有文件名称的文件
x = size(filename,1);
for i = 1:x;
%read file
read_name = ['/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/电压数据/', filename{i,1}]; %读取文件名称时，文件名称的写法
data_V = csvread(read_name,6 ,0); %读取filename中从第7行第一列开始的所有数据
data_offset = csvread(read_name,4 , 0, [4 0 4 31]);% 读取filename 中单独第4行的所有数据
gun = data_V(:,32);
V_grabz12 = data_V(:,1) - data_offset(1); %抓手Z方向电压
V_grabx12 = data_V(:,2) - data_offset(2); %抓手X方向电压
V_Fy14 = data_V(:, 3) - data_offset(3); %前台Y14电压
V_Fy23 = data_V(:, 4) - data_offset(4); %前台Y23电压
V_Fz1 = data_V(:,5) - data_offset(5); %前台Z1电压
V_Fz2 = data_V(:,6) - data_offset(6); %前台Z2电压
V_Fz3 = data_V(:,7) - data_offset(7); %前台Z3电压
V_Fz4 = data_V(:,8) - data_offset(8); %前台Z4电压.对照邮件的解析其中的电压所对应的意义
V_Ry14 = data_V(:, 11) - data_offset(11); %后台Y14电压
V_Ry23 = data_V(:, 12) - data_offset(12); %后台Y23电压
V_Rz1 = data_V(:,13) - data_offset(13); %后台z1电压
V_Rz2 = data_V(:,14) - data_offset(14); %后台z2电压
V_Rz3 = data_V(:,15) - data_offset(15); %后台z3电压
V_Rz4 = data_V(:,16) - data_offset(16); %后台z4电压
F_Fz1 = (V_Fz1 ./3.611).*1000;
F_Fz2 = (V_Fz2 ./3.611).*1000;
F_Fz3 = (V_Fz3 ./3.611).*1000;
F_Fz4 = (V_Fz4 ./3.611).*1000; %力值转换公式，工程师提供
FZ = F_Fz1 + F_Fz2 + F_Fz3 + F_Fz4; % FZ是4个传感器相加
F_Y14 = (V_Fy14./3.861).*1000;
F_Y23 = (V_Fy23./3.861).*1000;
FY = F_Y14 + F_Y23; %FY4个传感器在水平于台上相加
Gz = (V_grabz12./3.899).*1000;
Gx = (V_grabx12./1.842).*1000;%把抓手的力算出来但是没有进行合成，对方向不太确定
F_Rz1 = (V_Rz1 ./3.657).*1000;
F_Rz2 = (V_Rz2 ./3.657).*1000;
F_Rz3 = (V_Rz3 ./3.657).*1000;
F_Rz4 = (V_Rz4 ./3.657).*1000;
RZ = F_Rz1 + F_Rz2 + F_Rz3 + F_Rz4; %后台垂直台的力
R_Y14 = (V_Ry14 ./3.864).*1000;
R_Y23 = (V_Ry23 ./3.864).*1000;
RY = R_Y14 + R_Y23; %后台平行台子的力
%滤波filt
n = 2;
fs = 500;
Wn = 10/(fs/2);
[a, b] = butter(n, Wn);

%前脚垂直力和前脚水平力，前脚力 frontplate
qianjiao_horizontal = FZ .*(sin(10.2*pi/180)) + FY.*(cos(10.2*pi/180));
qianjiao_vertical = FZ .*(cos(10.2*pi/180)) - FY.*(sin(10.2*pi/180));
F_F = ((FZ).^2 + (FY).^2).^0.5;
%滤波之后_1
F_F_1 = filtfilt(a,b,F_F);
qianjiao_horizontal_1 = filtfilt(a,b,qianjiao_horizontal);
qianjiao_vertical_1 = filtfilt(a,b,qianjiao_vertical);

%后脚垂直力和后脚水平力 rearplate
houjiao_horizontal = RZ .*(sin(10.2*pi/180)) + RY.*(cos(10.2*pi/180));
houjiao_vertical = RZ .*(cos(10.2*pi/180)) - RY.*(sin(10.2*pi/180));
F_R = ((RZ).^2 + (RY).^2).^0.5;
F_R_1 = filtfilt(a,b,F_R);
houjiao_horizontal_1 = filtfilt(a,b,houjiao_horizontal);
houjiao_vertical_1 = filtfilt(a,b,houjiao_vertical);

%把手的力值Gz为垂直于水面方向，Gx为平行于水面方向
zhuashou_vertical = (Gz).*(-1);
zhuashou_vertical_1 = filtfilt(a,b, zhuashou_vertical);
zhuashou_horizontal = Gx;
zhuashou_horizontal_1 = filtfilt(a,b, zhuashou_horizontal);

%所有力：垂直于测力台  vertical and horizontal force
li_vertical = FZ + RZ;
li_horizontal = FY + RY; 
F_V = li_vertical.*(cos(10.2*pi/180)) - li_horizontal.*(sin(10.2*pi/180))+Gz;
F_H = li_vertical.*(sin(10.2*pi/180)) + li_horizontal.*(cos(10.2*pi/180))+Gx;
F_V_1 = filtfilt(a,b,F_V);
F_H_1 = filtfilt(a,b,F_H);

%integration
%积分找出开始时间和结束时间
%创造时间序列，为积分做准备
T = 0:0.002:10;
T = T';
d = size(F_H_1,1);
t = T(1:d, 1);
%运用体重对数据进行标准化
%计算标准体重
mg = mean(F_V_1(1:500));
F_F_2 = F_F_1 ./mg;
qianjiao_horizontal_2 = qianjiao_horizontal_1./mg;
qianjiao_vertical_2 = qianjiao_vertical_1./mg;
F_R_2 = F_R_1 ./mg;
houjiao_horizontal_2 = houjiao_horizontal_1./mg;
houjiao_vertical_2 = houjiao_vertical_1./mg;
zhuashou_vertical_2 = zhuashou_vertical_1./mg;
zhuashou_horizontal_2 = zhuashou_horizontal_1./mg;
F_V_2 = F_V_1 ./mg;
F_H_2 = F_H_1 ./mg;

%积分共8列数,命名规则按照H_txt中的顺序进行
jifen1 = cumtrapz(t, qianjiao_horizontal_1);
jifen2 = cumtrapz(t, qianjiao_vertical_1);
jifen3 = cumtrapz(t, houjiao_horizontal_1);
jifen4 = cumtrapz(t, houjiao_vertical_1);
jifen5 = cumtrapz(t, zhuashou_vertical_1);
jifen6 = cumtrapz(t, zhuashou_horizontal_1);
jifen7 = cumtrapz(t, F_V_1);
jifen8 = cumtrapz(t, F_H_1);

%数据输出 ouput data
write_name = ['/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/力值数据/', filename_1{i, 1}];
H_txt = {'前台合力','前台水平力','前台垂直力','后台合力','后台水平力','后台垂直力','抓手垂直力','抓手水平力'...
    '垂直力','水平力', '时间轴','Gun'};
H_txt1 = {'前台水平力积分','前台垂直力积分','后台水平力积分','后台垂直力积分','抓手垂直力积分','抓手水平力积分','垂直力积分','水平力积分'}
%标准化数据
xlswrite(write_name, F_F_2, 'data', 'A2');
xlswrite(write_name, H_txt(1), 'data', 'A1');
xlswrite(write_name,qianjiao_horizontal_2, 'data', 'B2');
xlswrite(write_name, H_txt(2), 'data', 'B1');
xlswrite(write_name,qianjiao_vertical_2, 'data', 'C2');
xlswrite(write_name, H_txt(3), 'data', 'C1');
xlswrite(write_name, F_R_2, 'data', 'D2');
xlswrite(write_name, H_txt(4), 'data', 'D1');
xlswrite(write_name, houjiao_horizontal_2, 'data', 'E2');
xlswrite(write_name, H_txt(5), 'data', 'E1');
xlswrite(write_name, houjiao_vertical_2,'data', 'F2');
xlswrite(write_name, H_txt(6), 'data', 'F1');
xlswrite(write_name, zhuashou_vertical_2,'data', 'G2');
xlswrite(write_name, H_txt(7), 'data', 'G1');
xlswrite(write_name, zhuashou_horizontal_2,'data', 'H2');
xlswrite(write_name, H_txt(8), 'data', 'H1');
xlswrite(write_name, F_V_2 , 'data', 'I2');
xlswrite(write_name, H_txt(9), 'data', 'I1');
xlswrite(write_name,F_H_2 , 'data', 'J2');
xlswrite(write_name, H_txt(10), 'data', 'J1');
xlswrite(write_name, t , 'data', 'K2');
xlswrite(write_name, H_txt(11), 'data', 'K1');
%Gun 写入excel
xlswrite(write_name, gun , 'data', 'L2');
xlswrite(write_name, H_txt(12), 'data', 'L1');

%后面是积分的写入，前面的力不除以体重
xlswrite(write_name, jifen1 , 'data', 'M2');
xlswrite(write_name, H_txt1(1), 'data', 'M1');
xlswrite(write_name, jifen2 , 'data', 'N2');
xlswrite(write_name, H_txt1(2), 'data', 'N1');
xlswrite(write_name, jifen3 , 'data', 'O2');
xlswrite(write_name, H_txt1(3), 'data', 'O1');
xlswrite(write_name, jifen4 , 'data', 'P2');
xlswrite(write_name, H_txt1(4), 'data', 'P1');
xlswrite(write_name, jifen5 , 'data', 'Q2');
xlswrite(write_name, H_txt1(5), 'data', 'Q1');
xlswrite(write_name, jifen6 , 'data', 'R2');
xlswrite(write_name, H_txt1(6), 'data', 'R1');
xlswrite(write_name, jifen7 , 'data', 'S2');
xlswrite(write_name, H_txt1(7), 'data', 'S1');
xlswrite(write_name, jifen8 , 'data', 'T2');
xlswrite(write_name, H_txt1(8), 'data', 'T1');
end





