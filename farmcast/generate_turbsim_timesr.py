import numpy as np
import struct

def read_turbsim_bts(filename):
    """ read BTS file, with field: 
                    u    (3 x nt x ny x nz)
                    uTwr (3 x nt x nTwr)
    """

    bts_data = {}


    scl = np.zeros(3, np.float32); off = np.zeros(3, np.float32)
    with open(filename, mode='rb') as f:            
        # Reading header info
        ID, nz, ny, nTwr, nt                      = struct.unpack('<h4l', f.read(2+4*4))
        dz, dy, dt, uHub, zHub, zBottom           = struct.unpack('<6f' , f.read(6*4)  )
        scl[0],off[0],scl[1],off[1],scl[2],off[2] = struct.unpack('<6f' , f.read(6*4))
        nChar, = struct.unpack('<l',  f.read(4))
        info = (f.read(nChar)).decode()
        # Reading turbulence field
        u    = np.zeros((3,nt,ny,nz))
        uTwr = np.zeros((3,nt,nTwr))
        # For loop on time (acts as buffer reading, and only possible way when nTwr>0)
        for it in range(nt):
            Buffer = np.frombuffer(f.read(2*3*ny*nz), dtype=np.int16).astype(np.float32).reshape([3, ny, nz], order='F')
            u[:,it,:,:]=Buffer
            Buffer = np.frombuffer(f.read(2*3*nTwr), dtype=np.int16).astype(np.float32).reshape([3, nTwr], order='F')
            uTwr[:,it,:]=Buffer
        u -= off[:, None, None, None]
        u /= scl[:, None, None, None]
        bts_data['u']    = u
        uTwr -= off[:, None, None]
        uTwr /= scl[:, None, None]
        bts_data['uTwr'] = uTwr
    bts_data['info'] = info
    bts_data['ID']   = ID
    bts_data['dt']   = np.round(dt, 8) # dt is stored in single precision in the TurbSim output
    bts_data['y']    = np.arange(ny)*dy 
    bts_data['y']   -= np.mean(bts_data['y']) # y always centered on 0
    bts_data['z']    = np.arange(nz)*dz +zBottom
    bts_data['t']    = np.round(np.arange(nt)*dt, 8)
    bts_data['zTwr'] =-np.arange(nTwr)*dz + zBottom
    bts_data['zRef'] = zHub
    bts_data['uRef'] = uHub

    return bts_data


def writeTimeSeriesFile(fileOut,yloc,zloc,u,v,w,time):
    """ Write a TurbSim primary input file, 

    """

    print(f'Writing {fileOut}')
    # --- Writing TurbSim user-defined time series file
    with open(fileOut, 'w') as f:
        f.write( '--------------TurbSim v2.00.* User Time Series Input File-----------------------\n')
        f.write( '     Time series input from low-res turbsim run\n')
        f.write( '--------------------------------------------------------------------------------\n')
        f.write( '          3 nComp - Number of velocity components in the file\n')
        f.write( '          1 nPoints - Number of time series points contained in this file (-)\n')
        f.write( '          1 RefPtID - Index of the reference point (1-nPoints)\n')
        f.write( '     Pointyi Pointzi ! nPoints listed in order of increasing height\n')
        f.write( '       (m)     (m)\n')
        f.write(f'       {yloc:.5f}   {zloc:.5f}\n')
        f.write( '--------Time Series-------------------------------------------------------------\n')
        f.write( 'Elapsed Time         Point01u             Point01v           Point01w\n')
        f.write( '         (s)            (m/s)                (m/s)              (m/s)\n')
        for i in range(len(time)):
            f.write(f'\t{time[i]:.2f}\t\t\t  {u[i]:.5f}\t\t\t  {v[i]:.5f}\t\t\t {w[i]:.5f}\n')


def generateTimeSeriesFile(filename, x, y, z, ymid, zmid, TimeStep_HR, AnalysisTime_LR, T):
    """
    Generates a time-series file based on TurbSim binary time-series (BTS) data.
    This function reads a TurbSim BTS file, extracts velocity components at a 
    specified spatial location, applies a time shift based on the x-coordinate, 
    and writes the resulting time-series data to a new file.
    Parameters:
        filename (str): Path to the TurbSim BTS file.
        x (float): x-coordinate of the desired location.
        y (float): y-coordinate of the desired location.
        z (float): z-coordinate of the desired location.
        TimeStep_HR (float): Time step for the high-resolution time-series data.
        T (int): Identifier for the output time-series file.
    Returns:
        AnalysisTime_HR: The total time in the high-resolution time-series data.
    Notes:
        - The function assumes that the BTS file contains velocity components 
          (u, v, w) and spatial coordinates (y, z).
        - The time shift is calculated based on the mean velocity at the specified 
          location and the x-coordinate.
        - The output file is named by appending `USRTimeSeries_T{T}.txt` to the 
          input filename (excluding its original extension).
    
    """
    bts_data = read_turbsim_bts(filename)
    bts_data['t'] = np.round(bts_data['t'], 6) # rounding single precision read as double precision
    bts_data['dt'] = np.round(bts_data['dt'], 6)

    iy = np.argmin(np.abs(bts_data['y']-y))
    iz = np.argmin(np.abs(bts_data['z']-z))


    yloc = bts_data['y'][iy] - y
    zloc = bts_data['z'][iz] - z
    time = bts_data['t']
    id_end = np.argmin(abs(time - AnalysisTime_LR))

    iy_mid = np.argmin(np.abs(bts_data['y']-ymid))
    iz_mid = np.argmin(np.abs(bts_data['z']-zmid))
    Vxyz = bts_data['u'][0,:,iy_mid,iz_mid]
    start_time_step = round( (x/Vxyz.mean())/bts_data['dt'] )
    uvel = np.roll(bts_data['u'][0, :id_end, iy, iz], start_time_step)
    vvel = np.roll(bts_data['u'][1, :id_end, iy, iz], start_time_step)
    wvel = np.roll(bts_data['u'][2, :id_end, iy, iz], start_time_step)

    timeSeriesOutputFile = filename[:-4] + f'_T{T}.txt'

    # Map it to high-res time 
    time_hr = np.arange(0, time[id_end] + TimeStep_HR, TimeStep_HR)
    uvel_hr = np.interp(time_hr, time[:id_end], uvel)
    vvel_hr = np.interp(time_hr, time[:id_end], vvel)
    wvel_hr = np.interp(time_hr, time[:id_end], wvel)

    writeTimeSeriesFile(timeSeriesOutputFile, yloc, zloc, uvel_hr, vvel_hr, wvel_hr, time_hr)

    AnalysisTime_HR = (len(time_hr) - 1) * TimeStep_HR

    return AnalysisTime_HR

