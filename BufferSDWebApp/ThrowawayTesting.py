import sys
sys.path.insert(0, r'C:\Users\scg2600\source\repos\BufferSDWebApp\BufferSDWebApp\BufferSDWebApp\static\pyscripts')
from plotTitration import getTitrationData
from GenBCCurve import pyGenBCCurve
from ModelBCCurve import pyModelBCCurve
acid_path = r"C:\Users\scg2600\OneDrive - University of Texas at Arlington\Documents\MATLAB\Example Files\EXAMPLE_ACID.RPT"
base_path = r"C:\Users\scg2600\OneDrive - University of Texas at Arlington\Documents\MATLAB\Example Files\EXAMPLE_BASE.RPT"
acid_x, acid_y = getTitrationData(acid_path)
print(f"Acid Titration x-axis: acid_x = \n{acid_x}")
print(f"Acid Titration y-axis: acid_y = \n{acid_y}")
base_x, base_y = getTitrationData(base_path)
print(f"Acid Titration x-axis: base_x = \n{base_x}")
print(f"Acid Titration y-axis: base_y = \n{base_y}")
D2B, oriBC, BC, WC = pyGenBCCurve(0.05, 2, 2, 0.05, 0.3, 0.1, 2, acid_x, acid_y, base_x, base_y)
print("STARTING POINT HERE!!!!!1!")
#print(f"Original Buffer Capacity: oriBC = \n{oriBC}")
#print(f"Gap Filled Buffer Capacity: BC = \n{BC}")
#print(f"Water Curve: WC = \n{WC}")
X = BC[:, 0]
Y = BC[:, 1]
buftable, tbetainfo, SPX = pyModelBCCurve(15, 7, 0.001, 0.2, 2, 2, 12, X, Y)
print(buftable)
print(SPX)


