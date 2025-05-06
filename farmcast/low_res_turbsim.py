import numpy as np

def set_low_res_turbsim(n_turbines, rotor_diameter, hub_height, ws, spacing, wind_direction, Cmeander = 1.9, transient = 120, analysis_time = 600, domain_edge_LR = [1., 1., 1., 1.], dy = 10., dz = 10.):

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
        The transient time to be added to the analysis time (in seconds). Default is 300 seconds.
    analysis_time : float, optional
        The analysis time for the simulation (in seconds). Default is 600 seconds.
    domain_edge_LR : list, optional
        The extra size in rotor diameters along the edges of the domain for x (left and right) and y (top and bottom) for the low-resolution turbsim box. Default is [1., 1.].

    Returns:
    --------
    tuple
        A tuple containing:
        - GridHeight (float): The height of the low-resolution grid (in meters). Set to 2 * hub_height - 1. to stay 1 m above ground.
        - GridWidth (float): The width of the low-resolution grid (in meters).
        - AnalysisTime (float): The analysis time for the simulation (in seconds).
        - TimeStep (float): The time step for the low-resolution simulation (in seconds).
    Notes:
    ------
    - The grid dimensions are calculated based on the rotor diameter and wind direction.
    - The analysis time is determined by the lowest wind speed, highest spacing, and the transient time.
    """


    Height = hub_height  + 2 * rotor_diameter 
    Width = (rotor_diameter + 2. * np.max(spacing) * (n_turbines - 1) * rotor_diameter * np.sin(np.radians(np.max(abs(np.array(wind_direction)))))) + 2 * domain_edge_LR[1] * rotor_diameter
    # Set the analysis time based on the lowest wind speed and highest spacing, plus transient
    AnalysisTime = np.ceil(((n_turbines - 1) * np.max(spacing) * rotor_diameter + 2 * domain_edge_LR[0] * rotor_diameter)/ np.min(ws) + transient + analysis_time)
    # Set the time step based on the lowest wind speed and rotor diameter. It cannot be larger than 1 s
    TimeStep = 0.25 #np.round(np.min([1., Cmeander * rotor_diameter / (np.min(ws) * 10.0)]), 1)
    ny = np.ceil(Width/dy)+1
    nz = np.ceil(Height/dz)+1
    # We need to make sure the number of points is odd.
    if ny%2 == 0:
        ny += 1
    if nz%2 == 0:
        nz += 1
    
    NumGrid_Z_LR = int(nz)
    NumGrid_Y_LR = int(ny)
    GridWidth = dy*(ny-1)
    GridHeight = dz*(nz-1)
    Dgrid=min(GridHeight,GridWidth)
    HubHt_for_TS = 1. - 0.5*Dgrid + GridHeight
    

    return NumGrid_Z_LR, NumGrid_Y_LR, GridHeight , GridWidth, AnalysisTime, TimeStep, HubHt_for_TS