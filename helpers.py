import pandas as pd
import geopandas as gpd
import seaborn as sns
from shapely.geometry import Point
import matplotlib.pyplot as plt


def df_to_markdown(df, columns):
    print(df[columns].to_markdown(index=False))

# Writes clean data to a folder containing preprocessed files
# (The first row will contain the column data types)
def save_dataset(filename, dataset):
    with open(filename, "wt") as f:
        f.write(",".join(map(str, dataset.dtypes)) + "\n")
        dataset.to_csv(f, index=False, lineterminator="\n")

# Reads a preprocessed dataset from a file and returns it as a pandas DataFrame
# (The function expects to find the column data types from the first row)
def load_dataset(filename):
    with open(filename, "rt") as f:
        types = next(f).rstrip().split(",")[0:]
        columns = next(f).rstrip().split(",")[0:]
        return pd.read_csv(f, dtype=dict(zip(columns, types)), names=columns)

# Returns a preprocessed region (maakunta) id based on municipality (kunta) id
def get_rid_by_mid(municipality_id, mappings):
    match = mappings.loc[mappings['municipality_id'] == municipality_id, 'region_id']
    
    if match.empty:
        return None
    
    return int(match.values[0])

# Returns a preprocessed region (maakunta) id based on maakunta's name (in Finnish, Swedish or English)
def get_rid_by_name(region_name, mappings):
    if region_name == "WHOLE COUNTRY":
        return int(0)

    match = mappings.loc[(mappings['region_fi'] == region_name) |
                         (mappings['region_sv'] == region_name) |
                         (mappings['region_en'] == region_name), 'region_id']
   
    if match.empty:
        return None
    
    return int(match.values[0])
    
# Returns a preprocessed municipality (kunta) id based on municipality's name (in Finnish, Swedish or English)
def get_mid_by_name(municipality_name, mappings):
    match = mappings.loc[(mappings['municipality_fi'] == municipality_name) |
                         (mappings['municipality_sv'] == municipality_name) |
                         (mappings['municipality_en'] == municipality_name), 'municipality_id']
    
    if match.empty:
        return None
    
    return int(match.values[0])
    
# Return the municipality (kunta) name based on municipality id
def get_name_by_mid(municipality_id, mappings):
    municipality_name = mappings.loc[mappings['municipality_id'] == municipality_id, 'municipality_en'].values[0]
    return municipality_name

# Returns a municipality id based on coordinates (WGS84)
def get_mid_by_coords(coords, map):
    point = [Point(coords)]
    points = gpd.GeoDataFrame(geometry=point, crs="EPSG:4326")
    points = points.to_crs(map.crs)
    points_with_municipalities = gpd.sjoin(points, map, how="left", predicate="within")
    natcode = points_with_municipalities["NATCODE"].values[0]
    if pd.isna(natcode):
        return None
    return int(natcode)

# Returns a timestamp based on year and quarter
def get_last_day_of_quarter(year, quarter):
    if quarter == 1:
        return pd.Timestamp(year, 3, 31)
    elif quarter == 2:
        return pd.Timestamp(year, 6, 30)
    elif quarter == 3:
        return pd.Timestamp(year, 9, 30)
    elif quarter == 4:
        return pd.Timestamp(year, 12, 31)

# Draws a stacked area chart
def draw_stacked_area(df, index, columns, values, title="", xlabel="", ylabel="", legend_title="", style="default"):
    with plt.style.context(style):
        pivot_data = df.pivot_table(index=index, columns=columns, values=values, aggfunc='sum', fill_value=0)
        
        plt.figure(figsize=(12, 6))
        pivot_data.plot(kind='area', stacked=True, alpha=0.6, linewidth=1, figsize=(12, 6))

        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid()

        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles[::-1], labels[::-1], title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show()

# Draws a line chart
def draw_line_chart(df, index, columns, values, title="", xlabel="", ylabel="", legend_title="", style="default", tick_frequency=None, label_rotation=45):
    with plt.style.context(style):
        pivot_data = df.pivot(index=index, columns=columns, values=values)

        plt.figure(figsize=(12, 6))
        
        for column in pivot_data.columns:
            plt.plot(pivot_data.index, pivot_data[column], label=column, linewidth=1)

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        ax = plt.gca()
        if tick_frequency:
            ax.set_xticks(ax.get_xticks()[::tick_frequency])

        plt.xticks(rotation=label_rotation, fontsize=10)
        plt.yticks(fontsize=10)

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.show()

# Draws a bar chart
def draw_bar_chart(df, index, values, hue=None, title="", xlabel="", ylabel="", legend_title="", color="skyblue", style="default"):
    with plt.style.context(style):
        fig, ax = plt.subplots(figsize=(12, 6))

        if hue:
            df_pivot = df.pivot(index=index, columns=hue, values=values)
            df_pivot.plot(kind='bar', stacked=False, ax=ax, colormap=color)

            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
            ax.legend(title=legend_title)
        else:
            bars = ax.bar(df[index], df[values], color=color)

            ax.set_title(title, fontsize=16)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)

            ax.set_xticks(range(len(df[index])))
            ax.set_xticklabels(df[index], rotation=45, ha='right', fontsize=10)

        ax.grid(axis='y', zorder=0)
        ax.set_axisbelow(True)
        plt.yticks(fontsize=10)

        plt.tight_layout()
        plt.show()

# Draws a facet grid
def draw_facetgrid(data, col, hue, x, y, palette="tab20c", height=5, aspect=1.5, title=None, xlabel=None, ylabel=None, legend_title=None):
    g = sns.FacetGrid(data, col=col, hue=hue, palette=palette, height=height, aspect=aspect)
    
    g.map(sns.lineplot, x, y)
    
    if legend_title:
        g.add_legend(title=legend_title)
    else:
        g.add_legend()

    if xlabel:
        g.set_axis_labels(xlabel)
    if ylabel:
        g.set_axis_labels(y_var=ylabel)
    
    if title:
        plt.subplots_adjust(top=0.9)
        g.fig.suptitle(title)

    g.tight_layout()
