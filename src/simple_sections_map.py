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


def plot_map(df, metric, title, img_name):
    df = df.to_crs(epsg=3857)
    ax = df.eval(f'pct_afam = {metric}')\
            .plot('pct_afam', cmap='plasma', alpha=.7, linewidth=.25, edgecolor='k', legend=True)
    ax.set_axis_off()
    ax.set_title(title)

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    
    # plt.savefig(os.path.join(MAPS, img_name + ".png"), dpi=300)
    plt.show()


def main():
    df, df_without_trindade = read_datasets()
    print("Plotting maps")

    plot_map(df, "indicator_norm", "Norma indicador", "norma_indicador")
    plot_map(df_without_trindade, "indicator_norm", "Norma indicador sem Trindade", "norma_indicador_sem_trindade")

    plot_map(df, "validations", "validations", "validations")
    plot_map(df_without_trindade, "validations", "validations_sem_trindade", "validations_sem_trindade")


    plot_map(df, "N_INDIVIDUOS", "No individuos", "No individuos")
    plot_map(df, "weight", "Peso", "Peso")



    # print("Plotting validations")
    # plot_map(df, "validations", "validations")

    # metric_in_geopkg = ['N_NUCLEOS_FAMILIARES','N_NUCLEOS_FAMILIARES_COM_FILHOS_TENDO_O_MAIS_NOVO_MENOS_DE_25',\
    #    'N_INDIVIDUOS', 'N_INDIVIDUOS_H', 'N_INDIVIDUOS_M', 'N_INDIVIDUOS_0_14',\
    #    'N_INDIVIDUOS_15_24', 'N_INDIVIDUOS_25_64', 'N_INDIVIDUOS_65_OU_MAIS','N_ALOJAMENTOS_TOTAL', 
    #     'N_EDIFICIOS_EXCLUSIV_RESID', 'N_ALOJAMENTOS_FAMILIARES', 'N_ALOJAMENTOS_FAM_CLASS_RHABITUAL',\
    #     'N_RHABITUAL_COM_ESTACIONAMENTO'
    #     ]
    
    
    # # for each metric, divid indicator by the norm of the metric and plot 
    # for metric in metric_in_geopkg: 
    #     # get the norm 
    #     metric_mean = df[metric].mean()
    #     metric_std = df[metric].std()
    #     temp_df = df.copy()
    #     temp_df[f"{metric}_norm"] = (df[metric] - metric_mean) / metric_std
    #     #temp_df[f"{metric}_norm"] = temp_df.apply(lambda x: x[f"{metric}_norm"]/ x["indicator_norm"] if x["indicator_norm"] > 0 else 0, axis=1)
    #     temp_df[f"{metric}_norm"] = temp_df.apply(lambda x: x["indicator"] / x[f"{metric}_norm"] if x[f"{metric}_norm"] != 0 else 0, axis=1) 
    #     plot_map(temp_df, f"{metric}_norm", f"indicator_norm_over_{metric}")


       


if __name__ == '__main__':
    main()
