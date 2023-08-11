import numpy as np
import matplotlib.pyplot as plt
from astropy.utils.data import get_pkg_data_filename
from astropy.io import fits
from scipy.optimize import curve_fit

def closest(x, arr):
    difference_array = np.absolute(arr-x)
    # find the index of minimum element from the array
    index = difference_array.argmin()
    return index

def Atmospheric_dispersion_correction(cube_path, 
                                      center_x=True, 
                                      center_y=True, 
                                      range_x = None, 
                                      range_y = None):
    if len(data) == 0:
        obs = get_pkg_data_filename(cube_path)
        hdul = fits.open(cube_path)
        header = hdul[0].header
        N = header["NAXIS3"]
        wave = np.zeros(N)
        #obtain the data and wavelength
        data = fits.getdata(obs, ext=0)[:, :, :]

        for i in range(N):
            wave[i] = (i+header["CRPIX3"])*header["CDELT3"] + header["CRVAL3"]
    
    if (len(data) > 0) and (len(wave) == 0):
        print("wave= ")
        print("Error: If you provide the data, also should provide the wavelength")

    if len(data) > 0:
        N = len(data)

    pix_x = len(data[0, 0, :])
    pix_y = len(data[0, :, 0])

    x_coords_center = np.zeros(N)
    for l in range(N):
        suma_x = 0
        mass_center_x = 0

        for i in range(pix_x):
            mass_center_x += (i*np.sum(data[l, :, i]))
            suma_x += np.sum(data[l, :, i])

        x_coords_center[l] = mass_center_x / suma_x

    if center_x == False:
        x_coords_center = np.ones(N)*np.nanmedian(x_coords_center)


    y_coords_center = np.zeros(N)
    for l in range(N):
        suma_y = 0
        mass_center_y = 0

        for j in range(pix_y):
            mass_center_y += (j*np.sum(data[l, j, :]))
            suma_y += np.sum(data[l, j, :])


        y_coords_center[l] = mass_center_y / suma_y

    if center_y == False:
        y_coords_center = np.ones(N)*np.nanmedian(y_coords_center)


    fig, axes = plt.subplots(2, 1, figsize=(18, 6))

    # Define the parabola function
    def parabola(x, a, b, c):
        return a*x**2 + b*x + c

    if range_y == None:
        # Fit a parabola to the data using curve_fit()
        popt_y, pcov_y = curve_fit(parabola, wave[:], y_coords_center[:] - y_coords_center[0])
    if range_y != None:
        # Fit a parabola to the data using curve_fit()
        lower = closest(range_y[0], wave)
        upper = closest(range_y[1], wave)
        popt_y, pcov_y = curve_fit(parabola, wave[lower:upper], y_coords_center[lower:upper] - y_coords_center[0])

    # Plot the data and the parabola

    axes[0].set_title("Movement of the center in y of the object through wavelength")
    axes[0].plot(wave, y_coords_center,  linewidth=0.3, c="k", alpha=1, label='center in y-spaxels')
    axes[0].plot(wave, y_coords_center[0] + parabola(wave, *popt_y), c="red", label='parabola')
    axes[0].plot(wave, y_coords_center[0] + np.round(parabola(wave, *popt_y)), linestyle=":", c="purple", label='round parabola', zorder=10)
    axes[0].set_ylim(-1, pix_y + 1)
    axes[0].set_xlabel("Wavelength [nm]", fontsize=14)
    axes[0].set_ylabel("y-spaxels", fontsize=14)
    axes[0].grid(False)
    axes[0].legend()

    if range_x == None:
        # Fit a parabola to the data using curve_fit()
        popt_x, pcov_x = curve_fit(parabola, wave[:], x_coords_center[:] - x_coords_center[0])

    if range_x != None:
        lower = closest(range_x[0], wave)
        upper = closest(range_x[1], wave)
        popt_x, pcov_x = curve_fit(parabola, wave[lower:upper], x_coords_center[lower:upper] - x_coords_center[0])

    # Plot the data and the parabola

    axes[1].set_title("Movement of the center in x of the object through wavelength")
    axes[1].plot(wave, x_coords_center,  linewidth=0.3, c="k", alpha=1, label='center in y-spaxels')
    axes[1].plot(wave, x_coords_center[0] + parabola(wave, *popt_x), c="red", label='parabola')
    axes[1].plot(wave, x_coords_center[0] + np.round(parabola(wave, *popt_x)), linestyle=":", c="purple", label='round parabola', zorder=10)
    axes[1].set_ylim(-1, pix_x + 1)
    axes[1].set_xlabel("Wavelength [nm]", fontsize=14)
    axes[1].set_ylabel("x-spaxels", fontsize=14)
    axes[1].grid(False)
    axes[1].legend()
    plt.show()

    if center_y == True: 

        y_mov = np.round(y_coords_center[0] + parabola(wave, *popt_y))
        y_mov_float = y_coords_center[0] + parabola(wave, *popt_y)


    if center_y == False:

        y_mov = np.round(y_coords_center)
        y_mov_float = y_coords_center


    y_variation = y_mov_float - y_mov
    y_dif_center = int(np.max(y_mov) - np.min(y_mov))
    long_y = int(pix_y + y_dif_center)
    y_offset = y_mov - y_mov[0] 


    if center_x == True:

        x_mov = np.round(x_coords_center[0] + parabola(wave, *popt_x))
        x_mov_float = x_coords_center[0] + parabola(wave, *popt_x)


    if center_x == False:

        x_mov = np.round(x_coords_center)
        x_mov_float = x_coords_center


    x_variation = x_mov_float - x_mov
    x_dif_center = int(np.max(x_mov) - np.min(x_mov))
    long_x = int(pix_x + x_dif_center)
    x_offset = x_mov - x_mov[0] 


    medianas = np.zeros((pix_y, pix_x))
    for i in range(pix_x):
        for j in range(pix_y):
            medianas[j, i] = np.nanpercentile(data[:, j, i], 50)

    corrected_ydata = np.zeros((N, long_y, pix_x))
    for l in range(N):
        for i in range(pix_x):
            for j in range(pix_y):
                if (y_variation[l]) < 0:
                    if j == 0:
                        corrected_ydata[l, int(j - y_offset[l]), i] = data[l, j, i] * (1 + (y_variation[l]))
                    else:
                        ponderado = medianas[j, i] / medianas[j-1, i]
                        corrected_ydata[l, int(j - y_offset[l]), i] = data[l, j, i] * (1 + (y_variation[l])) + data[l, j-1, i] * (y_variation[l]) * (-1) * ponderado 
                if (y_variation[l]) >= 0:
                    if j == pix_y-1:
                        corrected_ydata[l, int(j - y_offset[l]), i] = data[l, j, i] * (1 - (y_variation[l]))
                    else:
                        ponderado = medianas[j, i] / medianas[j+1, i]
                        corrected_ydata[l, int(j - y_offset[l]), i] = data[l, j, i] * (1 - (y_variation[l])) + data[l, j+1, i] * (y_variation[l]) / ponderado

                if long_y > pix_y:
                    for d in range(long_y - pix_y):
                        corrected_ydata[l, int((long_y - y_offset[l] - d -1)%long_y), i] = None

    corrected_xdata = np.zeros((N, long_y, long_x))
    for l in range(N):
        for i in range(pix_x):
            for j in range(pix_y):
                if (x_variation[l]) < 0:
                    if i == 0:
                        corrected_xdata[l, j, int(i - x_offset[l])] = corrected_ydata[l, j, i] * (1 + (x_variation[l]))
                    else:
                        ponderado = medianas[j, i] / medianas[j, i-1]
                        corrected_xdata[l, j, int(i - x_offset[l])] = corrected_ydata[l, j, i] * (1 + (x_variation[l])) + corrected_ydata[l, j, i-1] * (x_variation[l]) * (-1) * ponderado 
                if (x_variation[l]) >= 0:
                    if i == pix_x-1:
                        corrected_xdata[l, j, int(i - x_offset[l])] = corrected_ydata[l, j, i] * (1 - (x_variation[l]))
                    else:
                        ponderado = medianas[j, i] / medianas[j, i+1]
                        corrected_xdata[l, j, int(i - x_offset[l])] = corrected_ydata[l, j, i] * (1 - (x_variation[l])) + corrected_ydata[l, j, i+1] * (x_variation[l]) / ponderado

                if long_x > pix_x:
                    for d in range(long_x - pix_x):
                        corrected_xdata[l, j, int((long_x - x_offset[l] - d -1)%long_x)] = None

    corrected_data = corrected_xdata[:, y_dif_center:int(long_y-y_dif_center), x_dif_center:int(long_x-x_dif_center)]

    x_center = np.round(x_coords_center[0] + parabola(wave, *popt_x)[0]) - x_dif_center
    y_center = np.round(y_coords_center[0] + parabola(wave, *popt_y)[0]) - y_dif_center
    return corrected_data, wave, (x_center, y_center)



