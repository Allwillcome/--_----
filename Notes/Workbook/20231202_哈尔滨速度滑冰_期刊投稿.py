# %% [markdown]
# # 处理速度滑冰数据

# %%
import pandas as pd
import os
import numpy as np

# %%
# 选择参数
traget_datas = ["Joint Angles ZXY", "Segment Angular Velocity"]
# 选择直道或者弯道
road_type = "直道"
# 填写0，或者1
target_data = traget_datas[1]

# %%
# 文件路径设置
excel_dir = "/Volumes/ESD-USB/哈尔滨滑冰测试/excel"
record_excel_path = "/Volumes/ESD-USB/哈尔滨滑冰测试/RecordData/20231201_短道速滑特征时刻表_期刊投稿.xlsx"

# %%
# 读取记录数据的excel 表格
excelfile = pd.ExcelFile(record_excel_path)
excelfile.sheet_names
record_df = pd.read_excel(record_excel_path, sheet_name="特征时刻")

# %% [markdown]
# ## 构建表头

# %%
# 构建表格表头
joints = [" Hip ", " Knee ", " Ankle "]
segments = [" Upper Leg ", " Lower Leg ", " Foot "]
seg_types = ["Left", "Right"]
seg_axis = ["x", "y", "z"]
joint_orientations = ["Flexion/Extension","Abduction/Adduction", "Internal/External Rotation"]
joint_orientations_ankle = ["Dorsiflexion/Plantarflexion","Abduction/Adduction", "Internal/External Rotation"]

# 构建列表头名称
def CreateSelectColumns(seg_type,target_data, segments, joints, joint_orientations, joint_orientations_ankle, seg_axis):
    if target_data == "Joint Angles ZXY":
        select_seg_types_colmuns = [seg_type + joint + seg_orientation
                    for joint in joints
                    for seg_orientation in ((joint_orientations_ankle if joint.strip()=="Ankle" else joint_orientations))]
    else:
        select_seg_types_colmuns = [seg_type + segment + seg_ax
                    for segment in segments
                    for seg_ax in seg_axis]
    return select_seg_types_colmuns

# 获取列表名称
Left_select_columns = CreateSelectColumns("Left",target_data, segments, joints, joint_orientations, joint_orientations_ankle, seg_axis)
Right_select_columns = CreateSelectColumns("Right",target_data, segments, joints, joint_orientations, joint_orientations_ankle, seg_axis)


# %% [markdown]
# ## 计算特征时刻

# %%
# 计算特征时刻数据
def GetEventData(target_data_df, select_columns, contact_event, off_event):
    # 触冰时刻
    data_concat_event = target_data_df[select_columns].iloc[contact_event]
    data_off_event = target_data_df[select_columns].iloc[off_event]

    # 离冰时刻
    frame = [data_concat_event, data_off_event]
    result_event_data = pd.concat(frame, axis=0)

    return result_event_data

# %%
# 确定蹬冰开始和结束时的特征值
def GetEachTestResult(record_df, target_df, record_row, road_number, road_type):
    
    # 确定左侧脚触冰和离冰时刻
    Left_contact_event = record_df.loc[record_row, f"{road_number}{road_type}蹬冰开始-左"]
    Left_off_event = record_df.loc[record_row, f"{road_number}{road_type}蹬冰结束-左"]
    
    # 确定右脚触冰和离冰时刻
    Right_contact_event = record_df.loc[record_row, f"{road_number}{road_type}蹬冰开始-右"]
    Right_off_event = record_df.loc[record_row, f"{road_number}{road_type}蹬冰结束-右"]

    # 获取特征时刻对应数据
    Left_event_data = GetEventData(target_df, Left_select_columns, Left_contact_event, Left_off_event)
    Right_event_data = GetEventData(target_df, Right_select_columns, Right_contact_event, Right_off_event)

    frame = [Left_event_data, Right_event_data]
    Result_each_test = pd.concat(frame, axis=0)

    return Result_each_test

