from config.loader import load_settings


def test_load_settings_returns_settings_instance():
    settings = load_settings()
    assert settings.app_name is not None
    assert settings.app_env in {"development", "testing", "staging", "production"}