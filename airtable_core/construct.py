import datetime as dt

import pandas as pd


def get_metadata(file_path: str):
    metadata = []
    file_name_metadata = open(file_path).name.split("_")
    metadata.append(file_name_metadata[0].split("\\")[-1])
    year = int(file_name_metadata[5])
    month = int(file_name_metadata[6])
    day = int(file_name_metadata[7][0:2])
    metadata.append(dt.datetime(year, month, day))
    return metadata + file_name_metadata[1:4]


def get_raw_data(file_path: str):
    raw_data = pd.read_csv(file_path)
    raw_data = raw_data[23:]
    raw_data.columns = raw_data.iloc[0]
    raw_data = raw_data[1:]
    raw_data = raw_data.reset_index(drop=True)
    raw_data = raw_data[raw_data.columns.drop(list(raw_data.filter(regex="error")))]
    return raw_data


def get_linearity_data(metadata: list, raw_data):
    linearity = pd.DataFrame(
        columns=[
            "System",
            "Date",
            "Argo Identity",
            "Objective",
            "slide ID",
            "Wavelength",
            "Power Instruction",
            "Power (mW)",
        ]
    )
    percent_data = raw_data[0:15]
    percent_data = percent_data.fillna(0).astype(int)
    percent_data.set_index("power_instruction", inplace=True)
    for rowIndex, row in percent_data.iterrows():  # iterate over rows
        for columnIndex, value in row.items():
            if (
                value != 0
                and percent_data[percent_data[columnIndex] == value].index.tolist()[0]
                % 10
                == 0
            ):
                power_data = (
                    metadata
                    + [int(columnIndex[:-6])]
                    + percent_data[percent_data[columnIndex] == value].index.tolist()
                    + [value]
                )
                power_data = pd.Series(power_data, index=linearity.columns)
                linearity = linearity.append(power_data, ignore_index=True)
    return linearity


def get_experimental_data(metadata: list, raw_data):
    thresholds = raw_data[
        11 : raw_data[
            raw_data.isin(
                [
                    "measured_optical_power_error",
                    "measured_optical_power_average",
                    "time",
                ]
            ).any(axis=1)
        ].index[0]
    ]  # this line can be done better
    thresholds = thresholds.fillna(0).astype(float)
    thresholds.set_index("power_instruction", inplace=True)
    experimental = pd.DataFrame(
        columns=[
            "System",
            "Date",
            "Argo Identity",
            "Objective",
            "slide ID",
            "Wavelength",
            "Power Instruction",
            "Threshold",
        ]
    )
    for rowIndex, row in thresholds.iterrows():  # iterate over rows
        for columnIndex, value in row.items():
            if (
                value != 0
                and thresholds[thresholds[columnIndex] == value].index.tolist()[0] % 10
                != 0
            ):
                power_data = (
                    metadata
                    + [int(columnIndex[:-6])]
                    + thresholds[thresholds[columnIndex] == value].index.tolist()
                    + [value]
                )
                power_data = pd.Series(power_data, index=experimental.columns)
                experimental = experimental.append(power_data, ignore_index=True)
    return experimental


def get_threshold(system, wavelength, date, df):
    thresholds = df[df["System"] == system]
    thresholds = thresholds[thresholds["Wavelength"] == wavelength]
    thresholds = thresholds[thresholds["Date"] == date]
    return thresholds["Power Instruction"].min()


def get_dashboard_data(linearity, experimental):
    linearity["System"] = linearity.System.astype("category")
    linearity["Wavelength"] = linearity.Wavelength.astype("category")
    dashboard = pd.DataFrame(
        columns=[
            "System",
            "Date",
            "Wavelength",
            "Laser Power at 100%",
            "Experimental (% laser power)",
            "R^2",
            "Effective",
            "Current",
        ]
    )
    Systems = linearity["System"].cat.categories
    for system in Systems:
        pd_sys = linearity[linearity["System"] == system]
        Wavelengths = pd_sys["Wavelength"].cat.categories
        for wavelength in Wavelengths:
            pd_wavelength = pd_sys[pd_sys["Wavelength"] == wavelength]
            if not pd_wavelength.empty:
                pd_current = pd_wavelength[
                    pd_wavelength["Date"] == pd_wavelength["Date"].max()
                ]
                row_data = []
                row_data.append(system)
                row_data.append(pd_current["Date"].max())  # Max Date
                row_data.append(wavelength)
                row_data.append(
                    pd_current["Power (mW)"].max()
                )  # power in MW of 100% at current date
                row_data.append(
                    get_threshold(
                        system, wavelength, pd_current["Date"].max(), experimental
                    )
                )  # Threshold
                row_data.append(0)  # This needs to be pulled from Airtable
                row_data.append(True)  # modify later with condition
                if pd_current["Date"].max() == pd_wavelength["Date"].max():
                    row_data.append(True)
                else:
                    row_data.append(False)
                row_data = pd.Series(row_data, index=dashboard.columns)
                dashboard = dashboard.append(row_data, ignore_index=True)
    return dashboard
