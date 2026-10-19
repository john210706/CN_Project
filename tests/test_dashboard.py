from streamlit.testing.v1 import AppTest


def test_dashboard():
    app = AppTest.from_file("dashboard/app.py", default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Deadline-Aware Opportunistic Routing Lab"
