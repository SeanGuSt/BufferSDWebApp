from scipy.optimize import Bounds, minimize as fmincon
import numpy as np
#from EventsFile import BetaModel_AB
def SimplexBCPK_DF5(ObsXY, ABmat, minConc, pK_tol, LB, UB):#Equivalent of SimplexBCPK_DF5 from SimplexBCPK_DF5.m
    #assignments
    SPX = {"ABmat":None, "BCmat":None, "Pred":None, "SSE":None, "Obs":None}
    ObsX = ObsXY[:,0]#pH values (col)
    ObsY = ObsXY[:,1]#BC values (col)
    zeroflag = False#bool for check for no buffers
    PredX = ObsX#x value vector
    salt = 0#all calc done without IS correction
    ABmat = ABmat[abs(ABmat[:,0])>minConc, :]#keep values that meet condition for minimum conc in AB
    if ABmat.size == 0:#check for empty matrix
        ABmat = np.zeros((1, 2))#if empty, just use zeros
        zeroflag = True#set a flag so fit only water?
    else:
        ABmat = combineABs(ABmat, pK_tol)#combine rows w/similar pKs

    #set up boundry values for fmincon constraints on each parameter value
    row, col = ABmat.shape#get size of ABmat
    lowerBounds = np.zeros((row, col))#LB matrix, conc values remain zero 
    lowerBounds[:, 1] = LB#LB pKs have min of titration curve
    upperBounds = np.ones((row, col))#UB matrix, conc values have max of 1 M/L 
    upperBounds[:, 1] = UB#UB pKs have max of titration curve
    def ABmat2paramvec(paramValues):#Equivalent of ABmat2paramvec from SimplexBCPK_DF5.m
        #Convert AB matrix to linear vector conc;pK in order
        return paramValues.flatten('F')
    lbvec = ABmat2paramvec(lowerBounds)#convert matrix to vector (subfunc)
    ubvec = ABmat2paramvec(upperBounds)#convert matrix to vector (subfunc)

    #set up parameters for fmincon optimization
    paramvec = ABmat2paramvec(ABmat)
    fhan = lambda p:CalcSSE(p, salt, ObsX, ObsY)#anon. function SSE: python, found here
    bound = Bounds(lbvec, ubvec)#Define bounds for optimization
    #scipy.optimize.minimize is equivalent to fmincon from MATLAB in this instance
    res = fmincon(fhan, paramvec, tol=1e-20, bounds=bound)#optimize with constraints

    #regenerate AB matrix
    ABmat_pred = paramvec2ABvals(res.x)#convert linear vector to ABmat: python, found here
    #adjust AB matrix (remove very small or neg values and combine like pKs)
    ABmat_pred = ABmat_pred[abs(ABmat_pred[:,0])>minConc, :]#keep values that meet condition for minimum conc in AB
    ABmat_pred = combineABs(ABmat_pred, 0.3)#combine rows w/similar pKs

    #set pred data
    if zeroflag:
        ABmat_pred = np.zeros((1, 2))
    #Predicted data with BetaModel
    SPX["Pred"] = BetaModel_AB(ABmat_pred,salt, PredX)#returns Nx2 (pH,BC)
    if any(ABmat_pred[:,0] == 0):#dont call with a zero conc row
        SPX["BCmat"] = np.zeros((1,2))#return 1x2 zero matrix
    else:
        SPX["BCmat"] = Conc2Beta(ABmat_pred)#get beta values from AB matrix
    SPX["Obs"] = ObsXY#Nx2 (pH vector, BC)
    SPX["ABmat"] = ABmat_pred#Nx2 output (pred conc, pKvals)
    SPX["SSE"] = res.fun/20#scalar (sum sq err, recorrect)
    return SPX

def CalcSSE(paramvec, salt, ObsX, ObsY):#Equivalent of CalcSSE from SimplexBCPK_DF5.m
    ABvalues = paramvec2ABvals(paramvec)#python, found below
    Pred = BetaModel_AB(ABvalues, salt, ObsX)#python, EventsFile.py
    return 20*np.sum(np.power(ObsY - Pred[:,1], 2))

def paramvec2ABvals(paramvec):#Equivalent of paramvec2ABvals from SimplexBCPK_DF5.m
    #Convert linear conc;pK params back to AB matrix 
    num_rows = int(len(paramvec)/2)#get index for 1/2 of vector
    ABvals = np.zeros((num_rows, 2), dtype=float)
    ABvals[:, 0] = paramvec[:num_rows]#conc vals in 1st col
    ABvals[:, 1] = paramvec[num_rows:]#pK vals in 2nd col
    return ABvals

def combineABs(ABmat, tol):#Equivalent of CombineABs from CombineABs.m
    row, col = ABmat.shape#get number of AB pairs
    newABmat = np.zeros((row, col))
    newABmat[0, :] = ABmat[0,:]#new AB mat with 1st val
    index = 0#Index for new ABmat
    if row > 1:
        for i in range(1, row):
            if abs(ABmat[i,1] - ABmat[i-1,1]) < tol:#if next with tol of prev
                temp_conc = ABmat[i,0] + newABmat[index,0]#get new conc
                newABmat[index, 0] = temp_conc#set new value to new AB mat
            else:
                index += 1#advance index
                newABmat[index,:] = ABmat[i,:]#pK values different, so use
    return newABmat[:index+1, :]

def Conc2Beta(ABmat):#Equivalent of Conc2Beta from Conc2Beta.m
    #get number of rows in ABmat, set up return matrix
    rows, cols = ABmat.shape#rows in ABmat
    NaClPercent = 0#don't alter pK due to salt
    temp = np.zeros((rows, 2))#return matrix
    #for each row, calculate the beta value for the corresponding pH
    for i in range(rows):
        temp[i, :] = BetaModel_AB(ABmat[i,:], NaClPercent, np.array(ABmat[i, 1], ndmin=1))#python, EventsFile.py
    #BetaModel returns pH, BC: we want BC, pH
    return temp[:,::-1]


