# intro:

- draft a chapter about GEOINT
- draft a paragraph about geojson
- draft a chapter about osm

# define tasks: 

a company working in gold mine exploitation ask some intelligence support to find where and how establish logistics in Enga Region - Papua New Guinee : this is a war zone with tribal conflicts. Find datasets and show them in a efficient and meaningfull way. Find source of data:

- mines (https://www.mindat.org/ , https://pypi.org/project/openmindat/, )
- roads by type (https://www.openstreetmap.org/)
- conflicts hotspots ((https://ucdp.uu.se/) )


# RUN code

```
streamlit run main.py
```




## Technologies Used

- **Streamlit** — map dashboard UI
- **pydeck** — 3D geospatial visualisation (WebGL-based maps)
- **geopandas** — geospatial data manipulation and GeoJSON handling
- **pyrosm** — OpenStreetMap PBF file parsing for road extraction
- **openmindat** — client for the mindat.org mineral locality database
- **UCDP GED API** — Uppsala Conflict Data Program georeferenced event data
- **Geofabrik** — OpenStreetMap regional PBF data downloads
