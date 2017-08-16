from lexos.helpers.error_messages import NOT_ONE_REPLACEMENT_COLON_MESSAGE, \
    REPLACEMENT_RIGHT_OPERAND_MESSAGE
from lexos.helpers.exceptions import LexosException
from lexos.processors.prepare.scrubber import replacement_handler, \
    get_remove_whitespace_map, make_replacer, get_remove_punctuation_map, \
    get_remove_digits_map, get_all_punctuation_map, delete_words, \
    handle_gutenberg, split_input_word_string, \
    get_special_char_dict_from_file, process_tag_replace_options, \
    scrub_select_apos, consolidate_hyphens, consolidate_ampers, \
    merge_file_and_manual_strings, remove_stopwords, keep_words
from test.helpers import special_chars_and_punct as chars, gutenberg as guten


class TestGetSpecialCharDictFromFile:

    def test_get_special_char_dict_from_file(self):
        assert get_special_char_dict_from_file(mode="MUFI-3") == chars.MUFI3
        assert get_special_char_dict_from_file(mode="MUFI-4") == chars.MUFI4
        # This option should be processed by handle_special_characters() only
        try:
            get_special_char_dict_from_file(mode="doe-sgml")
        except ValueError:
            pass
        else:
            raise AssertionError
        try:
            get_special_char_dict_from_file(mode="MADEUP-6")
        except ValueError:
            pass
        else:
            raise AssertionError


# handle_special_characters


class TestMakeReplacer:
    not_special_string = "This string contains no special chars?!\nWow."

    def test_make_replacer_doe_sgml(self):
        r = make_replacer(replacements=chars.DOE_SGML)
        assert r(self.not_special_string) == self.not_special_string
        assert r(chars.DOE_SGML_KEYS) == chars.DOE_SGML_VALS
        assert r(
            "Text. &omacron;Alternating&t;? &lbar;\nWith &bbar; special "
            "characters!&eacute;;") == \
            "Text. ōAlternatingþ? ł\nWith ƀ special characters!é;"

    def test_make_replacer_early_english_html(self):
        r = make_replacer(replacements=chars.EE_HTML)
        assert r(self.not_special_string) == self.not_special_string
        assert r(chars.EE_HTML_KEYS) == chars.EE_HTML_VALS
        assert r(
            "Text. &ae;Alternating&E;? &gt;\nWith &#540; special "
            "characters!&#383;;") == \
            "Text. æAlternatingĘ? >\nWith Ȝ special characters!ſ;"

    def test_make_replacer_mufi_3(self):
        r = make_replacer(replacements=chars.MUFI3)
        assert r(self.not_special_string) == self.not_special_string
        assert r(chars.MUFI3_KEYS) == chars.MUFI3_VALS
        assert r(
            "Text. &tridotdw;Alternating&AOlig;? &ffilig;\nWith &nlrleg; "
            "special characters!&afinslig;;") == \
            "Text. ∵AlternatingꜴ? ﬃ\nWith ƞ special characters!\uefa4;"

    def test_make_replacer_mufi_4(self):
        r = make_replacer(replacements=chars.MUFI4)
        assert r(self.not_special_string) == self.not_special_string
        assert r(chars.MUFI4_KEYS) == chars.MUFI4_VALS
        assert r(
            "Text. &llhsqb;Alternating&OBIIT;? &aeligdotbl;\nWith &circledot; "
            "special characters!&shy;;") == \
            "Text. ⸤AlternatingꝊ? \ue436\nWith ◌ special characters!\xad;"

    def test_make_replacer_other(self):
        # Note that make_replacer() is currently only called within
        # handle_special_characters(), which itself is only called if neither
        # the text field nor the file upload are used in the special characters
        #  menu on the front end.
        # That means these test cases cannot occur under normal usage, but
        # the fact make_replacer() still works is reassuring
        r = make_replacer(
            replacements={'a': 'z', 'e': 'q', 'i': 'w', 'o': 'p', 'u': 'x'})
        assert r("ythklsv") == "ythklsv"
        assert r("aeiou") == "zqwpx"
        assert r("Jklt. aghscbmtlsro? e\nLvdy u jgdtbhn srydvlnmfk!i;") == \
            "Jklt. zghscbmtlsrp? q\nLvdy x jgdtbhn srydvlnmfk!w;"


