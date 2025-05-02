from farmcast.generate_turbsim_timesr import generateTimeSeriesFile
import os

def test_generate_turbsim_timesr():
    """
    Test the generateTimeSeriesFile function.
    This test checks if the function generates a time-series file correctly.
    """
    # Define input parameters
    run_dir = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(run_dir, "ws6.00_s0_TI0.06_shear0.20.bts")
    x = 0.0
    y = 0.0
    z = 0.0
    TimeStep_HR = 0.1
    T = 1

    # Call the function to generate the time-series file
    generateTimeSeriesFile(filename, x, y, z, TimeStep_HR, T)
