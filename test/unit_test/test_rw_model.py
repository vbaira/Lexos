from lexos.receivers.rolling_windows_receiver import RWAFrontEndOptions, \
    WindowUnitType, RWATokenType, RWARatioTokenOptions, RWAWindowOptions,\
    RWAAverageTokenOptions
from lexos.models.rolling_windows_model import RollingWindowsModel, \
    RWATestOptions

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
                                       numerator_token="ta",
                                       denominator_token="ha"),
                                       average_token_options=None,
                                       passage_file_id=1,
                                       window_options=RWAWindowOptions
                                       (window_size=3, window_unit=
                                       WindowUnitType("letter")),
                                       milestone=None))

rw_ratio_model_one = RollingWindowsModel(test_option=test_ratio_count_one)
#---------------------------------------------------------------------------

# --------------------test by average count-----------------------------------
test_average_count_one = RWATestOptions(file_id_content_map=
                                      {0: "ha ha ha ha la ta ha",
                                       2: "la la ta ta da da ha",
                                       3: "ta da ha"
                                       },
                                      rolling_windows_options=
                                      RWAFrontEndOptions
                                      (ratio_token_options=None,
                                       average_token_options=RWAAverageTokenOptions("string"), tokens=["string"]),
                                       passage_file_id=1,
                                       window_options=RWAWindowOptions
                                       (window_size=3, window_unit=
                                       WindowUnitType("letter")),
                                       milestone=None))

rw_average_count_model_one = RollingWindowsModel\
    (test_option=test_average_count_one)
#---------------------------------------------------------------------------

print("DONE")

class TestRW:
    def test_get_rw_from_list:
