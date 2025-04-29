import numpy as np

def set_low_res_turbsim(n_turbines, rotor_diameter, ws, spacing, wind_direction, transient = 120, analysis_time = 600):

    """
    Configure low-resolution TurbSim parameters for wind turbine simulations.

    Parameters:
    -----------
    n_turbines : int
        The number of turbines in the farm.
    rotor_diameter : float
        The diameter of the wind turbine rotor (in meters).
    ws : array-like
        A list or array of wind speeds (in m/s).
    spacing : array-like
        A list or array of spacing factors (dimensionless) between turbines.
    wind_direction : array-like
        A list or array of wind directions (in degrees).
    transient : float, optional
        The transient time to be added to the analysis time (in seconds). Default is 300 seconds.

    Returns:
    --------
    tuple
        A tuple containing:
        - GridHeight_LR (float): The height of the low-resolution grid (in meters).
        - GridWidth_LR (float): The width of the low-resolution grid (in meters).
        - AnalysisTime_LR (float): The analysis time for the simulation (in seconds).

    Notes:
    ------
    - The grid dimensions are calculated based on the rotor diameter and wind direction.
    - The analysis time is determined by the lowest wind speed, highest spacing, and the transient time.
    """

    GridHeight_LR = 1.1 * rotor_diameter
    GridWidth_LR = 1.1 * rotor_diameter / np.cos(np.radians(np.max(abs(np.array(wind_direction)))))
    # Set the analysis time based on the lowest wind speed and highest spacing, plus transient
    AnalysisTime_LR = (n_turbines - 1) * np.max(spacing) * rotor_diameter / np.min(ws) + transient + analysis_time

    return GridHeight_LR , GridWidth_LR, AnalysisTime_LR