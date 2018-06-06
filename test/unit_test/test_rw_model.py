from lexos.receivers.rolling_windows_receiver import RWAFrontEndOptions, \
    WindowUnitType, RWATokenType, RWARatioTokenOptions, RWAWindowOptions, \
    RWAAverageTokenOptions
from lexos.models.rolling_windows_model import RollingWindowsModel, \
    RWATestOptions
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot

# --------------------test by ratio count-----------------------------------
test_ratio_count_one = RWATestOptions(file_id_content_map=
                                      {0: "ha ha ha ha la ta ha",
                                       2: "la la ta ta da da ha",
                                       3: "ta da ha"
                                       },
                                      rolling_windows_options=
                                      RWAFrontEndOptions
                                      (ratio_token_options=RWARatioTokenOptions
                                      (token_type=RWATokenType("string"),
                                       numerator_token="t",
                                       denominator_token="a"),
                                       average_token_options=None,
                                       passage_file_id=0,
                                       window_options=RWAWindowOptions
                                       (window_size=3, window_unit=
                                       WindowUnitType("letter")),
                                       milestone=None))

rw_ratio_model_one = RollingWindowsModel(test_option=test_ratio_count_one)

# noinspection PyProtectedMember
rw_ratio_windows = rw_ratio_model_one._get_windows()
# noinspection PyProtectedMember
rw_ratio_model_one.get_rwa_graph()
# ---------------------------------------------------------------------------
# --------------------test by average count-----------------------------------
test_average_count_one = RWATestOptions(file_id_content_map=
                                        {0: "ha ha ha ha la ta ha",
                                         2: "la la ta ta da da ha",
                                         3: "ta da ha"
                                         },
                                        rolling_windows_options=
                                        RWAFrontEndOptions
                                        (ratio_token_options=None,
                                         average_token_options=
                                         RWAAverageTokenOptions
                                         (token_type=RWATokenType("string"),
                                          tokens=["string"]),
                                         passage_file_id=1,
                                         window_options=RWAWindowOptions
                                         (window_size=3, window_unit=
                                         WindowUnitType("letter")),
                                         milestone=None))
rw_average_count_model_one = RollingWindowsModel \
    (test_option=test_average_count_one)
# ---------------------------------------------------------------------------


# noinspection PyProtectedMember
class TestRatio:
    def test_get_windows(self):
        assert (rw_ratio_model_one._get_windows() ==
        ['ha ', 'a h', ' ha', 'ha ', 'a h', ' ha', 'ha ', 'a h', ' ha',
         'ha ', 'a l', ' la', 'la ', 'a t', ' ta', 'ta ', 'a h']).all()

    def test_token_ratio_windows(self):
        pd.testing.assert_series_equal(
            left=rw_ratio_model_one._find_token_ratio_in_windows(
                rw_ratio_windows),
            right=pd.Series(
                data=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                      0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0],
                ), check_names=False)

    def test_get_token_ratio_graph(self):
        assert rw_ratio_model_one._get_token_ratio_graph()['type'] == \
               'scattergl'
        assert (rw_ratio_model_one._get_token_ratio_graph()['x'] ==
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                 16]).all()
        assert rw_ratio_model_one._get_token_ratio_graph()['mode'] == 'lines'
        assert rw_ratio_model_one._get_token_ratio_graph()['name'] == 't / a'


print("DONE")
