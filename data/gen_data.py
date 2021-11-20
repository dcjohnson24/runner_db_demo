import os
import sys
import pandas as pd
import numpy as np
import datetime
from sqlalchemy.exc import IntegrityError

from os.path import dirname, abspath

path = dirname(dirname(abspath(__file__)))
sys.path.append(path)

from app.models import Race
from app import db, create_app


def gen_run_time(time: str, num_races: int=10) -> pd.Series:
    """Generate random marathon times for runners

    Arguments:
        time {str} -- The average marathon time

    Keyword Arguments:
        size {int} -- The number of races (default: {10})

    Returns:
        pd.Series -- [description]
    """
    np.random.seed(485859)
    dt = datetime.datetime.strptime(time, '%H:%M')
    minutes = dt.minute
    hours = dt.hour
    time_in_min = (datetime.timedelta(hours=hours, minutes=minutes)
                   .total_seconds() / 60.0)
    race_times = np.random.normal(time_in_min, scale=15, size=num_races)
    return pd.to_timedelta(race_times, 'm')


def load_df_orm(df: pd.DataFrame, table: db.Model) -> None:
    """Load table into SQL using ORM

    Arguments:
        df {pd.DataFrame} -- DataFrame matching the
            schema of the table class
        table {db.Model} -- the ORM model class
    """
    for _, row in df.iterrows():
        runner = table(**row.to_dict())
        try:
            db.session.add(runner)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
    db.session.commit()


def gen_data(num_races: int=10) -> pd.DataFrame:
    """Create a dataframe for three runners with a specified number of races

    Keyword Arguments:
        num_races {int} -- number of races per runner (default: {10})

    Returns:
        pd.DataFrame -- DataFrame containing runner races corresponding
                        to Race table in database
    """
    return pd.DataFrame(
        {'pos': np.random.randint(400),
         'name': (['Lethabo Ndlovu'] * num_races + ['Bandile Nkosi']
                  * num_races + ['Karabo Khumalo'] * num_races),
         'race': [f'Race{i}' for i in range(num_races)] * 3,
         'time': np.concatenate(
             (gen_run_time('03:47', num_races=num_races),
              gen_run_time('04:31', num_races=num_races),
              gen_run_time('4:10', num_races=num_races))
         ),
         'sex': ['male'] * num_races + ['male'] * num_races + ['female'] * num_races,
         'age': [37] * num_races + [55] * num_races + [44] * num_races,
         'cat': ['senior'] * num_races + ['veteran'] * num_races + ['veteran'] * num_races,
         'distance_km': [42] * num_races * 3,
         'race_year': [2019] * num_races * 3}
    )


def main() -> None:
    """Generate data and load to db
    """
    df = gen_data()
    app = create_app()
    app.app_context().push()

    load_df_orm(df, Race)


if __name__ == '__main__':
    main()

