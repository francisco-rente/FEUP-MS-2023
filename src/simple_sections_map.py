# Generate a simple sections map, with representation of a metric 
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import pandas as pd
import os

SECTIONS_GPKG = "./datasets/BGRI2021_1312.gpkg"

MAPS= "./results/maps/"

#section_id,weight,validations,indicator,indicator_norm
VALIDATIONS = "./results/indicator.csv"
VALIDATIONS_WITHOUT_TRINDADE = "./results/indicator_without_trindade.csv"

info_code = ['OBJECTID', 'BGRI2021',    
       'N_EDIFICIOS_CLASS_CONST_3_OU_MAIS_ALOJAMENTOS',
       'N_EDIFICIOS_EXCLUSIV_RESID', 'N_EDIFICIOS_1_OU_2_PISOS',
       'N_EDIFICIOS_3_OU_MAIS_PISOS','N_ALOJAMENTOS_TOTAL',
       'N_ALOJAMENTOS_FAMILIARES', 'N_ALOJAMENTOS_FAM_CLASS_RHABITUAL',
       'N_ALOJAMENTOS_FAM_CLASS_VAGOS_OU_RESID_SECUNDARIA',
       'N_RHABITUAL_COM_ESTACIONAMENTO', 'N_RHABITUAL_PROP_OCUP',
       'N_RHABITUAL_ARRENDADOS', 'N_AGREGADOS_DOMESTICOS_PRIVADOS',
       'N_ADP_1_OU_2_PESSOAS', 'N_ADP_3_OU_MAIS_PESSOAS',
       'N_NUCLEOS_FAMILIARES',
       'N_NUCLEOS_FAMILIARES_COM_FILHOS_TENDO_O_MAIS_NOVO_MENOS_DE_25',
       'N_INDIVIDUOS', 'N_INDIVIDUOS_H', 'N_INDIVIDUOS_M', 'N_INDIVIDUOS_0_14',
       'N_INDIVIDUOS_15_24', 'N_INDIVIDUOS_25_64', 'N_INDIVIDUOS_65_OU_MAIS',
       'SHAPE_Area', 'geometry']



def read_datasets():
    val_per_section = pd.read_csv(VALIDATIONS, sep=",")
    val_per_section_without_trindade = pd.read_csv(VALIDATIONS_WITHOUT_TRINDADE, sep=",")
    df = gpd.read_file(SECTIONS_GPKG)

    return df.merge(val_per_section, left_on='OBJECTID', right_on='section_id'), df.merge(val_per_section_without_trindade, left_on='OBJECTID', right_on='section_id')


def plot_map(df, metric, title, img_name, min_val=0, max_val=1):
    df = df.to_crs(epsg=3857)
    ax = df.eval(f'pct_afam = {metric}')\
            .plot('pct_afam', cmap='plasma', alpha=.7, linewidth=.15, edgecolor='k', legend=True, vmin = min_val, vmax = max_val,
                                        legend_kwds={'orientation': "horizontal", 
                                                    'shrink': 0.8,
                                                     }, figsize=(10, 10))
    ax.set_axis_off()
    ax.set_title(title)

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    

    plt.savefig(os.path.join(MAPS, img_name + ".png"), dpi=500, bbox_inches='tight')
    plt.close()


def main():
    print("Reading datasets")
    df, df_without_trindade = read_datasets()

    if not os.path.exists(MAPS):
        try:
            print(f"Creating directory {MAPS}")
            os.mkdir(MAPS)
        except OSError:
            print ("Creation of the directory %s failed" % MAPS)
            exit(1)

    print("Plotting maps")
    plot_map(df, "indicator_norm", "Normalized indicator per section", "norma_indicador")
    plot_map(df_without_trindade, "indicator_norm", "Normalized indicator w/o Trindade", "norma_indicador_sem_trindade")
    

    plot_map(df, "validations", "No of validations", "validations", min_val=0, max_val=10**6)
    plot_map(df_without_trindade, "validations", "Validations w/o Trindade", "validations_sem_trindade", min_val=0, max_val=10**6)
    
    plot_map(df, "weight", "Weight per section", "weight", min_val=400, max_val=1500)
    plot_map(df_without_trindade, "weight", "Weight w/o Trindade", "weight_sem_trindade", min_val=400, max_val=1500)
       


if __name__ == '__main__':
    main()
