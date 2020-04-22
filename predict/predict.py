import sys
import os
sys.path.append(os.pardir)

import pmdarima as pm
from pmdarima.model_selection import cross_val_score
import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from tqdm import tqdm

from config import Config


def predict_runner(name: str, df: pd.DataFrame, n_forecasts: int=1) -> str:
    """ Predict the next race time for a runner

    Arguments:
        name {str} -- Runner name
        df {pd.DataFrame} -- DataFrame of races

    Keyword Arguments:
        n_forecasts {int} -- number of steps ahead (default: {1})

    Returns:
        str -- The prediction and confidence intervals of the next race time
    """
    runner_df = df.loc[df.name.str.contains(name, case=False)]
    if runner_df.empty:
        return
    minutes = runner_df.time.dt.seconds / 60.0
    model = pm.auto_arima(minutes, seasonal=False, suppress_warnings=True)
    pred, conf_int = model.predict(n_forecasts, return_conf_int=True)
    cv_score = cross_val_score(model, minutes, scoring='mean_absolute_error')
    mean_cv_score = np.mean(cv_score)

    def formatter(num: int) -> str:
        return str(datetime.timedelta(minutes=num)).split('.')[0]

    pred_format = formatter(pred[0])
    conf_int_format = [formatter(x) for x in conf_int[0]]
    mean_cv_score_format = formatter(mean_cv_score)
    pred_string = (f'Results for {runner_df.name.unique()[0]}\n'
                   f'The prediction for the next 42 km race'
                   f' is {pred_format} with 95 % confidence'
                   f' interval ({conf_int_format[0]},'
                   f' {conf_int_format[1]})\n'
                   f'The average cross validation error score is'
                   f' {mean_cv_score_format}.\n'
                   f'Error is measured using Mean Absolute Error (MAE)')
    pred_string = pred_string.split('\n')
    return pred_string


def main() -> None:
    """Predict race times for all runners
    """
    engine = create_engine(Config.SQL_ALCHEMY_DATABASE_URI)
    race_df = pd.read_sql_table('race', con=engine)

    for name in race_df.name.unique():
        print(f'Predictions for {name}')
        print(predict_runner(name, race_df))


if __name__ == '__main__':
    main()
