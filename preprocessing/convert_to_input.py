#%%
import pandas as pd
#09-06-2020
#18-05-2022
#09-08-2022
#07-02-2023
#23-05-2023

for date in ['02122024']:# '23052023','09062020', '18052022', '09082022', '07022023', '23012024', '18052022', '10042024', '22052024']:
    path_in = f'N:/Projects/11207500/11207510/F. Other information/meetcampagnes/ruwe_data_campagnes/meetcampagne_{date}.xlsx'
    path_out = f'N:/Projects/11207500/11207510/B. Measurements and calculations/02_handmetingen/handmetingen_{date}.csv'
    header_lines =  [
        '==========================    BEGINNING OF DATA     ==========================',
         '[Field campaign]',
         f'  Date                    ={date}',
         '  Project                 =Meetnet IJmuiden',
         '  Project number          =11207510',
         '  Number of samples       =38',
         '[Channel 1]',
         '  Identification          =Sample identification number',
         '[Channel 2]',
         '  Identification          =pH (-)',
         '[Channel 3]',
         '  Identification          =Electrical Conductivity (µS/cm)',
         '[Channel 4]',
         '  Identification          =Redox potential (mV)',
         '[Channel 5]',
         '  Identification          =Temperature (°C)',
         '[Channel 6]',
         '  Identification          =Concentration dissolved oxygen (mg/L)',
         '',
         '',]
    
    header = '\n'.join([str(line) for line in header_lines])
    with open(path_out, 'w') as fp:
        fp.write(header)
    
    df = pd.read_excel(path_in)   
    df= df[['Monsternaam', 'pH', 'Ec (µS/cm)','Redox (mV)', 'Temp (°C)', 'O2']]
    df.columns = ['Sample number', 'pH[-]','Electrical Conductivity[µS/cm]',
                  'Redox potential[mV]','Temperature[°C]','Concentration dissolved oxygen[mg/L]']
    df = df[~df['Sample number'].isin(['Z13PB600-01_1','B25A0942_3','B25A0942_5','B25A0942_6','B25A0942_7'])]
    df['Sample number'] = df['Sample number'].replace('B25A0942_4','B25A0942_3')
    df = df.set_index('Sample number').sort_index()
    df.to_csv(path_out, header=True, mode='a', sep=';')
    
    


# %%
