# Generate a simple sections map, with representation of a metric 
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import pandas as pd

SECTIONS_GPKG = "../../datasets/BGRI2021_1312.gpkg"


# section_id,validations,section_id,weight,indicator
VALIDATIONS = "./validation_per_section.csv"


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
    df = gpd.read_file(SECTIONS_GPKG)


    common_ids = len(set(df.OBJECTID).intersection(set(val_per_section["section_id"])))
    print(f"Number of common ids: {common_ids}")

    return df.merge(val_per_section, left_on='OBJECTID', right_on='section_index')

def plot_map(df, metric):
    df = df.to_crs(epsg=3857)
    ax = df.eval(f'pct_afam = {metric}')\
            .plot('pct_afam', cmap='plasma', alpha=.7, linewidth=.25, edgecolor='k', legend=True)
    ax.set_axis_off()
    ax.set_title("Heatmap of " + metric)

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    plt.show()


def main():
    df = read_datasets()
    plot_map(df, "indicator/ N_INDIVIDUOS_25_64")

if __name__ == '__main__':
    main()
