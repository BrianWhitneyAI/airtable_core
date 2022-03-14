import requests


def add_to_airtable(endpoint, AIRTABLE_API_KEY, data):
    if endpoint is None:
        return
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {}
    r = requests.post(endpoint, json=data, headers=headers)
    return r.status_code == 200


def add_all_to_airtable(endpoint, AirTable_API_Key, df):
    for index, row in df.iterrows():
        data = row.values.tolist()
        add_to_airtable(endpoint, AirTable_API_Key, data)
        print("Adding row #" + (index + 1))
    print("complete")
    # This method should delete repeat data as well

    # If statement for Airtable Dashboard
    # set currents
