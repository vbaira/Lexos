from lexos.processors.prepare.cutter import cut_by_characters


class TestCutByCharacters:
    def test_empty_string(self):
        assert cut_by_characters(text="", chunk_size=10, overlap=10,
                                 last_prop=0) == [""]

    def test_string_chunk_size(self):
        assert cut_by_characters(text="ABABABAB", chunk_size=10, overlap=0,
                                 last_prop=0) == ["ABABABAB"]
        assert cut_by_characters(text="ABABABAB", chunk_size=2, overlap=0,
                                 last_prop=0) == ["AB", "AB", "AB", "AB"]
        assert cut_by_characters(text="ABABABAB", chunk_size=3, overlap=0,
                                 last_prop=0) == ["ABA", "BAB", "AB"]

    def test_string_overlap(self):
        assert cut_by_characters(text="WORD", chunk_size=2, overlap=0,
                                 last_prop=0) == ["WO", "RD"]
        assert cut_by_characters(text="ABBA", chunk_size=2, overlap=1,
                                 last_prop=0) == ["AB", "BB", "BA"]
        assert cut_by_characters(text="ABCDE", chunk_size=3, overlap=2,
                                 last_prop=0) == ["ABC", "BCD", "CDE"]
        assert cut_by_characters(text="ABCDEF", chunk_size=4, overlap=3,
                                 last_prop=0) == ["ABCD", "BCDE", "CDEF"]

    def test_string_last_prop(self):
        assert cut_by_characters(text="ABABABABABA", chunk_size=5, overlap=0,
                                 last_prop=0.2) == ["ABABA", "BABAB", "A"]
        assert cut_by_characters(text="ABABABABABA", chunk_size=5, overlap=0,
                                 last_prop=0.21) == ["ABABA", "BABABA"]

























from lexos.helpers.general_functions import make_preview_from
from lexos.helpers.general_functions import merge_list


def test_make_preview():
    assert make_preview_from(" ") == " "
    assert make_preview_from("This is a test") == "This is a test"


class TestMergeList:
    def test_merge_list_empty_dict(self):
        assert merge_list([{}, {}]) == {}
        assert merge_list([{"XX": 20}, {}]) == {"XX": 20}

    def test_merge_list_empty(self):
        assert merge_list([]) == {}

    def test_merge_list_regular(self):
        assert merge_list([{"Q": 10}, {"Q": 90}]) == {"Q": 100}
        assert merge_list([{"A": 12}, {"B": 20}]) == {"A": 12, "B": 20}
        assert merge_list([{"A": 12},
                           {"B": 12, "C": 12},
                           {"A": 1, "B": 2, "C": 3}]) == \
               {"A": 13, "B": 14, "C": 15}
