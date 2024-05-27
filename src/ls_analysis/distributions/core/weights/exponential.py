# -*- coding: utf-8 -*-
"""
Created on 2024/05/18

@author: brassbeat
"""
import pandas as pd


def get_weights(values: pd.Series, decay: float) -> pd.Series:
    ones = values.mask(values.notna(), 1)
    exponents = ones.sum() - ones.cumsum()
    denormalized_weights = exponents.rpow(decay).convert_dtypes()
    return denormalized_weights


def main():
    pass


if __name__ == "__main__":
    main()
