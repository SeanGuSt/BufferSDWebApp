import numpy as np

from js import document, chartCurve, JSON, setupTable, abSwap, programAtLeastLevel, plotThing, plotBC, numberCleanup, changeProgramLevel, programAtLevel
from pyodide.ffi import create_proxy
from json import dumps, loads
import pandas as pd
import io
import asyncio
#Defaults, in case the user hasn't something to input
defaultDict = {
        'pH':0.05,
        'Order': 15,
        'MinConc':0.001,
        'NaClpercent':2,
        'NpKs':7,
        'LB':2,
        'UB':12,
        'pK_tol':0.2,
        'Trim_beg':0,
        'Trim_end':0,
        'MinGap':0.3,
        'Init_Vol':0.05,
        'Increment':0.1,
        'HCl':2,
        'NaOH':2,
        'ingredient':'ingredient',
        'conTitr':100
        }
#global Buffer Capacity array, BC
BC = None
oriBC = None
fillBC = None
orifillBC = None
measuredpH = -1
buftable = None
acid_x = None
acid_y = None
base_x = None
base_y = None
def set_globals(key, value):
    globals()[key] = value
#Creating proxies is necessary to allow a python function to be used for an event.
#These functions must be asynchronous, which is achieved by putting "async" before def (need to import asyncio)
async def preParamsSetter(event):#Equivalent to app.setParamTable
    etf = event.target.files
    if etf is not None:
        if etf.length > 0:
            for file in etf:
                trueFile = await file.text()
                givenDict = pd.read_csv(io.StringIO(trueFile), engine="python").loc[:, ["Value", "Parameter"]].set_index("Parameter").T.to_dict('list')
                pyParamsSetter(True, givenDict)#python, found below
    else:
        #defaultDic = pd.read_csv("static/paramfile_test.csv", engine="python").loc[:, ["Value", "Parameter"]].set_index("Parameter").T.to_dict('list')
        pyParamsSetter(False, defaultDict)
    changeProgramLevel(1)
async def prePD(event):
    changeProgramLevel(1)
async def prePlotTitration(event):#Generic version of app.OpenBaseTitrationButtonPushed & app.OpenAcidTitrationButtonPushed
    etf = event.target.files
    gotFiles = etf.length>0
    if not programAtLeastLevel(1):
            return False
    if event.target.id == "acid_titr_button":
        index = 0
    else:
        if not programAtLeastLevel(2):
            return False
        index = 1
    changeProgramLevel(2 + index)#javascript, GraphHandling.js
    if gotFiles:
        for file in etf:
            trueFile = await file.text()
        f = open("temp.txt", "w")
        f.write(trueFile)
        f.close()
        x, y = getTitrationData("temp.txt")#python, plotTitration.py
    else:
        x = [0]
        y = [0]
    if index==0:
        set_globals("acid_x", x)
        set_globals("acid_y", y)
    else:
        set_globals("base_x", x)
        set_globals("base_y", y)
    results = xy2dataset(x, y)
    plotThing(py2js(results), index)#javascript, GraphHandling.js
    

async def preGenBCCurve(event):#Equivalent of app.GenerateBCCurveButtonPushed
    if not programAtLeastLevel(3):#javascript, GraphHandling.js
        return False
    changeProgramLevel(4)
    init_vol = float(docel("Init_Vol").value)
    molHCl = float(docel("HCl").value)
    molNaOH = float(docel("NaOH").value)
    removeVal = float(docel("pH").value)
    mingaps = float(docel("MinGap").value)
    increment = float(docel("Increment").value)
    NaClPercent = float(docel("NaClpercent").value)
    set_globals("measuredpH", (acid_y[0] + base_y[0])/2)
    D2B, oriBC, fillBC = pyGenBCCurve(init_vol, molHCl, molNaOH, removeVal, mingaps, increment, acid_x, acid_y, base_x, base_y)#python, GenBCCurve.py
    fillcurve = xy2dataset(fillBC)
    oricurve = xy2dataset(oriBC)
    set_globals("oriBC", oriBC)
    set_globals("BC", oriBC)
    set_globals("fillBC", fillBC)
    set_globals("orifillBC", fillBC)
    maxBC = np.amax(BC[:,1])
    WC = genWater(maxBC, NaClPercent, 1.5, 12.5)
    plotBC(py2js(fillcurve), py2js(oricurve), maxBC)
    watercurve = xy2dataset(WC)
    plotThing(py2js(watercurve), 4, True, "Water")#javascript, graphHandling.js
