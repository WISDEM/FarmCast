import numpy as np

def set_turbsim(n_turbines, rotor_diameter, hub_height, ws, spacing, wind_direction, Cmeander = 1.9, transient = 120, analysis_time = 600, domain_edge = [1., 1., 1., 1.], dy = 10., dz = 10., res = 'low'):
    """
    Configure low-resolution TurbSim parameters for wind turbine simulations.

    Parameters:
    -----------
    n_turbines : int
        The number of turbines in the farm.
    rotor_diameter : float
        The diameter of the wind turbine rotor (in meters).
    hub_height : float
        The hub height of the wind turbine (in meters).
    ws : array-like
        A list or array of wind speeds (in m/s).
    spacing : array-like
        A list or array of spacing factors (dimensionless) between turbines.
    wind_direction : array-like
        A list or array of wind directions (in degrees).
    Cmeander : float, optional
        The wake meandering constant. Default is 1.9.
    transient : float, optional
        The transient time to be added to the analysis time (in seconds). Default is 120 seconds.
    analysis_time : float, optional
        The analysis time for the simulation (in seconds). Default is 600 seconds.
    domain_edge : list, optional
        The extra size in rotor diameters along the edges of the domain for x (left and right) and y (top and bottom) for the TurbSim box. Default is [1., 1., 1., 1.].
    dy : float, optional
        The grid spacing in the y-direction (in meters). Default is 10 m.
    dz : float, optional
        The grid spacing in the z-direction (in meters). Default is 10 m.

    Returns:
    --------
    tuple
        A tuple containing:
        - NumGrid_Z (int): Number of grid points in the z-direction (vertical).
        - NumGrid_Y (int): Number of grid points in the y-direction (horizontal).
        - GridHeight (float): The height of the low-resolution grid (in meters).
        - GridWidth (float): The width of the low-resolution grid (in meters).
        - AnalysisTime (float): The total analysis time for the simulation (in seconds).
        - TimeStep (float): The time step for the low-resolution simulation (in seconds).
        - HubHt_for_TS (float): Adjusted hub height for TurbSim (in meters).

    Notes:
    ------
    - The grid dimensions are calculated based on the rotor diameter, turbine spacing, and wind direction.
    - The analysis time is determined by the lowest wind speed, highest spacing, and the transient time.
    - The grid resolution ensures an odd number of points in both y and z directions.
    """

    Height = hub_height  + 2 * rotor_diameter 
    if res == 'low':
        Width = (
            2. * np.max(spacing) * (n_turbines - 1) * rotor_diameter * np.sin(
            np.radians(np.max(abs(np.array(wind_direction))))
            )
            + 2 * domain_edge[1] * rotor_diameter
        )
        Height = hub_height  + 2 * rotor_diameter 
    else:
        Width = rotor_diameter * (1. + domain_edge[1])
        Height = hub_height  + 0.5 * rotor_diameter * (1. + domain_edge[1])
    # Set the analysis time based on the lowest wind speed and highest spacing, plus transient
    AnalysisTime = np.ceil(
        (
            (n_turbines - 1) * np.max(spacing) * rotor_diameter 
            + 2 * domain_edge[0] * rotor_diameter
        ) / np.min(ws) 
        + transient 
        + analysis_time
    )
    # Set the time step based on the lowest wind speed and rotor diameter. It cannot be larger than 1 s
    TimeStep = 0.25 #np.round(np.min([1., Cmeander * rotor_diameter / (np.min(ws) * 10.0)]), 1)
    ny = np.ceil(Width/dy)+1
    nz = np.ceil(Height/dz)+1
    # We need to make sure the number of points is odd.
    if ny%2 == 0:
        ny += 1
    if nz%2 == 0:
        nz += 1
    
    NumGrid_Z = int(nz)
    NumGrid_Y = int(ny)
    GridWidth = dy*(ny-1)
    GridHeight = dz*(nz-1)
    Dgrid=min(GridHeight,GridWidth)
    HubHt_for_TS = 1. - 0.5*Dgrid + GridHeight
    

    return (NumGrid_Z, NumGrid_Y, GridHeight, GridWidth, 
            AnalysisTime, TimeStep, HubHt_for_TS)