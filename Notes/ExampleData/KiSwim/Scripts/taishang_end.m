filename = importdata('/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/��ѹ����/LIST.TXT');
filename_1 = importdata('/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/��ֵ����/LIST.TXT');%��ȡ�����ļ����Ƶ��ļ�
x = size(filename,1);
for i = 1:x;
%read file
read_name = ['/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/��ѹ����/', filename{i,1}]; %��ȡ�ļ�����ʱ���ļ����Ƶ�д��
data_V = csvread(read_name,6 ,0); %��ȡfilename�дӵ�7�е�һ�п�ʼ����������
data_offset = csvread(read_name,4 , 0, [4 0 4 31]);% ��ȡfilename �е�����4�е���������
gun = data_V(:,32);
V_grabz12 = data_V(:,1) - data_offset(1); %ץ��Z�����ѹ
V_grabx12 = data_V(:,2) - data_offset(2); %ץ��X�����ѹ
V_Fy14 = data_V(:, 3) - data_offset(3); %ǰ̨Y14��ѹ
V_Fy23 = data_V(:, 4) - data_offset(4); %ǰ̨Y23��ѹ
V_Fz1 = data_V(:,5) - data_offset(5); %ǰ̨Z1��ѹ
V_Fz2 = data_V(:,6) - data_offset(6); %ǰ̨Z2��ѹ
V_Fz3 = data_V(:,7) - data_offset(7); %ǰ̨Z3��ѹ
V_Fz4 = data_V(:,8) - data_offset(8); %ǰ̨Z4��ѹ.�����ʼ��Ľ������еĵ�ѹ����Ӧ������
V_Ry14 = data_V(:, 11) - data_offset(11); %��̨Y14��ѹ
V_Ry23 = data_V(:, 12) - data_offset(12); %��̨Y23��ѹ
V_Rz1 = data_V(:,13) - data_offset(13); %��̨z1��ѹ
V_Rz2 = data_V(:,14) - data_offset(14); %��̨z2��ѹ
V_Rz3 = data_V(:,15) - data_offset(15); %��̨z3��ѹ
V_Rz4 = data_V(:,16) - data_offset(16); %��̨z4��ѹ
F_Fz1 = (V_Fz1 ./3.611).*1000;
F_Fz2 = (V_Fz2 ./3.611).*1000;
F_Fz3 = (V_Fz3 ./3.611).*1000;
F_Fz4 = (V_Fz4 ./3.611).*1000; %��ֵת����ʽ������ʦ�ṩ
FZ = F_Fz1 + F_Fz2 + F_Fz3 + F_Fz4; % FZ��4�����������
F_Y14 = (V_Fy14./3.861).*1000;
F_Y23 = (V_Fy23./3.861).*1000;
FY = F_Y14 + F_Y23; %FY4����������ˮƽ��̨�����
Gz = (V_grabz12./3.899).*1000;
Gx = (V_grabx12./1.842).*1000;%��ץ�ֵ������������û�н��кϳɣ��Է���̫ȷ��
F_Rz1 = (V_Rz1 ./3.657).*1000;
F_Rz2 = (V_Rz2 ./3.657).*1000;
F_Rz3 = (V_Rz3 ./3.657).*1000;
F_Rz4 = (V_Rz4 ./3.657).*1000;
RZ = F_Rz1 + F_Rz2 + F_Rz3 + F_Rz4; %��̨��ֱ̨����
R_Y14 = (V_Ry14 ./3.864).*1000;
R_Y23 = (V_Ry23 ./3.864).*1000;
RY = R_Y14 + R_Y23; %��̨ƽ��̨�ӵ���
%�˲�filt
n = 2;
fs = 500;
Wn = 10/(fs/2);
[a, b] = butter(n, Wn);

