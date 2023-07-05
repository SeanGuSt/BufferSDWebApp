from js import document, chartCurve, JSON, haveAllNeccesities, plotThing, plotBC, tableSetup, numberCleanup
from pyodide.ffi import create_proxy
from json import dumps, loads
import numpy as np
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
def set_globalBC(x):
    global BC
    BC = x
#Creating proxies is necessary to allow a python function to be used for an event.
#These functions must be asynchronous, which is achieved by putting "async" before def (need to import asyncio)
async def preParamsSetter(event):#Equivalent to app.setParamTable
    etf = event.target.files
    if etf.length>0:
        for file in etf:
            trueFile = await file.text()
            givenDict = pd.read_csv(io.StringIO(trueFile), engine="python").loc[:, ["Value", "Parameter"]].set_index("Parameter").T.to_dict('list')
            pyParamsSetter(True, givenDict)#python, found below
    else:
        pyParamsSetter(False, defaultDict)
async def prePlotTitration(event):#Generic version of app.OpenBaseTitrationButtonPushed & app.OpenAcidTitrationButtonPushed
    etf = event.target.files
    gotFiles = etf.length>0
    if event.target.id == "acid_titr_button":
        index = 0
    else:
        index = 1
    if gotFiles:
        for file in etf:
            trueFile = await file.text()
        f = open("temp.txt", "w")
        f.write(trueFile)
        f.close()
        x, y = getTitrationData("temp.txt")#python, plotTitration.py
    else:
        x = 0
        y = 0
    results = xy2dataset(x, y)
    plotThing(py2js(results), py2js(index), py2js(gotFiles))#javascript, GraphHandling.js
async def preGenBCCurve(event):#Equivalent of app.GenerateBCCurveButtonPushed
    if not haveAllNeccesities():#javascript, GraphHandling.js
        return False
    init_vol = float(docel("Init_Vol").value)
    molHCl = float(docel("HCl").value)
    molNaOH = float(docel("NaOH").value)
    removeVal = float(docel("pH").value)
    mingaps = float(docel("MinGap").value)
    increment = float(docel("Increment").value)
    NaClPercent = float(docel("NaClpercent").value)
    acid_x, acid_y = dataset2xy(0)
    base_x, base_y = dataset2xy(1)
    D2B, oriBC, BC = pyGenBCCurve(init_vol, molHCl, molNaOH, removeVal, mingaps, increment, acid_x, acid_y, base_x, base_y)#python, GenBCCurve.py
    fillcurve = xy2dataset(BC)
    oricurve = xy2dataset(D2B["BC"])
    set_globalBC(BC)
    maxBC = np.amax(BC[:,1])
    WC = genWater(maxBC, NaClPercent, 1.5, 12.5)
    plotBC(py2js(fillcurve), py2js(oricurve), py2js(maxBC))
    watercurve = xy2dataset(WC)
    plotThing(py2js(watercurve), py2js(2), py2js(True))#javascript, graphHandling.js

async def preModelBCCurve(event):#Equivalent of part of app.ModelBCCurveButtonPushed
    order = int(docel("Order").value)
    #initialize optimization with pK distribution across pts
    NpKs = int(docel("NpKs").value)
    minConc = float(docel("MinConc").value)
    pK_tol = float(docel("pK_tol").value)
    LB = float(docel("LB").value)
    UB = float(docel("UB").value)
    NaClpercent = float(docel("NaClpercent").value)
    X, Y = dataset2xy(1)#init X and Y vals (Nx1) N= no. data points)
    buftable, tbetainfo, SPX = pyModelBCCurve(order, NpKs, minConc, pK_tol, NaClpercent, LB, UB, X, Y)#python, ModelBCCurve.py
    bcmat = xy2dataset(tbetainfo["BCCurve"])
    maxBC = np.amax(BC)
    if SPX["BCmat"][0, 0] != 0:
        WC = xy2dataset(tbetainfo["waterCurve"])
    else:
        WC = xy2dataset(genWater(maxBC, NaClpercent, 1, 13))
    plotThing(py2js(bcmat), py2js(3), py2js(True))
    plotThing(py2js(WC), py2js(4), py2js(True))
    if False:
        tableSetup(buftable)
    numberCleanup(py2js(SPX["SSE"]), py2js(tbetainfo["tBeta"]))
def main():#Sets the events for certain buttons and fields on BreditForm
    docel("paramFile").addEventListener("change", create_proxy(preParamsSetter), False)
    docel("acid_titr_button").addEventListener("change", create_proxy(prePlotTitration), False)
    docel("base_titr_button").addEventListener("change", create_proxy(prePlotTitration), False)
    docel("BC_Curve_button").addEventListener("click", create_proxy(preGenBCCurve), False)
    docel("BC_Model_button").addEventListener("click", create_proxy(preModelBCCurve), False)

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
    Kw = np.power(10, -AdjustpKaMonoprotic(14, IonicStr, Temp))
    pKa = AdjustpKaMonoprotic(pKa, IonicStr, Temp)
    Ka = np.power(10, -pKa)
    num_buffers = np.amax(np.shape(Conc))
    H = np.power(10, -pHvec)
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
        
main()