class TestReplacementHandlerAlone:
    test_string = "Test string is testing"

    def test_not_lemma_normal(self):
        assert replacement_handler(
            text=self.test_string, replacer_string="s:f", is_lemma=False) == \
            "Teft ftring if tefting"
        assert replacement_handler(
            text=self.test_string, replacer_string="i,e:a", is_lemma=False) \
            == "Tast strang as tastang"
        assert replacement_handler(
            text=self.test_string, replacer_string="q:z", is_lemma=False) == \
            self.test_string
        assert replacement_handler(
            text=self.test_string, replacer_string="t:l", is_lemma=False) == \
            "Tesl slring is lesling"
        assert replacement_handler(
            text=self.test_string, replacer_string="t:t", is_lemma=False) == \
            self.test_string
        assert replacement_handler(
            text=self.test_string, replacer_string=" r : t ", is_lemma=False)\
            == "Test stting is testing"
        assert replacement_handler(
            text=self.test_string, replacer_string="e:b \n i:o ",
            is_lemma=False) == "Tbst strong os tbstong"
        assert replacement_handler(
            text=self.test_string, replacer_string="n:t\nt:x", is_lemma=False)\
            == "Tesx sxrixg is xesxixg"
        assert replacement_handler(
            text=self.test_string, replacer_string="T,e,s,t,r,i,n,g:p\np:q",
            is_lemma=False) == "qqqq qqqqqq qq qqqqqqq"

    def test_not_lemma_incomplete_replacer(self):
        assert replacement_handler(
            text=self.test_string, replacer_string="g:", is_lemma=False) == \
            "Test strin is testin"
        assert replacement_handler(
            text=self.test_string, replacer_string=":", is_lemma=False) == \
            self.test_string
        assert replacement_handler(
            text=self.test_string, replacer_string=":k", is_lemma=False) == \
            "kTkeksktk ksktkrkiknkgk kiksk ktkeksktkiknkgk"
        assert replacement_handler(
            text=self.test_string, replacer_string="T,e,s,t,r,i,n,g:p\np:",
            is_lemma=False) == "   "
        assert replacement_handler(
            text=self.test_string, replacer_string="", is_lemma=False) == \
            self.test_string
        assert replacement_handler(
            text=self.test_string, replacer_string=" ", is_lemma=False) == \
            self.test_string
        assert replacement_handler(
            text=self.test_string, replacer_string="\n", is_lemma=False) == \
            self.test_string
        # Missing/too many colons
        try:
            replacement_handler(
                text=self.test_string, replacer_string="s,f", is_lemma=False)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string=",", is_lemma=False)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="k", is_lemma=False)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="t:u:w", is_lemma=False)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="t::w", is_lemma=False)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        # Too many arguments on right of colon
        try:
            replacement_handler(
                text=self.test_string, replacer_string="a:i,e", is_lemma=False)
        except LexosException as excep:
            assert str(excep) == REPLACEMENT_RIGHT_OPERAND_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="s,t:u,v",
                is_lemma=False)
        except LexosException as excep:
            assert str(excep) == REPLACEMENT_RIGHT_OPERAND_MESSAGE

    def test_not_lemma_spacing(self):
        assert replacement_handler(
            text="", replacer_string="", is_lemma=False) == ""
        assert replacement_handler(
            text="", replacer_string="a:b", is_lemma=False) == ""
        assert replacement_handler(
            text=" test test ", replacer_string="e:u", is_lemma=False) == \
            " tust tust "
        assert replacement_handler(
            text="\nt", replacer_string="a:b", is_lemma=False) == "\nt"

    def test_is_lemma_same(self):
        assert replacement_handler(
            text=self.test_string, replacer_string="string:thread",
            is_lemma=True) == "Test thread is testing"
        assert replacement_handler(
            text="Test test testing test test", replacer_string="test:work",
            is_lemma=True) == "Test work testing work work"
        assert replacement_handler(
            text=self.test_string, replacer_string="Test,testing:working",
            is_lemma=True) == "working string is working"
        assert replacement_handler(
            text=self.test_string,
            replacer_string="Test,is,testing:string\nstring:foo",
            is_lemma=True) == "foo foo foo foo"
        assert replacement_handler(
            text="lotsssssss\nof\ntexxxxxxxt", replacer_string="of:more",
            is_lemma=True) == "lotsssssss\nmore\ntexxxxxxxt"
        assert replacement_handler(
            text=" test ", replacer_string="test:text", is_lemma=True) == \
            " text "

    def test_is_lemma_incomplete_replacer(self):
        assert replacement_handler(
            text=self.test_string, replacer_string="is:", is_lemma=True) == \
            "Test string  testing"
        assert replacement_handler(
            text=self.test_string, replacer_string=":word", is_lemma=True) == \
            "wordTestword wordstringword wordisword wordtestingword"
        assert replacement_handler(
            text=self.test_string, replacer_string=":", is_lemma=True) == \
            self.test_string
        # Missing/too many colons
        try:
            replacement_handler(
                text=self.test_string, replacer_string="Test,testing,working",
                is_lemma=True)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="word", is_lemma=True)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="is::word",
                is_lemma=True)
        except LexosException as excep:
            assert str(excep) == NOT_ONE_REPLACEMENT_COLON_MESSAGE
        # Too many arguments on right of colon
        try:
            replacement_handler(
                text=self.test_string, replacer_string="working:Test,testing",
                is_lemma=True)
        except LexosException as excep:
            assert str(excep) == REPLACEMENT_RIGHT_OPERAND_MESSAGE
        try:
            replacement_handler(
                text=self.test_string, replacer_string="is,string:how,what",
                is_lemma=True)
        except LexosException as excep:
            assert str(excep) == REPLACEMENT_RIGHT_OPERAND_MESSAGE


