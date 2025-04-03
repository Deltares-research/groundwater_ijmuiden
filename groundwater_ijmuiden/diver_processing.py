import pandas as pd
import numpy as np

from pathlib import Path
from scipy import stats
from .helper_functions import EC_to_S, S_to_rho


class MonitoringWell:

    def __init__(
        self,
        well_id: str,
        reference_level: str,
        ztop: float,
        cable_length: float,
        well_depth: float,
        start_date: str,
        end_date: str,
    ):
        """
        A class to represent a monitoring well used for measuring and tracking groundwater levels and other environmental parameters.

        Attributes:
        ----------
        well_id : str
            A unique identifier for the monitoring well.
        reference_level : str
            The reference level for measurements (in meters NAP).
        ztop : float
            The elevation of the top of the well casing (in meters).
        cable_length : float
            The length of the cable diver is attached to (in meters below ztop), should be positive.
        well_depth : float
            The total depth of the well (in meters), should be positive.
        start_date : str
            The date when monitoring at the well began, formatted as a string ("DD-MM-YYYY").
        end_date : str
            The date when monitoring at the well ended, formatted as a string ("DD-MM-YYYY").

        """

        self.well_id = well_id
        self.date_range = pd.date_range(
            start=pd.to_datetime(start_date, format="%d-%m-%Y"),
            end=pd.to_datetime(end_date, format="%d-%m-%Y"),
            freq="h",
        )
        self.reference_level = reference_level
        self.ztop = pd.DataFrame({"ztop (m NAP)": ztop}, index=self.date_range)
        self.cable_length = pd.DataFrame(
            {"cable_length (m)": cable_length}, index=self.date_range
        )
        self.well_depth = well_depth
        self.elevation_head = ztop - well_depth
        self.water_density = pd.DataFrame(
            {"water_density (kg/m3)": 1000}, index=self.date_range
        )

    def update_properties(
        self,
        date_correction: str,
        new_ztop: float = None,
        new_cable_length: float = None,
    ):
        """
        Updates the ztop and/or cable length properties of the monitoring well for dates after a specified correction date.

        This method allows for modifying the `ztop` (elevation of the top of the well casing)
        and/or `cable_length` (length of the measurement device cable) from a given date onward.

        Parameters:
        ----------
        date_correction : str
            The date from which the new values should apply, formatted as '%d-%m-%Y'.
        new_ztop : float, optional
            The new ztop value to assign. If not provided, the `ztop` remains unchanged.
        new_cable_length : float, optional
            The new cable length value to assign. If not provided, the `cable_length` remains unchanged.
        """
        date_correction = pd.to_datetime(date_correction, format="%d-%m-%Y")
        if new_ztop is not None:
            self.ztop.loc[date_correction:] = new_ztop
        if new_cable_length is not None:
            self.cable_length.loc[date_correction:] = new_cable_length

    def add_barometer(self, df: pd.DataFrame):
        """
        Adds barometer data to the MonitoringWell.

        This method reads barometer data provided in the form of a DataFrame, aligns it with the object's
        existing date range, and assigns it to the  "barometer_data" attribute.

        Parameters:
        ----------
        df : pd.DataFrame
            A DataFrame containing barometer air pressure data (mH20) with a datetime index.
        """
        self.barometer_data = df.reindex(self.date_range)

    def add_diverdata(self, df: pd.DataFrame, zscore_limit=3):
        """
        Adds diver data to the MonitoringWell.

        This method reads barometer data provided in the form of a DataFrame, aligns it with the object's
        existing date range, removes outliers and assigns it to the "diver_data" attribute.

        Parameters:
        ----------
        df : pd.DataFrame
            A DataFrame containing barometer diver pressure data (mH20) with a datetime index.
        """

        criterium_1 = abs(stats.zscore(df["diver_pressure (mH2O)"])) < zscore_limit
        criterium_2 = df["diver_pressure (mH2O)"] > 11
        valid = criterium_1 & criterium_2

        self.diver_data = df.where(valid).reindex(self.date_range)

    def add_ec_measurements(self, df: pd.DataFrame):
        """
        Loads electrical conductivity (EC) measurements (in mS/cm) into the instance's `ec_measurements` attribute
        and updates water density accordingly.

        Parameters:
        ----------
        df : pd.DataFrame
            A DataFrame containing electrical conductivity (EC) measurements (in mS/cm).
        """

        self.ec_measurements = df
        self._calculate_water_density()

    def _calculate_water_density(self):
        """
        Calculates the water density based on electrical conductivity (EC) measurements
        and associated temperature data, then stores the results in the "water_density" attribute.

        """
        # Reference conditions for salinity calculation
        ref_temperature = 20  # °C
        ref_pressure = 10  # dbar

        ec_values = self.ec_measurements[
            ["electrical_conductivity (mS/cm)"]
        ].values.flatten()
        ec_index = self.ec_measurements.index

        temperature_at_diver = (
            self.diver_data.groupby(pd.Grouper(freq="1D"))
            .mean()
            .loc[ec_index, "temperature (degC)"]
            .values
        )

        salinity = EC_to_S(ec_values, ref_temperature, ref_pressure)
        density = S_to_rho(salinity, temperature_at_diver)

        water_density = pd.DataFrame(
            data={"water_density (kg/m3)": density}, index=ec_index
        )

        water_density = water_density.reindex(self.date_range)
        self.water_density = (
            water_density.interpolate(method="linear", axis=0).ffill().bfill()
        )

    def add_gw_measurements(self, df: pd.DataFrame):
        """
        Adds a handreadings to the "Monitoring Well" object.

        The method stores provided handreadings (in meter min ztop) and converts meter NAP
        based on the provided DataFrame,

        Parameters
        ----------
        df : pd.DataFrame
            A DataFrame containing the handreading data with the following structure:
            - Index: DatetimeIndex representing the date and time of the handreading.
            - Columns: 'head (m-ztop)': float, representing the head reading in meters below "ztop".

        """
        indices = np.searchsorted(self.date_range, df.index)
        gw_measurements = self.ztop.iloc[indices] - df[["head (m-ztop)"]].values
        self.gw_measurements = gw_measurements.rename(
            columns={"ztop (m NAP)": "head (m NAP)"}
        )

    def barometric_compensation(
        self,
        match_gw_measurements=False,
        method="last",
    ):
        """
        Perform barometric compensation on the pressure data to calculate the groundwater head.

        The method computes the water column height using pressure data and adjusts it
        for barometric pressure. It also interpolates and applies corrections based on
        manual handreadings if "match_handreadings" is set to "True".

        Parameters
        ----------
        match_gw_measurements : bool, optional
            Whether to match and adjust the computed water head using manual groundwater measurements.
            Defaults to "False".
        method : str, optional
            The method for matching groundwater measurement. Options are:
            - "last": Use the last handreading for adjustment.
            - "penultimate": Use the second last handreading for adjustment.
            - "all": Interpolate adjustments for all available groundwater measurements.
            Defaults to "last".
        """
        GRAVITATIONAL_ACCELERATION = 9.80665  # m/s²

        # Calculate water pressure (adjusting for barometric pressure)
        water_pressure = (
            self.diver_data["diver_pressure (mH2O)"]
            - self.barometer_data["air_pressure (mH2O)"]
        )

        # Compute water column height
        water_column = (9806.65 * water_pressure) / (
            self.water_density["water_density (kg/m3)"] * GRAVITATIONAL_ACCELERATION
        )

        # Calculate the point water head
        point_water_head = (
            self.ztop["ztop (m NAP)"]
            - self.cable_length["cable_length (m)"]
            + water_column
        )
        point_water_head = point_water_head.interpolate("linear", limit=1)

        # Store the result
        self.point_water_head = point_water_head.to_frame("point_water_head (m NAP)")

        # Match and adjust with groundwater measurements if requested
        if match_gw_measurements:
            if not hasattr(self, "gw_measurements"):
                raise ValueError("No groundwater measurements available to match.")

            indices = np.searchsorted(self.date_range, self.gw_measurements.index)

            if method == "last":
                # Adjust using the last groundwater measurements
                index = indices[-1]
                difference = (
                    point_water_head.iloc[index]
                    - self.gw_measurements["head (m NAP)"].iloc[-1]
                )
                correction_factor = pd.Series(difference, index=self.date_range)

            elif method == "penultimate":
                # Adjust using the penultimate groundwater measurements
                index = indices[-2]
                difference = (
                    point_water_head.iloc[index]
                    - self.gw_measurements["head (m NAP)"].iloc[-2]
                )
                correction_factor = pd.Series(difference, index=self.date_range)

            elif method == "all":
                # Adjust using all groundwater measurements (interpolated)
                difference = (
                    point_water_head.iloc[indices]
                    - self.gw_measurements["head (m NAP)"].values
                )
                correction_factor = (
                    difference.reindex(self.date_range)
                    .interpolate(method="linear", axis=0)
                    .ffill()
                    .bfill()
                )
            else:
                raise ValueError(
                    f"Invalid method '{method}'. Use 'last, 'penultimate', or 'all'."
                )

            # Apply correction to the water head
            point_water_head -= correction_factor
            self.point_water_head = point_water_head.to_frame(
                "point_water_head (m NAP)"
            )

        self.calculate_fresh_water_head()
        self.calculate_fresh_water_ref_head()

    def calculate_fresh_water_head(self):
        fresh_water_head = (
            self.water_density["water_density (kg/m3)"] / 1000
        ) * self.point_water_head["point_water_head (m NAP)"] - (
            (self.water_density["water_density (kg/m3)"] - 1000) / 1000
        ) * self.elevation_head

        self.fresh_water_head = fresh_water_head.to_frame("fresh_water_head (m NAP)")

    def calculate_fresh_water_ref_head(self):

        fresh_water_ref_head = (
            self.reference_level
            + (self.water_density["water_density (kg/m3)"] / 1000)
            * (self.point_water_head["point_water_head (m NAP)"] - self.elevation_head)
            - (self.water_density["water_density (kg/m3)"] / 1000)
            * (self.reference_level - self.elevation_head)
        )
        self.fresh_water_ref_head = fresh_water_ref_head.to_frame(
            "fresh_water_ref_head (m NAP)"
        )

    def drop_data(
        self,
        after: str = None,
        before: str = None,
        between: list = None,
    ):
        if after is not None:
            datetime_format = "%d-%m-%Y"
            end_date = pd.to_datetime(after, format=datetime_format)
            self.point_water_head = self.point_water_head.loc[:end_date]
            self.fresh_water_head = self.fresh_water_head.loc[:end_date]
            self.fresh_water_ref_head = self.fresh_water_ref_head.loc[:end_date]

        if before is not None:
            datetime_format = "%d-%m-%Y"
            start_date = pd.to_datetime(before, format=datetime_format)
            self.point_water_head = self.point_water_head.loc[start_date:]
            self.fresh_water_head = self.fresh_water_head.loc[start_date:]
            self.fresh_water_ref_head = self.fresh_water_ref_head.loc[start_date:]

        if between is not None:
            datetime_format = "%d-%m-%Y"
            start_date = pd.to_datetime(between[0], format=datetime_format)
            end_date = pd.to_datetime(between[1], format=datetime_format)
            self.point_water_head.loc[start_date:end_date] = np.nan
            self.fresh_water_head.loc[start_date:end_date] = np.nan
            self.fresh_water_ref_head.loc[start_date:end_date] = np.nan

    def export_point_water_head(self, fdir: str):
        export = pd.concat(
            [
                self.point_water_head[["point_water_head (m NAP)"]],
                self.diver_data[["temperature (degC)"]],
            ],
            axis=1,
        )
        export.to_csv(fdir + f"{self.well_id}.csv")

    def export_fresh_water_head(self, path: str | Path, referenced: bool = True):
        if referenced:
            export = pd.concat(
                [
                    self.fresh_water_ref_head[["fresh_water_ref_head (m NAP)"]],
                    self.diver_data[["temperature (degC)"]],
                ],
                axis=1,
            )
            export = export.rename(
                columns={"fresh_water_ref_head (m NAP)": "fresh_water_head (m NAP)"}
            )
            export.to_csv(path)
        else:
            export = pd.concat(
                [
                    self.fresh_water_head[["fresh_water_head (m NAP)"]],
                    self.diver_data[["temperature (degC)"]],
                ],
                axis=1,
            )
            export.to_csv(path)
