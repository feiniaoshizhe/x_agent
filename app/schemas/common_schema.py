"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/12 09:37
Description:
FilePath: common_schema
"""
import enum


class IGenderEnum(str, enum.Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"