"""Verify that the Feature-based module structure exists and is importable."""

def test_core_auth_module():
    import core.auth  # noqa: F401

def test_core_users_module():
    import core.users  # noqa: F401

def test_core_classes_module():
    import core.classes  # noqa: F401

def test_tasks_templates_module():
    import tasks.templates  # noqa: F401

def test_tasks_submissions_module():
    import tasks.submissions  # noqa: F401

def test_tasks_checkin_module():
    import tasks.checkin  # noqa: F401

def test_gamification_points_module():
    import gamification.points  # noqa: F401

def test_gamification_badges_module():
    import gamification.badges  # noqa: F401

def test_gamification_prizes_module():
    import gamification.prizes  # noqa: F401

def test_community_feed_module():
    import community.feed  # noqa: F401

def test_extensions_protocols_module():
    import extensions.protocols  # noqa: F401

def test_extensions_registry_module():
    import extensions.registry  # noqa: F401
