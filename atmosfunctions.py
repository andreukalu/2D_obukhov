import numpy as np
import pandas as pd

# COMPUTE OBUKHOV LENGTH

# Function to obtain friction velocity
def compute_friction_velocity(u, v, w):
    up = u - np.mean(u)
    vp = v - np.mean(v)
    wp = w - np.mean(w)
    uw = up*wp
    vw = vp*wp
    u_a = (np.mean(uw)**2 + np.mean(vw)**2)**(1/4)

    return u_a

def compute_mixing_ratio(rh, t, p):
    
    # Saturation vapor pressure in hPa
    e_s = 6.112 * np.exp(17.67 * t / (t + 243.5))
    
    # Actual vapor pressure
    e = rh / 100 * e_s
    
    # Mixing ratio
    r = 0.622 * e / (p - e)  # kg/kg
    return r

def compute_virtual_temperature(t, r):
    
    t_k = t + 273.15
    t_v = t_k*(1+0.61*r)

    return t_v

def compute_virtual_potential_temperature(t, rh, p, p0 = 1000):

    # Compute mixing ratio
    r = compute_mixing_ratio(rh, t, p)

    # Compute virtual temperature
    t_v = compute_virtual_temperature(t,r)

    # Gas constant for dry air
    Rd = 287 # J/(kg K)

    # Specific heat at constant pressure
    cp = 1005 # J/(kg K)

    # Compute the potential temperature
    vpt = t_v*(p0/p)**(Rd/cp)

    return vpt

def compute_obukhov_length(u, v, w, t, rh, p, p0 = 1000):

    # Von Karman constant
    k = 0.4

    # Gravitational acceleration
    g = 9.81

    # Compute friction velocity
    u_a = compute_friction_velocity(u, v, w)
    
    # Compute virtual potential temperature
    vpt = compute_virtual_potential_temperature(t, rh, p, p0)

    # Compute kinematic heat flux
    vpt_p = vpt - np.mean(vpt)
    w_p = w - np.mean(w)
    khf = np.mean(vpt_p * w_p)

    # Compute Obukhov length
    L = - (u_a**3 * np.mean(vpt)) / (k * g * khf)

    return L, u_a, khf, np.mean(vpt)

def process_df_obukhov_length(df_min, df_s):
    
    df_s_aux = df_s.copy()
    df_s_aux.set_index("datetime", inplace=True)
    df_min_aux = df_min.set_index('datetime')

    groups = df_s_aux.groupby(pd.Grouper(freq="10min")) #10min
    
    df_out = pd.DataFrame()
    for time_bin, segment in groups:
        u = segment['u_40']
        v = segment['v_40']
        w = segment['w_40']
        t = segment['T_40']

        if time_bin not in df_min_aux.index:
            continue
        df_min_segment = df_min_aux.loc[time_bin].copy()
        rh = df_min_segment['relativehumidity_34']
        p = df_min_segment['airpressure_21']

        L, u_a, khf, vpt_m = compute_obukhov_length(u, v, w, t, rh, p)
        df_min_segment['L'] = L
        df_min_segment['ua'] = u_a
        df_min_segment['khf'] = khf
        df_min_segment['vpt_m'] = vpt_m
        df_out = pd.concat([df_out,df_min_segment], axis=1)
    
    
    df_out = df_out.transpose()
    df_out = df_out.reset_index()
    df_out = df_out.rename(columns={'index': 'datetime'})
    return df_out