class TestReplacementHandlerWithMergeStrings:
    text_string = "This is... Some (random), te-xt I 'wrote'! Isn't it nice?"
    cache_folder = \
        '/tmp/Lexos_emma_grace/OLME8BVT2A6S0ESK11S1VIAA01Y22K/scrub/'
    cache_filenames = ['consolidations.p', 'lemmas.p', 'specialchars.p',
                       'stopwords.p']

    # No tests with neither replacer because handle_special_characters()
    # uses requests

    def test_replacement_handler_special(self):
        file_special_string = merge_file_and_manual_strings(
            file_string="-:_\n!:~\nn:ñ\na:@", manual_string="",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        manual_special_string = merge_file_and_manual_strings(
            file_string="", manual_string="-:_\n!:~\nn:ñ\na:@",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        split_special_string = merge_file_and_manual_strings(
            file_string="-:_\n!:~", manual_string="n:ñ\na:@",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        after_special = "This is... Some (r@ñdom), te_xt I 'wrote'~ Isñ't " \
                        "it ñice?"

        assert replacement_handler(
            text=self.text_string, replacer_string=file_special_string,
            is_lemma=False) == after_special
        assert replacement_handler(
            text=self.text_string, replacer_string=manual_special_string,
            is_lemma=False) == after_special
        assert replacement_handler(
            text=self.text_string, replacer_string=split_special_string,
            is_lemma=False) == after_special

    def test_replacement_handler_consol(self):
        file_consol_string = merge_file_and_manual_strings(
            file_string="o:u\nt,x:y\nI:i", manual_string="",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        manual_consol_string = merge_file_and_manual_strings(
            file_string="", manual_string="o:u\nt,x:y\nI:i",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        split_consol_string = merge_file_and_manual_strings(
            file_string="o:u\nt,x:y", manual_string="I:i",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        after_consol = "This is... Sume (randum), ye-yy i 'wruye'! isn'y iy" \
                       " nice?"

        assert replacement_handler(
            text=self.text_string, replacer_string=file_consol_string,
            is_lemma=False) == after_consol
        assert replacement_handler(
            text=self.text_string, replacer_string=manual_consol_string,
            is_lemma=False) == after_consol
        assert replacement_handler(
            text=self.text_string, replacer_string=split_consol_string,
            is_lemma=False) == after_consol

    def test_replacement_handler_lemma(self):
        file_lemma_string = merge_file_and_manual_strings(
            file_string="I,it:she\nrandom:interesting", manual_string="",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        manual_lemma_string = merge_file_and_manual_strings(
            file_string="", manual_string="I,it:she\nrandom:interesting",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        split_lemma_string = merge_file_and_manual_strings(
            file_string="I,it:she", manual_string="random:interesting",
            cache_folder=self.cache_folder,
            cache_filenames=self.cache_filenames, cache_number=2)
        after_lemma = "This is... Some (interesting), te-xt she 'wrote'! " \
                      "Isn't she nice?"

        assert replacement_handler(
            text=self.text_string, replacer_string=file_lemma_string,
            is_lemma=True) == after_lemma
        assert replacement_handler(
            text=self.text_string, replacer_string=manual_lemma_string,
            is_lemma=True) == after_lemma
        assert replacement_handler(
            text=self.text_string, replacer_string=split_lemma_string,
            is_lemma=True) == after_lemma


class TestProcessTagReplaceOptions:
    tag_text = "Text before tags.\n<first> Some text in the first tag " \
               "</first>\nText between the tags.\n<second tag_num= \"2-nd " \
               "tag's num\">Other text in the second tag</second>\nText" \
               " after the tags."
    no_end = "The ending <first> tags here <first> are a bit <second> messed" \
             " up."

    def test_process_tag_rep_options_remove_tag(self):
        action = "remove-tag"
        attribute = ""

        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="first", action=action,
            attribute=attribute) == "Text before tags.\n  Some text in the " \
                                    "first tag  \nText between the tags." \
                                    "\n<second tag_num= \"2-nd tag's num\">" \
                                    "Other text in the second tag</second>\n" \
                                    "Text after the tags."
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="second", action=action,
            attribute=attribute) == "Text before tags.\n<first> Some text in" \
                                    " the first tag </first>\nText between" \
                                    " the tags.\n Other text in the second " \
                                    "tag \nText after the tags."
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="first", action=action,
            attribute=attribute) == "The ending   tags here   are a bit " \
                                    "<second> messed up."
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="second", action=action,
            attribute=attribute) == "The ending <first> tags here <first> " \
                                    "are a bit   messed up."

    def test_process_tag_rep_options_remove_element(self):
        action = "remove-element"
        attribute = ""

        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="first", action=action,
            attribute=attribute) == "Text before tags.\n \nText between the" \
                                    " tags.\n<second tag_num= \"2-nd tag's " \
                                    "num\">Other text in the second tag" \
                                    "</second>\nText after the tags."
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="second", action=action,
            attribute=attribute) == "Text before tags.\n<first> Some text in" \
                                    " the first tag </first>\nText between " \
                                    "the tags.\n \nText after the tags."
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="first", action=action,
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="second", action=action,
            attribute=attribute) == self.no_end

    def test_process_tag_rep_options_replace_element(self):
        action = "replace-element"
        attribute = "a very nice attribute"

        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="first", action=action,
            attribute=attribute) == "Text before tags.\na very nice " \
                                    "attribute\nText between the tags." \
                                    "\n<second tag_num= \"2-nd tag's num\">" \
                                    "Other text in the second tag</second>\n" \
                                    "Text after the tags."
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="second", action=action,
            attribute=attribute) == "Text before tags.\n<first> Some text in" \
                                    " the first tag </first>\nText "\
                                    "between the tags.\na very nice " \
                                    "attribute\nText after the tags."
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="first", action=action,
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="second", action=action,
            attribute=attribute) == self.no_end

    def test_process_tag_rep_options_leave_tag(self):
        action = "leave-alone"
        attribute = ""

        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="first", action=action,
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="second", action=action,
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="first", action=action,
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="second", action=action,
            attribute=attribute) == self.no_end

    def test_process_tag_rep_options_other(self):
        action = "remove-tag"
        attribute = ""

        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="first", action="fake-option",
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="second", action="fake-option",
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="first", action="fake-option",
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="second", action="fake-option",
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="Text", action=action,
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag=" ", action=action,
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag="", action=action,
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.tag_text, tag=".", action=action,
            attribute=attribute) == self.tag_text
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="Text", action=action,
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            self.no_end, " ", action, attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.no_end, tag="", action=action,
            attribute=attribute) == self.no_end
        assert process_tag_replace_options(
            orig_text=self.no_end, tag=".", action=action,
            attribute=attribute) == self.no_end


