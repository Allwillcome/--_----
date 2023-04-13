# %%
import numpy as np
from scipy.spatial.transform import Rotation

def transform_euler_angles(quaternion):
    """
    使用四元数转换欧拉角，并将其转换为特定形式的欧拉角。
    
    Args:
        quaternion (list): 长度为4的列表，表示四元数。
    
    Returns:
        list: 长度为3的列表，表示经过转换的欧拉角。
    """
    # 使用四元数转换欧拉角
    rotation = Rotation.from_quat(quaternion)
    euler_angles = rotation.as_euler("zyx", degrees=True)
    
    # 将欧拉角转换为特定形式
    # 仅使用 transform 转化，得到的数据不正确，需要进一步转化
    # 第一个角度不需要变化，第二个角度前面加负数，第三个是和180互补加负数
    transformed_angles = np.round([euler_angles[0], -euler_angles[1], -(180 - euler_angles[2])], 6)
    
    return transformed_angles

# %%



