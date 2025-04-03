def EC_to_S(EC, t, p):  # t=ref, p=waterdruk
    """Convert electrical conductivity to salinity. Units are in mS/cm.
    Returns the salinity without the correction of Hill.

    Args:
    EC: The electrical conductivity in mS/cm.
    t: The temperature in degrees Celsius.
    p: The pressure of the water in decibar.

    Returns:
    The salinity of the water in psu (g/kg).
    """

    R = EC / 42.914
    a = [0.008, -0.1692, 25.3851, 14.0941, -7.0261, 2.7081]  # a0 - a5
    b = [0.0005, -0.0056, -0.0066, -0.0375, 0.0636, -0.0144]  # b0 - b5
    c = [0.6766097, 2.00564e-2, 1.104259e-4, -6.9698e-7, 1.0031e-9]  # c0 - c4
    d = [3.426e-2, 4.4464e-4, 4.215e-1, -3.107e-3]  # d1 - d4
    e = [2.070e-5, -6.370e-10, 3.989e-15]  # e1 - e3

    rt = sum(c[i] * t**i for i in range(len(c)))

    Rp = 1 + (p * (e[0] + e[1] * p + e[2] * p**2)) / (
        1 + d[0] * t + d[1] * t**2 + (d[2] + d[3] * t) * R
    )

    Rt = R / (Rp * rt)

    S = sum(
        (a[i] + b[i] * (t - 15.0) / (1 + 0.0162 * (t - 15.0))) * (Rt ** (i / 2.0))
        for i in range(len(a))
    )

    return S


def S_to_rho(S, t):  # t in bodem
    """salinity to density

    Arguments:
    t -- the temperature in degrees celcius
    S = the salinity of the water in psu (g/kg)

    Returns:

    rho --  groundwater density in kg/m^3"""

    a = [
        999.842594,
        6.793652 * 10**-2,
        -9.095290 * 10**-3,
        1.001685 * 10**-4,
        -1.120083 * 10**-6,
        6.536332 * 10**-9,
    ]
    b = [
        8.24493 * 10**-1,
        -4.0899 * 10**-3,
        7.6438 * 10**-5,
        -8.2467 * 10**-7,
        5.3875 * 10**-9,
    ]
    c = [-5.72466 * 10**-3, 1.0227 * 10**-4, -1.6545 * 10**-6]
    d = 4.8314 * 10**-4

    rho_f = sum(ai * t**i for i, ai in enumerate(a))
    term2 = sum(bi * t**i for i, bi in enumerate(b))
    term3 = sum(ci * t**i for i, ci in enumerate(c))

    rho = rho_f + term2 * S + term3 * S**1.5 + d * S**2

    return rho
