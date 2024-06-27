import Messages as msg
from static.pyscripts import plotTitration, GenBCCurve, ModelBCCurve, fminconpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#Inputting files functions
def input_getFile(message, debug_override):
    filepath = debug_override if debug_override else input(message)
    while True:
        try:
           print(msg.BSC_WAIT_PLZ)
           file = open(filepath)
           return filepath
        except: #If it fails, try again.
            filepath = input(msg.ERR_FILE_404)
def get_paramDict(debug_override = ""):
    #Gets the parameters from the csv file.
    #To save time during testing, you can input the filepath to your files putting them as function inputs in Command_Line_Buffer.py
    while True:
        try:
            #Turns the parameters into a dictionary. The names of these items CANNOT change.
            paramDict = pd.read_csv(input_getFile(msg.FIL_PARM_CSV, debug_override)).loc[:, ["Value", "Parameter"]].set_index("Parameter").T.to_dict('list')
            for key, value in paramDict.items():
                paramDict[key] = value[0]
            return paramDict
        except: #If it fails, try again.
            print(msg.ERR_CANT_LOAD_PARAMS)
def get_titration(message, debug_override = ""):
    #Load the titrarion data from an rpt file.
    #To save time during testing, you can input the filepath to your files putting them as function inputs in Command_Line_Buffer.py
    while True:
        try:
            titration = input_getFile(message, debug_override)
            #Runs the data through getTitrationData from plotTitration.py
            x, y = plotTitration.getTitrationData(titration)
            return fixup([x, y])
        except: #If it fails, try again.
            print(msg.ERR_CANT_LOAD_TITRATION)

#Generate BC Curve
def get_BC_outline(init_vol, molHCl, molNaOH, removeVal, mingaps, increment, NaClPercent, acid, base):
    print(msg.BSC_GEN_BC_CURVE)
    acid_x = acid[:, 0]; acid_y = acid[:, 1]
    base_x = base[:, 0]; base_y = base[:, 1]
    D2B, oriBC, fillBC = GenBCCurve.pyGenBCCurve(init_vol, molHCl, molNaOH, removeVal, mingaps, increment, acid_x, acid_y, base_x, base_y)
    maxBC = np.amax(oriBC[:,1])
    WC = fminconpy.genWater(maxBC, NaClPercent, 1.5, 12.5)
    oriBC = fixup(oriBC); fillBC = fixup(fillBC); WC = fixup(WC)
    return D2B, oriBC, fillBC, WC

def fixup(plot):
    plot = np.array(plot)
    if plot.shape[0] == 2:#Need a better way to ensure things go correctly. Right now, this assumes there will be 2 columns (for x and y values) but not 2 entries
        plot = plot.T
    return plot

def shift_and_trim_graph(trimbeg, trimend, electrode_shift, oriBC, fillBC):
    print(msg.BSC_SHIFT_TRIM_CURVE)
    BCpts = oriBC.shape[0]
    BC = oriBC
    if trimbeg+trimend <= BCpts:
        BC = oriBC[range(trimbeg, BCpts-trimend), :]
        BC[:, 0] += electrode_shift
        newFill = np.zeros(fillBC.shape)
        newFill[:,0] += electrode_shift
        fillBC += newFill
    return BC, fillBC

def get_BC_curve(order, NpKs, minConc, pK_tol, NaClpercent, LB, UB, BC, fillBC):
    print(msg.BSC_MDL_BC_CURVE)
    #Stacks the Buffer Capacity Curve with its filler, merging the two into one array
    X = np.hstack((BC[:, 0], fillBC[:, 0]))#pH values, x axis
    Y = np.hstack((BC[:, 1], fillBC[:, 1]))#BC values, y axis
    Y = Y[np.argsort(X)]
    X.sort()
    buftable, tbetainfo, SPX = ModelBCCurve.pyModelBCCurve(order, NpKs, minConc, pK_tol, NaClpercent, LB, UB, X, Y)#python, ModelBCCurve.py
    maxBC = np.amax(BC)
    if SPX["BCmat"][0, 0] != 0:
        WCApprox = tbetainfo["waterCurve"]
    else:
        WCApprox = fminconpy.genWater(maxBC, NaClpercent, 1, 13)
    tbetainfo["BCCurve"] = fixup(tbetainfo["BCCurve"])
    WCApprox = fixup(WCApprox)
    return buftable, tbetainfo, SPX, WCApprox

def make_and_save_plot(plotName, plotFileName, xlabel = "x-axis", ylabel = "y-axis", plots = {}):
    fig, ax = plt.subplots()
    for key, plot in plots.items():
        key = key.split("_")
        if key[1] == "scatter":
            ax.scatter(plot[:, 0], plot[:, 1])
        else:
            ax.plot(plot[:, 0], plot[:, 1])
    ax.set(xlabel=xlabel, ylabel=ylabel,
       title=plotName)
    fig.savefig(plotFileName)