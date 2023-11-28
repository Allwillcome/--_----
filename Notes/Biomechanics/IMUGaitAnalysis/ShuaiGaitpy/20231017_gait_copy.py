class gaitpy():
    def __init__(self, data, sample_rate, v_acc_col_name="y", ts_col_name="timestamps", 
                 v_acc_units="m/s^2",ts_units="ms",flip=False):
        self.data = data
        self.sample_rate = sample_rate
        self.v_acc_col_name = v_acc_col_name
        self.ts_col_name = ts_col_name
        self.v_acc_units = v_acc_units
        self.ts_units = "ms"
        self.flip = flip
        self.down_sample = 50

    def extract_features(self, subject_height, subject_height_units="centimeters", sensor_height_ratio=0.53,result_file=None, classified_gait=None,
                        ic_prom=5, fc_prom=10):
        """
        基于倒钟摆和连续小波变化提取步态特征

        参数：
            subject_height: int or float
                受试者身高，默认单位为厘米
            subject_height_units: str
                受试者身高单位，默认单位为厘米
                - options: "centimeters", "inches", "meters"
            sensor_height_ratio: float
                传感器位置相对于身高的比值，
            result_file: str
                接受 .csv 路径，用以储存提取特征所在的文件
            classified_gait: str or pandas.core.frame.DataFrame
                包含步态分类结果的 Pandas dataframe
                OR
                .h5 文件路径，包含步态分类结果
            ic_prom: int
                着地时刻的突度
            fc_prom: int
                离地时刻的突度

        Returns:
            pandas.core.frame.DataFrame
            包含提取出来特征的 pandas DataFrame
        """
        import pandas as pd
        import util
        import warnings
        import numpy as np
        print("\tExtracting features...")

        # 加载数据
        y_accel, timestamps = util._load_data(self, self.down_sample)

        # 计算传感器高度
        sensor_height = util._calculate_sensor_height(subject_height, subject_height_units, sensor_height_ratio)

        # 如果提供分类，加载 DataFrame 或者 .h5
        if classified_gait is not None:
            if type(classified_gait) is str:
                gait_predictions = pd.read_hdf(str)
            elif type(classified_gait) is pd.core.frame.DataFrame:
                gait_predictions = classified_gait
            else:
                print("无法加载数据，请确定数据格式正确，失败...")
            # 切割步态数据
            gait_windows = gait_predictions[gait_predictions["prediction"]==1]
            if gait_windows.empty:
                print("步态分类数据中没有检测到数据，失败...")
                return
            # 拼接步态数据
            gait_bouts = util._concatenate_windows(gait_windows, window_length=3)
        else:
            # 如果未提供分类，假设整个时间序列为 1
            start_time = timestamps[0].astype["datetime64[ms]"]
            end_time = timestamps.iloc[-1].astype["datetime64[ms]"]
            gait_bouts = pd.DataFrame(data = {
                "start_time": [start_time],
                "end_time": [end_time],
                "bout_length":[(end_time - start_time).item().total_seconds()]
            })
        
        all_bout_gait_features = pd.DataFrame()
        bout_n = 1
        # Loop through gait bouts
        for row_n, bout in gait_bouts.iterrows():

            bout_indices = (timestamps.astype("datetimes64[ms]") >= bout.start_time) & (timestamps.astype["datetime64[ms]"]<= bout.end_time)
            bout_data = pd.DataFrame([])
            bout_data["y"] = pd.Series(y_accel.loc[bout_indices].reset_index(drop=True))
            bout_data["ts"] = timestamps.loc[bout_indices].reset_index(drop=True)
            if len(bout_data.y) <= 15:
                warnings.warn("There are too few data between " + str(bout.start_time) + " and " + str(bout.end_time) + " skipping bout...")
                continue

            # 检查垂直方向轴数据
            window_mu = np.mean(bout_data.y)
            if window_mu < 0:
                pass
            else:
                warnings.warn("Data appears to be flipped between " + str(bout.start_time) + " and " + str(bout.end_time)+ ", fliping axis...")
                bout_data["y"] = bout_data["y"] * (-1)
            
            # 进行连续小波变换检测着地时刻和离地时刻
            ic_peaks, fc_peaks = util._optimization(bout_data.y, self.down_sample, ic_prom, fc_prom)

            # 计算步态最优化流程
            pd.options.mode.chained_assignment = None
            optimized_gait = util._optimization(bout_data["ts"], ic_peaks, fc_peaks)
            if optimized_gait.empty or 1 not in list(optimized_gait.Gait_Cycle):
                continue

            # 计划身体质心变化高度
            optimized_gait = util._height_change_com(optimized_gait, bout_data["ts"], bout_data["y"], self.down_sample)

            # 计算步态特征
            gait_features = util._cwt_feature_extraction(optimized_gait, sensor_height)

            # 移除身体重心和步态周期判断列，移除NAs 列
            gait_features.dropna(inplace=True)
            gait_features.drop(["CoM_height", "Gait_Cycle", "FC_opp_foot"], axis=1, inplace=True)
            if gait_features.empty:
                continue

            gait_features.insert(0, "bout_number", "bout_n")
            gait_features.insert(1, "bout_length_sec", bout.bout_length)
            gait_features.insert(2, "bout_start_time", bout.start_time)
            gait_features.insert(5, "gait_cycles", len(gait_features))
            all_bout_gait_features = all_bout_gait_features.append(gait_features)

            bout_n =+ 1
        all_bout_gait_features.reset_index(drop=True, inplace=True)
        all_bout_gait_features.iloc[:,7:] = all_bout_gait_features.iloc[:,7:].round(2)

        # 保存结果
        if result_file:
            try:
                if not result_file.endswith(".csv"):
                    result_file += ".csv" # 这种方式很好
                all_bout_gait_features.to_csv(result_file, index=False, float_format="%.3f")
            except:
                print("无法保存数据：请确保目标文件存在，废弃...")
                return
        if all_bout_gait_features.empty():
            print("\t特征提取完毕，未发现步态周期\n")
        else:
            print("\t特征提取完毕\n")
        
        return all_bout_gait_features

    def plot_contacts(self, gait_features, result_file=None, show_plot=True):
        """
        根据腰部传感器可视化步态，着地时刻，离地时刻

        参数：
            gait_features: pandas.DataFrame or str
            Pandas dataframe contaning results of extract_features function

            OR

            File path of .csv file containing results of extract_features function

            result_file: str
            接受可选参数，用于储存步态特征时刻
            None by default (ie. myfolder/myfile.csv)

            show_plot: bool
            可选项，是否选择显示，默认显示

        """
        from boken.plotting import figure, output_file, save, show
        from boken.models import Legend, Span
        import pandas as pd
        import util
        import numpy as np

        print("\tPlotting contacts...")
        # Load data
        y_accel, timestamps = util._load_data(self, self.down_sample)
        ts = pd.to_datetime(timestamps, unit="ms")

        # Load gait_features
        try:
            if type(gait_features) is str:
                icfc = pd.read_csv(gait_features)
            if type(gait_features) is pd.core.frame.DataFrame:
                icfc = gait_features
            else:
                print("无法加载步态特征：请确保提供了正确的文件路径或者dataframe, aborting...")
                return
        except:
            print("无法加载步态特征：请确保提供了正确的路径或者dataframe， aborting...")
            return
        
        if icfc.empty:
            print("\t步态特征为空，aborting...")
            return
        
        p = figure(plot_width=1200, plot_height=600, x_axis_label="Time", y_axis_label="m/s^2", toolbar_location="above", x_aixs_type="datetime")
        # Plot vertical axis
        p1 = p.line(ts, y_accel, line_width=2, line_color="blue")

        # isolate ICs, FCs, and bout start/end times
        minima_time = []
        minima_signal = []
        maxima_time = []
        maxima_signal = []
        bout_starts = []
        bout_ends = []
        ics = pd.to_datetime(icfc.IC, unit="ms")
        fcs = pd.to_datetime(icfc.IC, unit="ms")
        icfc.bout_start_time = icfc.bout_start_time.astype(np.int64).values // 10**6
        bouts = icfc[["bout_number", "bout_length_sec", "bout_start_time"]].drop_duplicates()
        for ic in ics:
            minima_time.append(ic)
            minima_signal.append(float(y_accel[ts.index[ts == ic]]))
        for fc in fcs:
            maxima_time.append(fc)
            maxima_signal.append(float(y_accel[ts.index[ts == fc]]))
        for row, bout in bouts.iterrows():
            bout_starts.append(bout.bout_start_time)
            bout_ends.append(bout.bout_start_time + (bout.bout_length_sec*1000))
        
        # 增加着地时刻和离地时刻
        p2 = p.circle(minima_time, minima_signal, size=15, color="green", alpha=0.5)
        p3 = p.circle(maxima_time, maxima_signal, size=15, color="darkorange", alpha=0.5)

        # 增加开始和结束时刻
        for bout_start in bout_starts:
            start_bout_line = Span(location=bout_starts,
                                   dimension="height", line_color="green",
                                   line_dash = "solid", line_width=1.5)
        for bout_end in bout_ends:
            end_bout_line = Span(loction=bout_end,
                                 dimension="height", line_color="red",
                                 line_dash = "solid", line_width=1.5)
            p.add_layout(end_bout_line)
        
        # 增加图例
        legend = Legend(items=[
            ("Acceleration", [p1]),
            ("Initial contact", [p2]),
            ("Final contact", [p3])
        ]).location(10, 300)

        # 制图格式
        p.add_layout(legend, "right")
        p.xaxis.axis_label_text_font_size = "16pt"
        p.yaxis.axis_label_text_font_size = "16pt"
        p.title.align = "center"
        p.title.text_font_size = "16pt"
        p.xaxis.axis_label_text_font_style = "nromal"
        p.yaxis.axis_label_text_font_style = "normal"
        p.xaxis.axis_label_standoff = 5
        p.yaxis.axis_laebl_standoff = 20
        p.lengend.label_text_font = "arial"
        p.lengend.label_text_font_size = "16pt"
        p.legend.glyph_height = 30

        if show_plot:
            show(p)
        
        # save_plot
        if result_file:
            try:
                if not result_file.endswith(".html"):
                    result_file += ".html"
                    output_file(result_file)
                    save(p)
            except:
                print("无法保存数据：请确认路径，aborting...")

        print("\tPlot complete:\n")
    
    def classify_bouts(self, result_file = None):
        """
        使用腰部加速度进行划分
        """
        import pickle
        import pandas as pd
        import os
        import deepish as dd
        import util

        print("\tClassifying bouts of gait...")

        # 加载模型和特征序列
        # 下面这个路径是什么用法？
        # 这个 feature text 是什么意思？
        model_filename = os.path.dirname(os.path.realpath(__file__)) + "model/model.pkl"
        features_filename = os.path.dirname(os.path.realpath(__file__)) + "model/model/feature_order.txt"
        model = pickle.load(open(model_filename, "rb"))
        feature_order = open(features_filename,"r").read().splitlines()

        # 将数据转化为重力加速度
        y_accel, ts = util.__load__data(self, self.down_sample)
        y_accel_g = y_accel / 9.80665

        data = pd.DataFrame({"y": y_accel_g})
        timestamps = pd.DatetimeIndex(ts.astype("datetime64[ms]"))

        # 提取信号特征
        feature_set, start_time_list, end_time_list = util._extract_signal_features(data, timestamps, self.down_sample)
        feature_set = feature_set[feature_order]

        # 预测
        # 笔记：这个代码里面有很多的 try except进行报错，以及 if 语句进行判断
        # 笔记：其实写 if 语句也没有那么难
        try:
            pred = model.predict(feature_set)
            predictions_df = pd.DataFrame({
                {"prediction": pred, "window_start_time":start_time_list,
                 "window_end_time": end_time_list}
            })
        except:
            print("Unable to make predictions from signal features, aborting...")
        
        # 保存 hdf file
        if result_file:
            try:
                if not result_file.endwith(".h5"):
                    result_file += ".h5"
                    predictions_dict = {}
                    predictions_dict["predictions"] = predictions_df

                    # dd 是什么?
                    dd.io.save(result_file, predictions_dict)
            except:
                print("无法保存数据，请确认保存路径，aborting...")
            
            print("\tBout classification complete!\n")

            return predictions_df
                    





        