# %%
# 计算所有人所有时刻数据关节角度/角速度数据
result_one_file_total = pd.DataFrame()
for record_row, row in record_df.iterrows():
    date = row["日期"]
    test_number = row["测试序号"]
    name = row["姓名"]
    xsens_number = row["实际xsens号"]

    # 拼接文件名
    excel_fname = f"{date}_{test_number}_{name}-00{xsens_number}.xlsx"

    excel_path = os.path.join(excel_dir,excel_fname)
    target_data_df = pd.read_excel(excel_path, sheet_name=target_data)
    # angle_df 
    # 读取record_df 一行数据得到的结果
    attribute_info = record_df.loc[record_row, ["姓名", "穿鞋", "xsens号","实际xsens号"]]

    Result_test_1 = GetEachTestResult(record_df, target_data_df, record_row, 1, road_type)
    Result_test_1_info = pd.concat([attribute_info, Result_test_1])
    Result_test_2 = GetEachTestResult(record_df, target_data_df, record_row, 2, road_type)
    Result_test_2_info = pd.concat([attribute_info, Result_test_2])
    frame = [Result_test_1_info, Result_test_2_info]
    result_one_file = pd.concat(frame, axis=1)
    result_one_file_total = pd.concat([result_one_file_total, result_one_file], axis=1)

# %%
# 查看结果
result_excel_dir = "/Volumes/ESD-USB/哈尔滨滑冰测试/ResultData"
result_excel_fname = f"{road_type}_{target_data}_蹬冰离冰_raw.xlsx"
result_excel_path = os.path.join(result_excel_dir, result_excel_fname)
# 保存到 Excel（转置后再保存）
result_one_file_total.T.to_excel(result_excel_path, index=False)
print(f"已完成：{result_excel_fname}")

# %% [markdown]
# ## 最大角度和角速度

# %%
# 计算最大值
def GetPhaseMaxData(target_data_df, select_columns, phase_start_event, phase_end_event):
    # 确定开始和结束时的数据
    phase_max_data = target_data_df[select_columns].iloc[phase_start_event : phase_end_event].max()

    return phase_max_data

# 计算特定阶段最大值
def GetEachTestPhaseMax(record_df, target_df, record_row, road_number, road_type):
    
    # 确定左侧脚开始和结束时刻
    Left_phase_start = record_df.loc[record_row, f"{road_number}{road_type}开始"]
    Left_phase_end = record_df.loc[record_row, f"{road_number}{road_type}结束"]
    
    # 确定右侧脚开始和结束时刻
    Right_phase_start = record_df.loc[record_row, f"{road_number}{road_type}开始"]
    Right_phase_end = record_df.loc[record_row, f"{road_number}{road_type}结束"]

    # 获取左右脚
    Left_phase_data = GetPhaseMaxData(target_df, Left_select_columns, Left_phase_start, Left_phase_end)
    Right_phase_data = GetPhaseMaxData(target_df, Right_select_columns, Right_phase_start, Right_phase_end)

    frame = [Left_phase_data, Right_phase_data]
    Result_each_test = pd.concat(frame, axis=0)

    return Result_each_test

# %%
# 计算所有人的数据
result_max_one_file_total = pd.DataFrame()
for record_row, row in record_df.iterrows():
    date = row["日期"]
    test_number = row["测试序号"]
    name = row["姓名"]
    xsens_number = row["xsens号"]

    # 拼接文件名
    excel_fname = f"{date}_{test_number}_{name}-00{xsens_number}.xlsx"

    excel_path = os.path.join(excel_dir,excel_fname)
    target_data_df = pd.read_excel(excel_path, sheet_name=target_data)
    # angle_df 
    # 读取record_df 一行数据得到的结果
    attribute_info = record_df.loc[record_row, ["姓名", "穿鞋", "xsens号","实际xsens号"]]

    Result_test_1 = GetEachTestPhaseMax(record_df, target_data_df, record_row, 1, road_type)
    Result_test_1_info = pd.concat([attribute_info, Result_test_1])
    Result_test_2 = GetEachTestPhaseMax(record_df, target_data_df, record_row, 2, road_type)
    Result_test_2_info = pd.concat([attribute_info, Result_test_2])
    
    frame = [Result_test_1_info, Result_test_2_info]
    result_max_one_file = pd.concat(frame, axis=1)
    result_max_one_file_total = pd.concat([result_max_one_file_total, result_max_one_file], axis=1)

# %%
# 查看结果
result_excel_dir = "/Volumes/ESD-USB/哈尔滨滑冰测试/ResultData"
result_excel_fname = f"速度滑冰_{road_type}_{target_data}_最大值_raw.xlsx"
result_excel_path = os.path.join(result_excel_dir, result_excel_fname)
# 保存到 Excel（转置后再保存）
result_max_one_file_total.T.to_excel(result_excel_path, index=False)
print(f"已完成：{result_excel_fname}")


