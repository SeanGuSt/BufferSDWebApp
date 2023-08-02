import numpy as np
#from fminconpy import SimplexBCPK_DF5
#from EventsFile import BetaModel_AB
from decimal import Decimal, localcontext, ROUND_HALF_UP
def pyModelBCCurve(order, NpKs, minConc, pK_tol, NaClpercent, LB, UB, X, Y):#Equivalent of part of app.ModelBCCurveButtonPushed
    res = SCBC_fit(X, Y, order)#get trig data: python, found below
    scbcpred = res["Pred"]
    psize = scbcpred.shape#number of data pts
    indxvec = splitvec(NpKs, psize[0])#python, found below
    #initialize temporary matrix for initial conc-pK values
    tempMat = np.zeros((NpKs, 2))
    for k in range(NpKs):#for each pK assign:
        tempMat[k] = scbcpred[indxvec[k], ::-1]#The BC and pK values
    SPX = SimplexBCPK_DF5(scbcpred, tempMat, minConc, pK_tol, LB, UB)#python, fminconpy.py
    letters = getAB_letters(SPX["ABmat"])#python, found below
    buftable = []#Build the table
    buftable.append(SPX["ABmat"][:, 0].tolist())
    buftable.append(SPX["ABmat"][:, 1].tolist())
    buftable.append(letters)
    buftable.append(SPX["BCmat"][:, 0].tolist())
    minpH = np.amin(scbcpred[:,0])
    maxpH = np.amax(scbcpred[:,0])
    waterNaCl = NaClpercent/5.84#ask about why, in the original code, this is app.NaClpercentEditField.Value and not app.ParamTable.Value('NaClPercent')
    tBetainfo = get_tBetaData(SPX["ABmat"], minpH, maxpH, waterNaCl, 0)
    return buftable, tBetainfo, SPX

def SCBC_fit(X, Y, order, calcArea=False):#Generic version of SCBCfit_only & SCBCfit_area
    #assignments
    res = {"Obs":None, "Pred":None, "params":None, "SSE":None, "recip_cond":None, "determinant":None, "area":None}
    mul = 0.5#X val multiplier (for 1 cycle 2..12)
    modelX = np.linspace(np.amin(X), np.amax(X), 100)#pred X: 100 pts between 2..12
    terms = 2*order + 1#b0 + 2 terms (for "degree" or "harmonic")
    N = len(X)#number of X data points

    #set up partial deriv matrix with summed sin, cos terms 
    def GetFactorMat(terms, order, N):
        #get a vector (termsxN) with 2*order + 1 number of sine - cosine 
        # terms (with initial 1) and appropriate multiplier
        k = 1#matrix row index, skip first row (all 1s)
        mat = np.ones((terms, N))#one row of X vals for each term 
        for j in range(1, order+1):#for each set of terms (order)
            mat[k,:] = np.sin(j*mul*X)#sine term (times order index and mult.)
            mat[k+1,:] = np.cos(j*mul*X)#cosine term (times order index and mult.)
            k+=2#advance row index
        return mat
    factormat = GetFactorMat(terms,order,N); #get matrix of X for each deriv
    pmat = np.zeros((terms,terms));          #square matrix for partial derivatives
    for l in range(terms):#for each row of square matrix (L not 1)
        for m in range(terms):#for each col of square matrix
            pmat[l,m] = np.dot(factormat[l,:],factormat[m,:])#sum sin and/or cos

    #get Y vector
    ymat = np.zeros(terms)#col vector for Y vals * each term
    for n in range(terms): #for each term mult Y val * sin or cos
        ymat[n] = np.dot(factormat[n,:], Y) #sum: SorC (col) * Y vals (col)
    #matrix division to calc params for sine-cosine model
    params = np.linalg.solve(pmat, ymat)#divide Y matrix by square param matrix
    if calcArea:#Only run this part to be like SCBCfit_area
        #This if statement is equivalent to CalcArea from SCBCfit_area
        loopvar = int((len(params) - 1)/2)#loop for each set of terms (but not Bo)
        b0 = params[0]#set Bo
        p = 1#counter for param index
        minX = np.amin(X)
        maxX = np.amax(X)
        evalMin = 0#to sum min X answer
        evalMax = 0#to sum max X answer
        for i in range(1, loopvar):
            evalMin += (params[p+1]*np.sin(i*mul*minX) - params[p]*np.cos(i*mul*minX))/(i*mul)
            evalMax += (params[p+1]*np.sin(i*mul*maxX) - params[p]*np.cos(i*mul*maxX))/(i*mul)
            p+=2
        evalMin += b0*minX
        evalMax += b0*maxX
        return evalMax - evalMin
    
    def CalcSCModel(currPrms, Xvals):#Equivalent of CalcSCModel from SCBCfit_only.m
        #calc model with final params and predicted X values
        loopvar = int((len(currPrms) - 1)/2)
        b0 = currPrms[0]
        p = 1
        sumterms = np.zeros(len(Xvals))
        for i in range(1, loopvar+1):
            sumterms += currPrms[p]*np.sin(i*mul*Xvals) + currPrms[p+1]*np.cos(i*mul*Xvals)
            p += 2
        return b0 + sumterms

    modelY = CalcSCModel(params,modelX)#calc predicted vals for each model X
    def CalcSC_SSE(currPrms):#calc sum squared error for param set
        predYvals = CalcSCModel(currPrms, X)#uses obs X values for this
        return np.sum(np.power(Y - predYvals, 2))#sum squared errors, predicted minus Y 
    SSE = CalcSC_SSE(params)#use predicted parameters to calc SSE
    Obs = np.transpose(np.vstack((X, Y)))
    Pred = np.transpose(np.vstack((modelX, modelY)))
    res["Obs"] = Obs#BC Curve
    res["Pred"] = Pred#predicted (SCBC) model data
    res["params"] = params
    res["SSE"] = SSE#sum sq. error term
    res["recip_cond"] = np.linalg.cond(pmat)#matrix condition
    res["determinant"] = np.linalg.det(pmat)#determinant
    return res