def Sigma_clipping_adapted_for_IFU(cube_path, data=np.array([]), wave=np.array([]), A=5, window=100): #, dim_y=4, dim_x=1.8, min_lambda=0, max_lambda=1000, centro = (0, 1)):
    if len(data) == 0:
        obs = get_pkg_data_filename(cube_path)
        hdul = fits.open(cube_path)
        header = hdul[0].header
        N = header["NAXIS3"]
        wave = np.zeros(N)
        #obtain the data and wavelength
        data = fits.getdata(obs, ext=0)[:, :, :]

        for i in range(N):
            wave[i] = (i+header["CRPIX3"])*header["CDELT3"] + header["CRVAL3"]
    
    if (len(data) > 0) and (len(wave) == 0):
        print("wave= ")
        print("Error: If you provide the data, also should provide the wavelength")

    if len(data) > 0:
        N = len(data)

    clean_data = data.copy()

    n = N - window//2 
    pix_x = len(data[0, 0, :])
    pix_y = len(data[0, :, 0])

    #dx = dim_x / (pix_x + 1)
    #dy = dim_y / (pix_y + 1)

    #distance_matrix = np.zeros((pix_y, pix_x))
    #for i in range(pix_x):
    #    for j in range(pix_y):
    #        distance_matrix[j, i] = np.sqrt( (dy*(j-centro[0]))**2 + (dx*(i-centro[1]))**2)

    #max_distance = np.max(distance_matrix)
    #radius = np.linspace(0, max_distance, 100)



    medianas = np.zeros((pix_y, pix_x))
    IQR = np.zeros(N)

    for lambda_wave in range(window//2, n):
        for i in range(pix_x):
            for j in range(pix_y):
            
                medianas[j, i] = np.nanpercentile(clean_data[lambda_wave-window//2:lambda_wave+window//2, j, i], 50)
        
        variable_y = (clean_data[lambda_wave]/medianas).reshape(pix_x*pix_y)
        #variable_x = distance_matrix.reshape(pix_x*pix_y)
        mediana = np.nanpercentile(variable_y, 50)
        deviation = variable_y - mediana
        upper_limit = np.nanpercentile(deviation, 75)
        lower_limit = np.nanpercentile(deviation, 25)
        IQR[lambda_wave] = upper_limit - lower_limit
        deviation = deviation.reshape(pix_y, pix_x)

        for lambda_x in range(pix_x):
            for lambda_y in range(pix_y):
                if (deviation[lambda_y, lambda_x] > A*upper_limit) or (deviation[lambda_y, lambda_x] < A*lower_limit):
                    clean_data[lambda_wave, lambda_y, lambda_x] = medianas[lambda_y, lambda_x]

    return clean_data, wave
    

def optimal_radius_selection_IFU(cube_path, min_lambda=0, max_lambda=1000, dim_y=4, dim_x=1.8, centro=(0,0), upper_lam=5000, lower_lam=2000, spaxelsFit=9, error=3):    
    obs = get_pkg_data_filename(cube_path)

    #obtain the data and wavelength
    data = fits.getdata(obs, ext=0)[:, :, :]
    wave = np.linspace(min_lambda, max_lambda, len(data))

    N = len(data)
    pix_x = len(data[0, 0, :])
    pix_y = len(data[0, :, 0])

    dx = dim_x / (pix_x + 1)
    dy = dim_y / (pix_y + 1)

    distance_matrix = np.zeros((pix_y, pix_x))
    for i in range(pix_x):
        for j in range(pix_y):
            distance_matrix[j, i] = np.sqrt( (dy*(j-centro[0]))**2 + (dx*(i-centro[1]))**2)

    max_distance = np.max(distance_matrix)
    radius = np.linspace(0, max_distance, 500)

    upper_value = closest(upper_lam, wave)
    lower_value = closest(lower_lam, wave)

    n = len(radius)
    lambda_values = wave[lower_value:upper_value]
    StoN_radius = np.zeros(n)
    signal_r = np.zeros(n)
    noise_r = np.zeros(n)
    radius_spaxel = np.zeros(n)
    spec_r = np.zeros((n, len(lambda_values)))

    def linear(x, m, c):
        return m*x + c

    for r in range(1, n):
        flujo_sumado = np.zeros(len(lambda_values))
        pixel_count = 0
        for i in range(pix_x):
            for j in range(pix_y):
                ventana = data[lower_value:upper_value, j, i]
                if distance_matrix[j, i] < radius[r]:
                    flujo_sumado = flujo_sumado + ventana
                    pixel_count += 1
        radius_spaxel[r] = pixel_count
        signal_r[r] = np.sum(flujo_sumado) 

        popt, pcov = curve_fit(linear, lambda_values, flujo_sumado)
        m, c = popt
        noise_r[r] = np.std((flujo_sumado - linear(lambda_values, m, c)))
        spec_r[r] =  flujo_sumado
        StoN_radius[r] = signal_r[r] / noise_r[r]
        
    indiceRadio = np.max([np.where(radius_spaxel == spaxelsFit)[0]])

    def f(x, alpha, cte):
        return alpha*np.sqrt(x + cte) 

    # Fit a line to the spectrum
    popt, pcov = curve_fit(f, signal_r[1:indiceRadio], StoN_radius[1:indiceRadio])
    alpha, cte = popt

    for i in range(1, len(radius)):
        if np.abs(f(signal_r[i], alpha, cte) - StoN_radius[i]) > f(signal_r[i], alpha, cte)*(error/100):
            indiceRadio = i - 1
            break

    fig, axes = plt.subplots(1, 1, figsize=(10, 6))

    axes.set_title("SNR as function of the signal increase")
    axes.plot(signal_r[1:], StoN_radius[1:], c="k", label = "Real S/N")
    axes.set_ylabel("S/N", fontsize=18)
    axes.set_xlabel("log(Signal)", fontsize=18)
    axes.plot(signal_r[1:], f(signal_r[1:], alpha, cte), c="red", label="Teoritical S/N")
    axes.fill_between(signal_r[1:], (1-error/100)*f(signal_r[1:], alpha, cte), (1 + error/100)*f(signal_r[1:], alpha, cte), color="red", alpha=0.1)
    axes.plot(signal_r[indiceRadio], StoN_radius[indiceRadio],  ".", c="blue", markersize=10, label="Optimal Radius: "+ str(np.round(radius[indiceRadio],2 ))+ '"')
    axes.legend()
    axes.grid(False)
    plt.show()

    return (radius[indiceRadio], radius_spaxel[indiceRadio])



    

