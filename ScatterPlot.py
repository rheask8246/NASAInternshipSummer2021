import pandas
import PyRootMegalibReader
import os
import matplotlib.pyplot as plt


dir = "/Users/rsenthil/ComPair/Simulations/Aeffexample"

#if not os.path.exists( f"{dir}/FarFieldPointSource_100MeV_StandardCSV.inc1.id1.tra.csv"):
#    _, _, _, df1 = PyRootMegalibReader.readOneSetOfSims( "/Users/rsenthil/ComPair/Geometry/AMEGO_Midex/AmegoBase.geo.setup", f"{dir}/FarFieldPointSource_100MeV.inc1.id1.sim", f"{dir}/FarFieldPointSource_100MeV_Standard.inc1.id1.tra",   )

#else:
df1 = pandas.read_csv("/Users/rsenthil/ComPair/Simulations/Aeffexample/FarFieldPointSource_100MeV_StandardCSV.inc1.id1.tra.csv")
df1.set_index("ID")

sel_pairs1 = (df1.RecoType == "Pair")


#if not os.path.exists( f"{dir}/FarFieldPointSource_100MeV_Kalman2DCSV.inc1.id1.tra.csv"):
#    _, _, _, df2 = PyRootMegalibReader.readOneSetOfSims( "/Users/rsenthil/ComPair/Geometry/AMEGO_Midex/AmegoBase.geo.setup", f"{dir}/FarFieldPointSource_100MeV.inc1.id1.sim", f"{dir}/FarFieldPointSource_100MeV_Kalman2D.inc1.id1.tra",   )

#else:
df2 = pandas.read_csv("/Users/rsenthil/ComPair/Simulations/Aeffexample/FarFieldPointSource_100MeV_Kalman2DCSV.inc1.id1.tra.csv")
df2.set_index("ID")

sel_pairs2 = (df2.RecoType == "Pair")

df_combined = df1[sel_pairs1].join( df2[sel_pairs2], how="inner", rsuffix="_kalman" )

print( df_combined[["RecoEnergy", "RecoEnergy_kalman", "RecoDelAngle", "RecoDelAngle_kalman"]])



plt.plot( df_combined.RecoEnergy, df_combined.RecoEnergy_kalman, ".")

plt.xlabel("Reco Energy (standard) [MeV]")
plt.ylabel("Reco Energy (kalman) [MeV]")
plt.title("True Energy: 100 MeV")
plt.grid(True)
plt.savefig("EnergyScatterplot_100MeV.png")
plt.clf()

