import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

def show_plotting_ui(df):
    """
    Mostra l'interfaccia utente per la creazione e personalizzazione dei grafici.
    Prende in input il DataFrame dallo stato della sessione.
    """
    st.header("Costruttore di Grafici")
    st.info("Usa la **Sidebar a sinistra** per mappare gli assi, personalizzare ed esportare il grafico.")
    
    # Prendiamo la lista delle colonne per i menu a tendina
    column_list = df.columns.tolist()
    
    # --- 1. Selezione Tipo di Grafico (in colonna) ---
    with st.container():
        plot_type = st.selectbox(
            "Scegli il tipo di grafico",
            ["Linea 2D", "Scatter 2D", "Scatter 3D", "Superficie 3D (Surface)"]
        )
    
    # --- 2. Mappatura Assi (in Sidebar) ---
    st.sidebar.header("2. Mappatura Assi")
    
    x_axis = st.sidebar.selectbox("Asse X", column_list, index=0, key="x_axis")
    y_axis = st.sidebar.selectbox("Asse Y", column_list, index=1 if len(column_list) > 1 else 0, key="y_axis")
    
    z_axis = None
    if "3D" in plot_type:
        z_axis = st.sidebar.selectbox("Asse Z", column_list, index=2 if len(column_list) > 2 else 0, key="z_axis")
        
    color_axis = st.sidebar.selectbox("Mappa Colore (opzionale)", [None] + column_list, key="color_axis")

    # --- 3. Personalizzazione (in Sidebar) ---
    st.sidebar.header("3. Personalizzazione")
    
    plot_title = st.sidebar.text_input("Titolo Grafico", f"{y_axis} vs {x_axis}")
    x_label = st.sidebar.text_input("Etichetta Asse X", x_axis)
    y_label = st.sidebar.text_input("Etichetta Asse Y", y_axis)
    z_label = "Z"
    if z_axis:
        z_label = st.sidebar.text_input("Etichetta Asse Z", z_axis)
    
    show_legend = st.sidebar.checkbox("Mostra Legenda", True)

    # --- 4. Generazione Grafico ---
    fig = None
    try:
        if plot_type == "Linea 2D":
            fig = px.line(df, x=x_axis, y=y_axis, color=color_axis, title=plot_title)
        
        elif plot_type == "Scatter 2D":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color_axis, title=plot_title)
        
        elif plot_type == "Scatter 3D":
            fig = px.scatter_3d(df, x=x_axis, y=y_axis, z=z_axis, color=color_axis, title=plot_title)
        
        elif plot_type == "Superficie 3D (Surface)":
            st.warning("""
                **Nota:** I grafici a superficie richiedono dati strutturati a 'griglia'.
                (Es. X=[1,2,3], Y=[A,B], Z=[z1a, z2a, z3a, z1b, z2b, z3b]).
                Se i tuoi dati sono solo 3 colonne 'sparse' (X, Y, Z), usa 'Scatter 3D'.
                Stiamo provando a 'pivotare' i dati...
            """)
            try:
                # Pivot dei dati: X diventa colonna, Y indice, Z valori
                df_pivot = df.pivot(index=y_axis, columns=x_axis, values=z_axis)
                fig = go.Figure(data=[go.Surface(z=df_pivot.values, x=df_pivot.columns, y=df_pivot.index)])
            except Exception as e:
                st.error(f"Impossibile creare grafico a superficie: {e}. Prova con Scatter 3D.")

        # --- 5. Applica Personalizzazioni e Mostra Grafico ---
        if fig:
            # Applica etichette e legenda
            fig.update_layout(
                xaxis_title=x_label,
                yaxis_title=y_label,
                showlegend=show_legend,
                # Grazie a Plotly, Interattività (Zoom, Pan) è già inclusa
            )
            if "3D" in plot_type:
                fig.update_layout(scene=dict(
                    xaxis_title=x_label,
                    yaxis_title=y_label,
                    zaxis_title=z_label
                ))
            
            # Mostra il grafico!
            st.plotly_chart(fig, use_container_width=True)

            # --- 6. Esportazione (in Sidebar) ---
            st.sidebar.header("4. Esportazione")
            img_format = st.sidebar.selectbox("Formato", ["png", "jpeg", "svg"])
            file_name = st.sidebar.text_input("Nome File", f"{plot_title.replace(' ', '_')}")

            # Converti il grafico in bytes
            buffer = BytesIO()
            fig.write_image(buffer, format=img_format)

            st.sidebar.download_button(
                label=f"Esporta come {img_format}",
                data=buffer,
                file_name=f"{file_name}.{img_format}",
                mime=f"image/{img_format}"
            )
            
    except Exception as e:
        st.error(f"Errore durante la creazione del grafico: {e}")