def splitvec(byN, vecsize):#Equivalent of splitvec from splitvec.m
    indices = np.zeros(byN)#initialize return vector
    increment = vecsize/(byN + 1)#calc increment between values
    previous = 0#initialize previous index value
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP#Without this, UGH would be rounded to the nearest even number if it had a decimal of 0.5
        for i in range(byN):#for each index in the vector
            UGH = previous + increment#get int value for next index
            indices[i] = int(Decimal(UGH).to_integral_value())#Round it and turn it into an integer
            previous = indices[i]#reset previous value
    return indices.astype(int) - 1


def getAB_letters(abmat):#Equivalent of app.getAB_letters
    #Get "a" or "b" letters for acid or base
    rows, cols = abmat.shape#get size of matrix
    letters = ['a']*rows#make a char vec
    for i in range(rows):#for each buffer
        if abmat[i, 1] > 7:#check pH
            letters[i] = 'b'#reset if above 7
    return letters


def get_tBetaData(ABmat,pHmin,pHmax,waterIS,crvIS):#Equivalent of get_tBetaData from get_tBetaData.m
    tbetainfo = {"BCCurve":None, "waterCurve":None, "pHvec":None, "bctBeta":None, "watertBeta":None, "tBeta":None}
    waterNaClpct = waterIS*5.84
    crvNaClpct = crvIS*5.84
    pHvec = np.arange(pHmin, pHmax + 0.001, 0.05)
    bc = BetaModel_AB(ABmat, crvNaClpct, pHvec)#python, EventsFile.py
    wtr = BetaModel_AB(np.zeros((1,2)), waterNaClpct, pHvec)
    tbetainfo["BCCurve"] = bc
    tbetainfo["waterCurve"] = wtr
    tbetainfo["pHvec"] = pHvec
    tbetainfo["bctBeta"] = 100*SCBC_fit(bc[:,0], bc[:,1], 15, True)
    tbetainfo["watertBeta"] = 100*SCBC_fit(wtr[:,0], wtr[:,1], 15, True)
    tbetainfo["tBeta"] = tbetainfo["bctBeta"] - tbetainfo["watertBeta"]
    return tbetainfo




