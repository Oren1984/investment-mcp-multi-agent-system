from feature_flags.flag_manager import FeatureFlagManager


def test_flag_enabled_when_set_to_true(monkeypatch):
    monkeypatch.setenv("MY_FEATURE_FLAG", "true")
    assert FeatureFlagManager.is_enabled("MY_FEATURE_FLAG") is True


def test_flag_enabled_when_set_to_1(monkeypatch):
    monkeypatch.setenv("MY_FEATURE_FLAG", "1")
    assert FeatureFlagManager.is_enabled("MY_FEATURE_FLAG") is True


def test_flag_enabled_when_set_to_yes(monkeypatch):
    monkeypatch.setenv("MY_FEATURE_FLAG", "yes")
    assert FeatureFlagManager.is_enabled("MY_FEATURE_FLAG") is True


def test_flag_disabled_when_set_to_false(monkeypatch):
    monkeypatch.setenv("MY_FEATURE_FLAG", "false")
    assert FeatureFlagManager.is_enabled("MY_FEATURE_FLAG") is False


def test_flag_disabled_when_unset():
    assert FeatureFlagManager.is_enabled("UNSET_FLAG_XYZ_123") is False


def test_flag_respects_custom_default_true():
    assert FeatureFlagManager.is_enabled("UNSET_FLAG_XYZ_123", default=True) is True


def test_flag_respects_custom_default_false():
    assert FeatureFlagManager.is_enabled("UNSET_FLAG_XYZ_123", default=False) is False


def test_flag_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("MY_FEATURE_FLAG", "TRUE")
    assert FeatureFlagManager.is_enabled("MY_FEATURE_FLAG") is True
