from plot_nodes import plot
import streamlit as st
import streamlit_folium

figure = plot()

streamlit_folium.folium_static(figure)