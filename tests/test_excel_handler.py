import pandas as pd
import pytest

from src.excel_handler import add_priority, read_excel


def test_read_excel_valid(tmp_path):
    df = pd.DataFrame({
        'ClientName': ['A', 'B'],
        'Address': ['1 Main St', '2 Main St'],
        'Priority': ['High', 'Low'],
    })
    path = tmp_path / "clients.xlsx"
    df.to_excel(path, index=False)

    result = read_excel(str(path))
    assert list(result['ClientName']) == ['A', 'B']


def test_read_excel_missing_column(tmp_path):
    df = pd.DataFrame({'ClientName': ['A'], 'Address': ['1 Main St']})
    path = tmp_path / "clients.xlsx"
    df.to_excel(path, index=False)

    with pytest.raises(ValueError, match="missing required column"):
        read_excel(str(path))


def test_read_excel_invalid_priority(tmp_path):
    df = pd.DataFrame({
        'ClientName': ['A'],
        'Address': ['1 Main St'],
        'Priority': ['Urgent'],
    })
    path = tmp_path / "clients.xlsx"
    df.to_excel(path, index=False)

    with pytest.raises(ValueError, match="Priority must be one of"):
        read_excel(str(path))


def test_read_excel_drops_blank_rows(tmp_path):
    df = pd.DataFrame({
        'ClientName': ['A', None],
        'Address': ['1 Main St', None],
        'Priority': ['High', None],
    })
    path = tmp_path / "clients.xlsx"
    df.to_excel(path, index=False)

    result = read_excel(str(path))
    assert len(result) == 1


def test_add_priority():
    df = pd.DataFrame({'ClientName': ['A'], 'Priority': ['Low']})
    add_priority(df, 'A', 'High')
    assert df.loc[0, 'Priority'] == 'High'


def test_add_priority_invalid():
    df = pd.DataFrame({'ClientName': ['A'], 'Priority': ['Low']})
    with pytest.raises(ValueError):
        add_priority(df, 'A', 'Urgent')