%ǰ�Ŵ�ֱ����ǰ��ˮƽ����ǰ���� frontplate
qianjiao_horizontal = FZ .*(sin(10.2*pi/180)) + FY.*(cos(10.2*pi/180));
qianjiao_vertical = FZ .*(cos(10.2*pi/180)) - FY.*(sin(10.2*pi/180));
F_F = ((FZ).^2 + (FY).^2).^0.5;
%�˲�֮��_1
F_F_1 = filtfilt(a,b,F_F);
qianjiao_horizontal_1 = filtfilt(a,b,qianjiao_horizontal);
qianjiao_vertical_1 = filtfilt(a,b,qianjiao_vertical);

%��Ŵ�ֱ���ͺ��ˮƽ�� rearplate
houjiao_horizontal = RZ .*(sin(10.2*pi/180)) + RY.*(cos(10.2*pi/180));
houjiao_vertical = RZ .*(cos(10.2*pi/180)) - RY.*(sin(10.2*pi/180));
F_R = ((RZ).^2 + (RY).^2).^0.5;
F_R_1 = filtfilt(a,b,F_R);
houjiao_horizontal_1 = filtfilt(a,b,houjiao_horizontal);
houjiao_vertical_1 = filtfilt(a,b,houjiao_vertical);

%���ֵ���ֵGzΪ��ֱ��ˮ�淽��GxΪƽ����ˮ�淽��
zhuashou_vertical = (Gz).*(-1);
zhuashou_vertical_1 = filtfilt(a,b, zhuashou_vertical);
zhuashou_horizontal = Gx;
zhuashou_horizontal_1 = filtfilt(a,b, zhuashou_horizontal);

%����������ֱ�ڲ���̨  vertical and horizontal force
li_vertical = FZ + RZ;
li_horizontal = FY + RY; 
F_V = li_vertical.*(cos(10.2*pi/180)) - li_horizontal.*(sin(10.2*pi/180))+Gz;
F_H = li_vertical.*(sin(10.2*pi/180)) + li_horizontal.*(cos(10.2*pi/180))+Gx;
F_V_1 = filtfilt(a,b,F_V);
F_H_1 = filtfilt(a,b,F_H);

%integration
%�����ҳ���ʼʱ��ͽ���ʱ��
%����ʱ�����У�Ϊ������׼��
T = 0:0.002:10;
T = T';
d = size(F_H_1,1);
t = T(1:d, 1);
%�������ض����ݽ��б�׼��
%�����׼����
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

%���ֹ�8����,����������H_txt�е�˳�����
jifen1 = cumtrapz(t, qianjiao_horizontal_1);
jifen2 = cumtrapz(t, qianjiao_vertical_1);
jifen3 = cumtrapz(t, houjiao_horizontal_1);
jifen4 = cumtrapz(t, houjiao_vertical_1);
jifen5 = cumtrapz(t, zhuashou_vertical_1);
jifen6 = cumtrapz(t, zhuashou_horizontal_1);
jifen7 = cumtrapz(t, F_V_1);
jifen8 = cumtrapz(t, F_H_1);

%������� ouput data
write_name = ['/Users/wangshuaibo/Documents/ScriptsofShuai/Notes/ExampleData/KiSwim/��ֵ����/', filename_1{i, 1}];
H_txt = {'ǰ̨����','ǰ̨ˮƽ��','ǰ̨��ֱ��','��̨����','��̨ˮƽ��','��̨��ֱ��','ץ�ִ�ֱ��','ץ��ˮƽ��'...
    '��ֱ��','ˮƽ��', 'ʱ����','Gun'};
H_txt1 = {'ǰ̨ˮƽ������','ǰ̨��ֱ������','��̨ˮƽ������','��̨��ֱ������','ץ�ִ�ֱ������','ץ��ˮƽ������','��ֱ������','ˮƽ������'}
%��׼������
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
%Gun д��excel
xlswrite(write_name, gun , 'data', 'L2');
xlswrite(write_name, H_txt(12), 'data', 'L1');

%�����ǻ��ֵ�д�룬ǰ���������������
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