async def shiftGraph(event):
    if not programAtLeastLevel(4):#Level 4 or higher required
        return False
    shift = float(docel("electrode_shift").value)
    newShift = np.zeros(oriBC.shape)
    newShift[:,0] += shift
    set_globals("BC", oriBC + newShift)
    newShift = np.zeros(orifillBC.shape)
    newShift[:,0] += shift
    set_globals("fillBC", orifillBC + newShift)
    maxBC = np.amax(BC[:,1])
    plotBC(py2js(xy2dataset(fillBC)), py2js(xy2dataset(BC)), maxBC)
    changeProgramLevel(4.3)

async def trimGraph(event):
    if not programAtLeastLevel(4):#Level 4 or higher required
        return False
    trimbeg = int(docel("Trim_beg").value)
    trimend = int(docel("Trim_end").value)
    shift = float(docel("electrode_shift").value)
    [BCpts, cols] = oriBC.shape
    if trimbeg+trimend > BCpts:
        return False
    set_globals("BC", oriBC[range(trimbeg, BCpts), :])
    [BCpts, cols] = BC.shape
    BC[:, 0] += shift
    set_globals("BC", BC[range(BCpts-trimend), :])
    maxBC = np.amax(BC[:,1])
    plotBC(py2js(xy2dataset(fillBC)), py2js(xy2dataset(BC)), maxBC)
    if event.target.id == "Trim_beg":
        index = 0.5
    else:
        index = 0.8
    changeProgramLevel(4 + index)
    
async def preModelBCCurve(event):#Equivalent of part of app.ModelBCCurveButtonPushed
    if not programAtLeastLevel(4):
        return False
    order = int(docel("Order").value)
    #initialize optimization with pK distribution across pts
    NpKs = int(docel("NpKs").value)
    minConc = float(docel("MinConc").value)
    pK_tol = float(docel("pK_tol").value)
    LB = float(docel("LB").value)
    UB = float(docel("UB").value)
    NaClpercent = float(docel("NaClpercent").value)
    X0, Y0 = dataset2xy(2)#init X and Y vals (Nx1) N= no. data points)
    X1, Y1 = dataset2xy(3)
    X = np.hstack((X0, X1))
    Y = np.hstack((Y0, Y1))
    Y = Y[np.argsort(X)]
    X.sort()
    buftable, tbetainfo, SPX = pyModelBCCurve(order, NpKs, minConc, pK_tol, NaClpercent, LB, UB, X, Y)#python, ModelBCCurve.py
    set_globals("buftable", buftable)
    bcmat = xy2dataset(tbetainfo["BCCurve"])
    maxBC = np.amax(BC)
    if SPX["BCmat"][0, 0] != 0:
        WC = xy2dataset(tbetainfo["waterCurve"])
    else:
        WC = xy2dataset(genWater(maxBC, NaClpercent, 1, 13))
    plotThing(py2js(bcmat), 5, True, "Buffer Approx.")
    plotThing(py2js(WC), 6, True, "Water Approx.")
    changeProgramLevel(5)#Do not move
    setupTable(py2js(buftable))
    numberCleanup("sse", SPX["SSE"], -3)
    numberCleanup("tb", tbetainfo["tBeta"])
    useAdjC()
async def preabSwap(event):
    global buftable
    if not programAtLevel(5):
        return False
    cell, newLetter = abSwap(event)
    if cell:
        buftable[2][cell] = newLetter
        useAdjC()
async def preUseAdjC(event):
    if not programAtLevel(5):
        return False
    useAdjC()
def main():#Sets the events for certain buttons and fields on BreditForm
    docel("paramFile").addEventListener("change", create_proxy(preParamsSetter), False)
    docel("paramDefaults").addEventListener("change", create_proxy(prePD), False)
    docel("acid_titr_button").addEventListener("change", create_proxy(prePlotTitration), False)
    docel("base_titr_button").addEventListener("change", create_proxy(prePlotTitration), False)
    docel("BC_Curve_button").addEventListener("click", create_proxy(preGenBCCurve), False)
    docel("electrode_shift").addEventListener("change", create_proxy(shiftGraph), False)
    docel("Trim_beg").addEventListener("change", create_proxy(trimGraph), False)
    docel("Trim_end").addEventListener("change", create_proxy(trimGraph), False)
    docel("adjc_checkbox").addEventListener("change", create_proxy(preUseAdjC), False)
    docel("BC_Model_button").addEventListener("click", create_proxy(preModelBCCurve), False)
    docel("myTable").addEventListener("click", create_proxy(preabSwap), False)
