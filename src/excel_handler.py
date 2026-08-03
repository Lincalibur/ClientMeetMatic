import pandas as pd

REQUIRED_COLUMNS = ['ClientName', 'Address', 'Priority']
VALID_PRIORITIES = {'High', 'Medium', 'Low'}


def read_excel(file_path):
    df = pd.read_excel(file_path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"'{file_path}' is missing required column(s): {', '.join(missing)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}."
        )

    df = df.dropna(subset=['ClientName', 'Address']).reset_index(drop=True)

    bad_priority = ~df['Priority'].isin(VALID_PRIORITIES)
    if bad_priority.any():
        bad_rows = df.loc[bad_priority, 'ClientName'].tolist()
        raise ValueError(
            f"Priority must be one of {sorted(VALID_PRIORITIES)}. "
            f"Invalid Priority for client(s): {', '.join(bad_rows)}."
        )

    return df


def add_priority(df, client_name, priority):
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of {sorted(VALID_PRIORITIES)}, got {priority!r}.")
    df.loc[df['ClientName'] == client_name, 'Priority'] = priority


def save_excel(df, file_path):
    df.to_excel(file_path, index=False)