# handle_tags


class TestGetAllPunctuationMap:

    def test_get_all_punctuation_map(self):
        assert get_all_punctuation_map() == chars.ORD_PUNCT_SYMBOL_TO_NONE


class TestScrubSelectApos:

    def test_scrub_select_apos(self):
        assert scrub_select_apos(
            text="Tes't test' ' 'test tes''t test'' '' ''test") == \
            "Tes't test  test test test  test"
        assert scrub_select_apos(text="Test test") == "Test test"
        assert scrub_select_apos(text="' ") == " "
        assert scrub_select_apos(text="'") == "'"
        assert scrub_select_apos(text="") == ""


class TestConsolidateHyphens:

    def test_consolidate_hyphens(self):
        assert consolidate_hyphens(
            text="Tes\u058At test\u2011 \u2012 \u2014test tes\uFE58\uFF0Dt "
            "test\u1400\u2E3A \u2E40\u2E17 \u3030\uFE31test "
            "tes\uFE32\u2E3B\u2013t test\u05BE\uFE63\u30A0 \u301C-\u2E1A\u2010"
            " \u2015\u1806") == "Tes-t test- - -test tes--t test-- -- " \
                                "--test tes---t test--- ---- --"
        assert consolidate_hyphens(text="Test test") == "Test test"
        assert consolidate_hyphens(text="") == ""


