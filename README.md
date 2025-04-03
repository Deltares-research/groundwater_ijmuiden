# Groundwater Salinization Monitoring - IJmuiden (11207510)

This Python environment is designed to process data from the groundwater monitoring network around the sea lock complex at IJmuiden.

## Collected Data

The collected data includes:

- **Diver Data**: Measurements from divers placed in monitoring wells to analyze groundwater dynamics in the area.
- **Field Measurements**: Representative water sample measurements, including:
    - Electrical Conductivity (EC)
    - Redox Potential
    - Water Temperature
- **Groundwater Level Measurements**: Manual measurements of groundwater levels, useful for validating diver data.
- **Hydrochemistry**: Chemical analysis of water samples.
- **Borelogs**: Borehole data (e.g., EM and gamma-ray logs) to monitor in situ salinization around the wells.

## Environment Overview

This environment provides tools to process and visualize the collected data. The following subfolders are included:

- **`preprocessing`**: Scripts for preprocessing data (not part of the official Python package).
- **`groundwater_ijmuiden`**: Core package scripts for processing diver data, which can be used in runfiles.
- **`runfiles`**: Scripts that utilize the package to process the data.
- **`figures`**: Plotting scripts for data visualization (not part of the official Python package).

### `groundwater_ijmuiden`

This package contains the core functionality for processing groundwater diver data. It provides several tools, including readers (e.g., `read_diver`) to open diver data. The main functionality allows processing raw diver data to calculate density-corrected freshwater head.

#### Workflow

The package is designed to generate a `MonitoringWell` class for each monitoring well. Initialization requires key parameters such as the top of the well (`ztop`) and cable length (`cable_length`). Properties of the well can be updated from a specified date using the `update_properties` method. Additional data can be added to the `MonitoringWell` instance, such as:
- **Barometric Data**: Add barometric pressure data using the `add_barometer` method. This data is used for barometric compensation calculations.
- **Diver Data**: Include diver data using the `add_diverdata` method. This data forms the basis for analyzing groundwater dynamics.
- **EC Measurements**: Add electrical conductivity (EC) measurements using the `add_ec_measurements` method. These measurements are used to derive water density for further calculations.
- **Groundwater Measurements**: Add manual groundwater level measurements using the `add_gw_measurements` method. These measurements are used for validating and adjusting groundwater levels.

#### Key Functions

1. **Barometric Compensation**: Calculates the height of the water column above the diver and references it to a vertical datum based on the cable length. Groundwater levels can be adjusted using hand measurements with the following methods:
     - `"last"`: Use the most recent hand measurement for adjustment.
     - `"penultimate"`: Use the second most recent hand measurement for adjustment.
     - `"all"`: Interpolate adjustments for all available groundwater measurements.
     The default method is `"last"`.

2. **Calculate Freshwater Head**: Converts the point water head to a freshwater head based on water density derived from EC measurements (see Post & Kooi, 2007).

3. **Calculate Freshwater Reference Head**: Computes the reference head based on point water head, water density, and aquifer reference level.

4. **Drop Data**: Deletes data from the groundwater time series before or after a specified date.

This package provides a framework for analyzing and interpreting groundwater salinization data.
