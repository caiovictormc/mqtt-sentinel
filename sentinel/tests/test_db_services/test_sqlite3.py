from sentinel.database import manager
from sentinel.database.services import SQLite3
from sentinel.rules import HomieRule

import pytest

import random
import string


DB_NAME = ':memory:'


@pytest.fixture(scope="module")
def db_service(request):
    db = manager(f"sqlite://{DB_NAME}")

    def fin():
        db.close()
    request.addfinalizer(fin)
    return db


def random_string():
    return ''.join(
        [random.choice(string.ascii_letters) for n in range(12)])


@pytest.fixture(scope="module")
def rule(request):
    rule = HomieRule(random_string(), random_string(), random_string())
    return rule


def test_is_sqlite_instance(db_service):
    assert isinstance(db_service, SQLite3)


def test_create_the_rule_table(db_service):
    db_service.migrate()

    cursor = db_service.conn.cursor()
    query = cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='rules';
    """)
    results = query.fetchone()
    assert len(results) > 0


def test_add_rules(db_service, rule):
    db_service.add_rule(rule)

    cursor = db_service.conn.cursor()
    query = cursor.execute("""
        SELECT topic, operator, equated FROM rules;
    """)
    result = query.fetchone()
    assert (rule.topic, rule.operator, rule.equated) == result