class TestConsolidateAmpers:

    def test_consolidate_ampers(self):
        assert consolidate_ampers(
            text="Tes\uFE60t test\u06FD \U0001F675 \u214Btest tes\U0001F674&t "
            "test\U000E0026\u0026 \uFF06") == "Tes&t test& & &test tes&&t " \
                                              "test&& &"
        assert consolidate_ampers(text="Test test") == "Test test"
        assert consolidate_ampers(text="") == ""


class TestGetRemovePunctuationMap:

    def test_get_remove_punct_map_no_cache(self):
        no_punct_string = "Some text with no punctuation"
        apos_string = "There's \"a lot\" of words in this text here ye' " \
                      "isn''t 'ere a lot\"ve 'em?'!"
        hyphen_string = "-\u2E3B\u058AMany\u05BE\u2010 \uFE32 " \
                        "\u2E3Amany\u2E40 \uFE31many\u30A0\u3030 " \
                        "\u2011types\u2012 of\u2013 \u301C\u2014" \
                        " \u2015hyphens \uFE58\uFE63\uFF0D " \
                        "\u1400in\u1806\u2E17 here!\u2E1A!"
        amper_string = "We\uFF06 \u214B\u06FD have tons\uFE60 &\u0026 tons " \
                       "\U0001F675 of \U000E0026ampers here!\U0001F674!"
        mixed_string = "There's a lot o' punct. & \"chars\" \U0001F674 " \
                       "mixed-up things in here! How''s it go\u30A0\ning to " \
                       "go?"

        map_no_apos = {key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE
                       if key != ord("'")}
        map_no_hyphen = {key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE
                         if key != ord("-")}
        map_no_amper = {key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE
                        if key != ord("&")}
        map_no_apos_hyphen = {
            key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE if
            key != ord("'") and key != ord("-")}
        map_no_apos_amper = {
            key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE if
            key != ord("'") and key != ord("&")}
        map_no_hyphen_amper = {
            key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE if
            key != ord("-") and key != ord("&")}
        map_no_all = {key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE if
                      key != ord("'") and key != ord("-") and key != ord("&")}
        map_previewing = {key: None for key in chars.ORD_PUNCT_SYMBOL_TO_NONE
                          if key != ord("…")}

        assert get_remove_punctuation_map(
            no_punct_string, apos=False, hyphen=False, amper=False,
            previewing=False) == (no_punct_string,
                                  chars.ORD_PUNCT_SYMBOL_TO_NONE)
        assert get_remove_punctuation_map(
            apos_string, apos=True, hyphen=False, amper=False,
            previewing=False) == ("There's \"a lot\" of words in this text"
                                  " here ye isnt ere a lot\"ve em?!",
                                  map_no_apos)
        assert get_remove_punctuation_map(
            hyphen_string, apos=False, hyphen=True, amper=False,
            previewing=False) == ("---Many-- - -many- -many-- -types- of- -- "
                                  "-hyphens --- -in-- here!-!", map_no_hyphen)
        assert get_remove_punctuation_map(
            amper_string, apos=False, hyphen=False, amper=True,
            previewing=False) == ("We& && have tons& && tons & of &ampers "
                                  "here!&!", map_no_amper)
        assert get_remove_punctuation_map(
            mixed_string, apos=True, hyphen=True, amper=False,
            previewing=False) == ("There's a lot o punct. & \"chars\" "
                                  "\U0001F674 mixed-up things in here! Hows it"
                                  " go-\ning to go?", map_no_apos_hyphen)
        assert get_remove_punctuation_map(
            mixed_string, apos=True, hyphen=False, amper=True,
            previewing=False) == ("There's a lot o punct. & \"chars\" & "
                                  "mixed-up things in here! Hows it "
                                  "go\u30A0\ning to go?", map_no_apos_amper)
        assert get_remove_punctuation_map(
            mixed_string, apos=False, hyphen=True, amper=True,
            previewing=False) == ("There's a lot o' punct. & \"chars\" & "
                                  "mixed-up things in here! How''s it "
                                  "go-\ning to go?", map_no_hyphen_amper)
        assert get_remove_punctuation_map(
            mixed_string, apos=True, hyphen=True, amper=True,
            previewing=False) == ("There's a lot o punct. & \"chars\" & "
                                  "mixed-up things in here! Hows it "
                                  "go-\ning to go?",
                                  map_no_all)
        assert get_remove_punctuation_map(
            no_punct_string, apos=False, hyphen=False, amper=False,
            previewing=True) == (no_punct_string, map_previewing)


