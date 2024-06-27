import numpy as np
from js import document, chartCurve, JSON, setupTable, abSwap, programAtLeastLevel, plotThing, plotBC, numberCleanup, changeProgramLevel, findLabelsAndValues, bufFile
from pyodide.ffi import create_proxy
from json import dumps, loads
import pandas as pd
import io
import asyncio
beginning_or_clear_all = 0;
parameters_input = 1;
acid_data_added = 2;
base_data_added = 3;
curve_generated_gaps_filled = 4;
pH_electrode_shifted = 4.3;
beginning_trimmed = 4.5;
ending_trimmed = 4.8;
curve_modeled = 5;
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
    changeProgramLevel(parameters_input)
async def preParamsDefault(event):
    pyParamsSetter(docel('paramDefaults').checked, defaultDict)
    changeProgramLevel(parameters_input)
async def prePlotTitration(event):#Generic version of app.OpenAcidTitrationButtonPushed & app.OpenBaseTitrationButtonPushed 
    etf = event.target.files
    gotFiles = etf.length>0
    if programAtLeastLevel(parameters_input) and gotFiles:
        for file in etf:
            trueFile = await file.text()
        f = open("temp.txt", "w")
        f.write(trueFile)
        f.close()
        x, y = getTitrationData("temp.txt")#python, plotTitration.py
        if event.target.id == "acid_titr_button":
            index = acid_data_added
            set_globals("acid_x", x)
            set_globals("acid_y", y)
        elif event.target.id == "base_titr_button" and programAtLeastLevel(acid_data_added):
            index = base_data_added
            set_globals("base_x", x)
            set_globals("base_y", y)
        else:
            return False
    changeProgramLevel(index)#javascript, GraphHandling.js  
    results = xy2dataset(x, y)
    plotThing(py2js(results), index - 2)#javascript, GraphHandling.js
    

async def preGenBCCurve(event):#Equivalent of app.GenerateBCCurveButtonPushed
    if programAtLeastLevel(base_data_added):#javascript, GraphHandling.js
        changeProgramLevel(curve_generated_gaps_filled)
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
        await shifTrimGraph(event)
async def redoGenBCCurve(event):
    if programAtLeastLevel(base_data_added):
        await preGenBCCurve(event)
async def shifTrimGraph(event):
    if programAtLeastLevel(curve_generated_gaps_filled):#Level 4 or higher required
        trimbeg = int(docel("Trim_beg").value)
        trimend = int(docel("Trim_end").value)
        shift = float(docel("electrode_shift").value)
        [BCpts, cols] = oriBC.shape
        if trimbeg+trimend <= BCpts:
            set_globals("BC", oriBC[range(trimbeg, BCpts), :])
            [BCpts, cols] = BC.shape
            BC[:, 0] += shift
            set_globals("BC", BC[range(BCpts-trimend), :])
            maxBC = np.amax(BC[:,1])
            newFill = np.zeros(orifillBC.shape)
            newFill[:,0] += shift
            set_globals("fillBC", orifillBC + newFill)
            plotBC(py2js(xy2dataset(fillBC)), py2js(xy2dataset(BC)), maxBC)
            match event.target.id:
                case "electrode_shift":
                    changeProgramLevel(pH_electrode_shifted)
                case "Trim_beg":
                    changeProgramLevel(beginning_trimmed)
                case "Trim_end":
                    changeProgramLevel(ending_trimmed)
            
    
async def preModelBCCurve(event):#Equivalent of part of app.ModelBCCurveButtonPushed
    if programAtLeastLevel(curve_generated_gaps_filled):
        order = int(docel("Order").value)
        #initialize optimization with pK distribution across pts
        NpKs = int(docel("NpKs").value)
        minConc = float(docel("MinConc").value)
        pK_tol = float(docel("pK_tol").value)
        LB = float(docel("LB").value)
        UB = float(docel("UB").value)
        NaClpercent = float(docel("NaClpercent").value)
        X0, Y0 = dataset2xy(2)#init X and Y vals (Nx1) N= no. data points)
        X1, Y1 = dataset2xy(3)#gap filler X and Y vals
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
        changeProgramLevel(curve_modeled)#Do not move
        setupTable(py2js(buftable))
        numberCleanup("sse", SPX["SSE"], -3)
        numberCleanup("tb", tbetainfo["tBeta"])
        useAdjC()

async def preabSwap(event):
    global buftable
    if programAtLeastLevel(curve_modeled):
        cell, newLetter = js2py(abSwap(event))
        if cell:
            buftable[2][cell] = newLetter
            useAdjC()

async def preUseAdjC(event):
    if programAtLeastLevel(curve_modeled):
        useAdjC()
async def hardReset(event):
    changeProgramLevel(beginning_or_clear_all)
async def getResults(event):
    if programAtLeastLevel(curve_modeled):
        ing = docel("ingredient").value;
        outputids = ['ingredient', 'conTitr', 'HCl', 'NaOH', 'Init_Vol', 'NaClpercent', 'Trim_beg', 'Trim_end', 'sse', 'eph', 'adjc', 'tb']
        findLabelsAndValues(py2js(outputids), 'Report_' + ing + '.csv')
        bufFile(py2js(buftable), 'BCTable_' + ing + '.csv')


def main():#Sets the events for certain buttons and fields on BreditForm
    docel("paramFile").addEventListener("change", create_proxy(preParamsSetter), False)
    docel("paramDefaults").addEventListener("change", create_proxy(preParamsDefault), False)
    docel("acid_titr_button").addEventListener("change", create_proxy(prePlotTitration), False)
    docel("base_titr_button").addEventListener("change", create_proxy(prePlotTitration), False)
    docel("BC_Curve_button").addEventListener("click", create_proxy(preGenBCCurve), False)
    docel("electrode_shift").addEventListener("change", create_proxy(shifTrimGraph), False)
    docel("Trim_beg").addEventListener("change", create_proxy(shifTrimGraph), False)
    docel("Trim_end").addEventListener("change", create_proxy(shifTrimGraph), False)
    docel("adjc_checkbox").addEventListener("change", create_proxy(preUseAdjC), False)
    docel("BC_Model_button").addEventListener("click", create_proxy(preModelBCCurve), False)
    docel("myTable").addEventListener("click", create_proxy(preabSwap), False)
    docel("clear_button").addEventListener("click", create_proxy(hardReset), False)
    docel("download_results_button").addEventListener("click", create_proxy(getResults), False)
    for key in defaultDict.keys():
        if not (key.__eq__("Trim_beg") or key.__eq__("Trim_end")):
                docel(key).addEventListener("change", create_proxy(redoGenBCCurve), False)
    

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
            docel(x).value = None

def useAdjC():
        isChecked = docel("adjc_checkbox").checked
        if isChecked:
            adjC_results = pyGetAdjCT(measuredpH, buftable, float(docel("NaClpercent").value))#python, found in getAdjCT.py
            adjC = adjC_results.x[0]
            numberCleanup("adjc", adjC)
        else:
            adjC = 0
            docel("adjc").value = None
        pH = CalcpH_ABT(buftable, float(docel("NaClpercent").value), adjC)
        numberCleanup("eph", pH)
main()