def dataset2xy(dataset_ind):#Translates chart.js datasets into numpy arrays
    titr = js2py(chartCurve.data.datasets[dataset_ind].data)
    x = np.arange(len(titr), dtype=float)
    y = np.arange(len(titr), dtype=float)
    i = 0
    for titrDict in titr:
        x[i] = titrDict["x"]
        y[i] = titrDict["y"]
        i+=1
    return x, y
def xy2dataset(*data):#Translates numpy arrays into chart.js datasets
    dataset = []
    if len(data) == 1:
        xy = data[0]
        for i in range(len(xy[:,0])):
            dataset.append({'x':xy[i, 0], 'y':xy[i, 1]})
        return dataset
    elif len(data) == 2:
        x = data[0]
        y = data[1]
        for i in range(len(x)):
            dataset.append({'x':x[i], 'y':y[i]})
        return dataset
    else:
        return False

def py2js(x):
    return JSON.parse(dumps(x))

def js2py(x):
    return loads(JSON.stringify(x))

def docel(x):
    return document.getElementById(x)

def pyParamsSetter(isChecked, givenDict):
    if isChecked:#Assign values from givenDict
        for x, y in givenDict.items():
            docel(x).value = py2js(y)
    else:#otherwise clear all fields
        for x in givenDict:
            docel(x).value = ""
          
def genWater(maxBC, NaClpercent, start, finish, start_inc = 0.075, finish_inc = 0.1, epsilon = 0.0001, step = 0.05):
    ABmat = np.zeros((1, 2))
    for i in range(1, 11):
        waterpHvec = np.arange(start, finish+epsilon, step)
        WC = BetaModel_AB(ABmat, NaClpercent, waterpHvec)
        maxWC = np.amax(WC[:,1])
        if maxWC < 1.7*maxBC:
            break
        else:
            start += i*start_inc
            finish -= i*finish_inc
    
    return WC
def BetaModel_AB(ABmat, NaClpercent, pHvec):
    if ABmat.ndim > 1:
        Conc = ABmat[:,0]
        pKa = ABmat[:,1] 
    else:
        Conc = np.array(ABmat[0], ndmin=1)
        pKa = np.array(ABmat[1], ndmin=1)
    const = 2.302585 #natural log of 10
    Temp = 25
    IonicStr = NaClpercent/5.84
    Kw = 10**-AdjustpKaMonoprotic(14, IonicStr, Temp)
    pKa = AdjustpKaMonoprotic(pKa, IonicStr, Temp)
    Ka = 10**-pKa
    num_buffers = np.amax(np.shape(Conc))
    H = 10**-pHvec
    num_pHvals = np.amax(np.shape(pHvec))
    OH = Kw/H
    buffvecs = np.zeros((num_pHvals, num_buffers))
    BCCurve = np.zeros((num_pHvals, 2))
    for j in range(num_buffers):
        buffvecs[:,j] = Conc[j]*Ka[j]*H/np.power(H+Ka[j], 2)
    buffsum = np.sum(buffvecs, 1)
    BCCurve[:,0] = pHvec
    BCCurve[:,1] = const*(buffsum + OH + H)
    return BCCurve

def AdjustpKaMonoprotic(pKo, I, TempC):
    b = 0.3
    epsilon = 78.3808
    degK = TempC + 273
    A = 1.825*(10**6)*np.power(epsilon*degK, -3/2)
    temp = -b*I + np.sqrt(I)/(1+np.sqrt(I))
    return pKo - 2*A*temp

def useAdjC():
        isChecked = docel("adjc_checkbox").checked
        if isChecked:
            adjC_results = pyGetAdjCT(measuredpH, buftable, float(docel("NaClpercent").value))
            adjC = adjC_results.x[0]
            numberCleanup("adjc", adjC)
        else:
            adjC = 0
            docel("adjc").value = ""
        pH = CalcpH_ABT(buftable, float(docel("NaClpercent").value), adjC)
        numberCleanup("eph", pH)
main()