class TestGetRemoveDigitsMap:

    def test_get_remove_digits_no_cache(self):
        assert get_remove_digits_map() == chars.ORD_DIGIT_TO_NONE


class TestSplitInputWordString:

    def test_split_input_word_str_with_words(self):
        assert split_input_word_string(
            input_string="\nThis\nstring\n\nhas\nnewlines\n\n") \
            == ["This", "string", "has", "newlines"]
        assert split_input_word_string(
            input_string=",This,string,,has,commas,,") == \
            ["This", "string", "has", "commas"]
        assert split_input_word_string(
            input_string=".This.string..has.periods..") == \
            [".This.string..has.periods.."]
        assert split_input_word_string(
            input_string=" This string  has spaces  ") == \
            ["This", "string", "has", "spaces"]
        assert split_input_word_string(
            input_string="\n., This,.string\n,, has.\n.some, of,. "
                         "\neverything \n..") == [".", "This", ".string",
                                                  "has.", ".some", "of", ".",
                                                  "everything", ".."]

    def test_split_input_word_str_no_words(self):
        assert split_input_word_string("") == []
        assert split_input_word_string("\n") == []
        assert split_input_word_string(",") == []
        assert split_input_word_string(" ") == []
        assert split_input_word_string(
            "\n \n ,.. ,\n.,, , \n\n.\n,   . \n... ,") == \
            ["..", ".", ".", ".", "..."]


class TestMergeFileAndManualStrings:

    def test_merge_file_and_manual_strings(self):
        string1 = "and. the\n who,how why"
        string2 = "what where, but. of,\nnot,for"
        cache_folder = \
            '/tmp/Lexos_emma_grace/OLME8BVT2A6S0ESK11S1VIAA01Y22K/scrub/'
        cache_filenames = ['consolidations.p', 'lemmas.p', 'specialchars.p',
                           'stopwords.p']
        cache_number = 1

        assert merge_file_and_manual_strings(
            file_string="", manual_string="", cache_folder=cache_folder,
            cache_filenames=cache_filenames, cache_number=cache_number) == "\n"
        assert merge_file_and_manual_strings(
            file_string=string1, manual_string="",
            cache_folder=cache_folder, cache_filenames=cache_filenames,
            cache_number=cache_number) == string1 + "\n"
        assert merge_file_and_manual_strings(
            file_string="", manual_string=string2,
            cache_folder=cache_folder, cache_filenames=cache_filenames,
            cache_number=cache_number) == "\n" + string2
        assert merge_file_and_manual_strings(
            file_string=string1, manual_string=string2,
            cache_folder=cache_folder, cache_filenames=cache_filenames,
            cache_number=cache_number) == string1 + "\n" + string2


