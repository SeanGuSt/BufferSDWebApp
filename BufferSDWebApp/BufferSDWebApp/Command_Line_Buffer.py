import Messages as msg
import Buffer_Functions as bf


#Retrieve the parameter file (the .csv)
paramDict = bf.get_paramDict()#Or bf.get_paramDict("path\to\file.csv")
#Retrieve the acid and base titration data
acid = bf.get_titration(msg.FIL_ACID_RPT)#Or bf.get_titration(msg.FIL_ACID_RPT, "path\to\file.RPT")
base = bf.get_titration(msg.FIL_BASE_RPT)#Or bf.get_titration(msg.FIL_BASE_RPT, "path\to\file.RPT")
dict0 = {"Acid Titration Data_scatter": acid, "Base Titration Data_scatter" : base}
#Plots the acid and base titration data
bf.make_and_save_plot(msg.PLT_NAME_GRPH0, msg.FIL_NAME_GRPH0, msg.XAXIS_LBL_GRPH0, msg.YAXIS_LBL_GRPH0, dict0)

init_vol = paramDict["Init_Vol"]; molHCl = paramDict["HCl"]; molNaOH = paramDict["NaOH"]
removeVal = paramDict["pH"]; mingaps = paramDict["MinGap"]; increment = paramDict["Increment"]
NaClPercent = paramDict["NaClpercent"]
D2B, oriBC, fillBC, WC = bf.get_BC_outline(init_vol, molHCl, molNaOH, removeVal, mingaps, increment, NaClPercent, acid, base)
dict1 = {"oriBC_scatter" : oriBC, "fillBC_scatter" : fillBC, "WC_scatter" : WC}
#Plots the BC Curve
bf.make_and_save_plot(msg.PLT_NAME_GRPH1, msg.FIL_NAME_GRPH1, msg.XAXIS_LBL_GRPH1, msg.YAXIS_LBL_GRPH1, dict1)

trimbeg = int(paramDict["Trim_beg"]); trimend = int(paramDict["Trim_end"]); electrode_shift = 0
oriBC, fillBC = bf.shift_and_trim_graph(trimbeg, trimend, electrode_shift, oriBC, fillBC)
dict2 = {"oriBC_scatter" : oriBC, "fillBC_scatter" : fillBC, "WC_scatter" : WC}
bf.make_and_save_plot(msg.PLT_NAME_GRPH2, msg.FIL_NAME_GRPH2, msg.XAXIS_LBL_GRPH2, msg.YAXIS_LBL_GRPH2, dict2)

order = int(paramDict["Order"]); NpKs = int(paramDict["NpKs"]); minConc = paramDict["MinConc"]; pK_tol = paramDict["pK_tol"]
LB = paramDict["LB"]; UB = paramDict["UB"]
buftable, tbetainfo, SPX, WCApprox = bf.get_BC_curve(order, NpKs, minConc, pK_tol, NaClPercent, LB, UB, oriBC, fillBC)
dict3 = {"oriBC_scatter" : oriBC, "fillBC_scatter" : fillBC, "WC_scatter" : WC, "BCApprox_line" : tbetainfo["BCCurve"], "WaterApprox_line" : WCApprox}
#Plots the modeled BC Curve
bf.make_and_save_plot(msg.PLT_NAME_GRPH3, msg.FIL_NAME_GRPH3, msg.XAXIS_LBL_GRPH3, msg.YAXIS_LBL_GRPH3, dict3)