class TestDeleteWords:
    test_string = "Many words were written, but not many of all the words " \
                  "said much at all."

    def test_delete_words(self):
        assert delete_words(
            self.test_string, ["Many", "words", "written", "all"]) == \
            " were written, but not many of the said much at all."
        assert delete_words(self.test_string, [""]) == self.test_string
        assert delete_words(self.test_string, []) == self.test_string
        assert delete_words("", ["words"]) == ""
        assert delete_words("", []) == ""
        assert delete_words(
            "Using\u200Aunicode\u3000whitespace\u2004!\u2008?",
            ["Using", "whitespace", "?"]) == "\u200Aunicode\u2004!"
        assert delete_words(
            "test test. test? test! test$ test* ^test test",
            ["test.", "test$", "^test", "test!"]) == "test test? test* test"


class TestRemoveStopwords:
    test_string = "This is a 'long' story. It is time for this long story " \
                  "to end to-night. end."

    def test_remove_stopwords_normal(self):
        assert remove_stopwords(self.test_string, "is") == \
            "This a 'long' story. It time for this long story to end " \
            "to-night. end."
        assert remove_stopwords(self.test_string, "This") == \
            " is a 'long' story. It is time for this long story to end " \
            "to-night. end."
        assert remove_stopwords(self.test_string, "this") == \
            "This is a 'long' story. It is time for long story to end " \
            "to-night. end."
        assert remove_stopwords(self.test_string, "This,this") == \
            " is a 'long' story. It is time for long story to end " \
            "to-night. end."
        assert remove_stopwords(self.test_string, "is,this\na, for") == \
            "This 'long' story. It time long story to end to-night. end."
        assert remove_stopwords(self.test_string, "story") == \
            "This is a 'long' story. It is time for this long to end " \
            "to-night. end."
        assert remove_stopwords(self.test_string, "long,to") == \
            "This is a 'long' story. It is time for this story end " \
            "to-night. end."
        assert remove_stopwords(
            "  Weird \t\t spacing\n\t\nhere   \tin\n\n\nthis\n \t text",
            "Weird, here, in, text") == "  \t\t spacing\n\t   \n\n\nthis\n \t"

    def test_remove_stopwords_edge(self):
        assert remove_stopwords(self.test_string, "") == self.test_string
        assert remove_stopwords(self.test_string, " ") == self.test_string
        assert remove_stopwords("test\nstring", "\n") == "test\nstring"
        assert remove_stopwords("test", "test") == ""
        assert remove_stopwords("   test   ", "test") == "     "
        assert remove_stopwords("\ntest\n", "test") == "\n"
        assert remove_stopwords("Test this code", "Test,this,code") == ""
        assert remove_stopwords("Another test", "test, test, test") == \
            "Another"
        assert remove_stopwords(self.test_string, "This\nend.\nfor") == \
            " is a 'long' story. It is time this long story to end to-night."
        assert remove_stopwords(self.test_string, "This long story") == \
            remove_stopwords(self.test_string, "This,long,story")
        assert remove_stopwords(self.test_string, ".") == self.test_string


class TestKeepWords:
    test_string = "Test text is this text here"
    test_string_period = test_string + "."

    def test_keep_words_normal(self):
        assert keep_words(self.test_string, "is") == " is"
        assert keep_words(self.test_string, "Test") == "Test"
        assert keep_words(self.test_string, "here") == " here"
        assert keep_words(self.test_string, "missing") == ""
        assert keep_words(self.test_string, "") == \
            keep_words(self.test_string, "missing")
        assert keep_words(self.test_string, " ") == \
            keep_words(self.test_string, "")
        assert keep_words(self.test_string, "text") == " text text"
        assert keep_words(self.test_string, "Test, here, is") == \
            "Test is here"
        assert keep_words(self.test_string, "Test,missing,text") == \
            "Test text text"
        assert keep_words(self.test_string, "Test missing text") == \
            keep_words(self.test_string, "Test,missing,text")
        assert keep_words(self.test_string, "Test\nmissing\ntext") == \
            keep_words(self.test_string, "Test,missing,text")
        assert keep_words("Word word word word gone word", "word") == \
            " word word word word"
        assert keep_words(self.test_string, self.test_string) == \
            self.test_string
        assert keep_words(self.test_string, "is, this") == \
            remove_stopwords(self.test_string, "Test, text, here")
        assert keep_words(
            "Test\u1680unicode\u205Fwhite\u2007spaces\u2001now",
            "unicode, white, now") == "\u1680unicode\u205Fwhite\u2001now"
        assert keep_words(
            "Test\nsome\t\tkeep words\n\nwhitespace\tpreservation\nwith  this"
            "\t sentence \n now", "Test, keep, whitespace, with, this, now") \
            == "Test\t\tkeep\n\nwhitespace\nwith  this\t \n now"

    def test_keep_words_punctuation(self):
        assert keep_words(self.test_string_period, "here") == ""
        assert keep_words(self.test_string_period, "here.") == " here."
        assert keep_words(self.test_string_period, "") == ""
        assert keep_words("there is some?text here", "some?text\nhere") ==\
            " some?text here"
        assert keep_words("there is some?text here", "some\ntext\nhere") \
            == " here"
        assert keep_words("there is some.text here", "some.text\nhere") ==\
            " some.text here"
        assert keep_words("there is some-text here", "some\ntext\nhere") == \
            " here"
        assert keep_words(
            self.test_string_period, self.test_string_period) == \
            self.test_string_period
        assert keep_words("Can we . use periods .. safely", ".") == " ."
        assert keep_words("Question mark s? ? ?? ???", "s?") == " s?"


class TestGetRemoveWhitespaceMap:

    def test_remove_whitespace_map(self):
        # All possible combinations of three boolean parameters:
        # 000
        assert get_remove_whitespace_map(
            spaces=False, tabs=False, new_lines=False) == {}
        # 100
        assert get_remove_whitespace_map(
            spaces=True, tabs=False, new_lines=False) == {ord(' '): None}
        # 010
        assert get_remove_whitespace_map(
            spaces=False, tabs=True, new_lines=False) == {ord('\t'): None}
        # 110
        assert get_remove_whitespace_map(
            spaces=True, tabs=True, new_lines=False) == \
            {ord(' '): None, ord('\t'): None}
        # 001
        assert get_remove_whitespace_map(
            spaces=False, tabs=False, new_lines=True) == \
            {ord('\n'): None, ord('\r'): None}
        # 101
        assert get_remove_whitespace_map(
            spaces=True, tabs=False, new_lines=True) == \
            {ord(' '): None, ord('\n'): None, ord('\r'): None}
        # 011
        assert get_remove_whitespace_map(
            spaces=False, tabs=True, new_lines=True) == \
            {ord('\t'): None, ord('\n'): None, ord('\r'): None}
        # 111
        assert get_remove_whitespace_map(
            spaces=True, tabs=True, new_lines=True) == \
            {ord(' '): None, ord('\t'): None, ord('\n'): None, ord('\r'): None}


# cache_filestring

# load_cached_filestring


class TestHandleGutenberg:

    def test_handle_gutenberg_match(self):
        assert handle_gutenberg(text=guten.TEXT_FRONT_PLATE) == \
            guten.FRONT_PLATE_EXTRA + guten.TEXT_NEITHER
        assert handle_gutenberg(text=guten.TEXT_FRONT_COPY) == \
            guten.TEXT_NEITHER
        assert handle_gutenberg(text=guten.TEXT_BACK) == guten.TEXT_NEITHER
        assert handle_gutenberg(text=guten.TEXT_BOTH_PLATE) == \
            guten.FRONT_PLATE_EXTRA + guten.TEXT_NEITHER
        assert handle_gutenberg(text=guten.TEXT_BOTH_COPY) == \
            guten.TEXT_NEITHER
        assert handle_gutenberg(
            text="This text is Copyright Joe Schmoe.\n\n\nDone.") == "Done."
        assert handle_gutenberg(
            text="This text is copyright Joe Schmoe.\n\n\nDone.") == "Done."

    def test_handle_gutenberg_no_match(self):
        assert handle_gutenberg(text=guten.TEXT_NEITHER) == guten.TEXT_NEITHER
        assert handle_gutenberg(text="") == ""
        assert handle_gutenberg(
            text="This text is copyright\nJoe Schmoe.\n\n\nDone.") == \
            "This text is copyright\nJoe Schmoe.\n\n\nDone."
        assert handle_gutenberg(
            text="This text is copyright Joe Schmoe.\n\nDone.") == \
            "This text is copyright Joe Schmoe.\n\nDone."


# prepare_additional_options

# scrub
