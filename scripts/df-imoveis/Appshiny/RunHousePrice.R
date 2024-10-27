#' @title: Run - Rodando pipeline para front e back-end *AMBIENTE DE STAGE/TESTE*
#' @author: Luiz Paulo Tavares 

# Definindo ambiente de trabalhp ===============================================
# Sun Oct 27 13:04:06 2024 ------------------------------

base::rm(list = ls()) 
grDevices::graphics.off()

setwd("~/Github/Projetos/IEEE/Projects/HousePriceProject/scripts/df-imoveis/DBs")

# Dependências \* 

library(pacman)
pacman::p_load(tidyverse, 
               readxl,
               stats,
               DataExplorer,
               GGally,
               plotly, 
               shiny, 
               bslib, 
               shinydashboard, 
               shiny, 
               leaflet)

# Globais & Constantes 

PATH = "~/Github/Projetos/IEEE/Projects/HousePriceProject/scripts/df-imoveis/functions"

COORDINATES <- base::data.frame(
                          location = c("Brasilia", "Gama", "Taguatinga", "Brazlandia", "Sobradinho", 
                                       "Planaltina", "Paranoa", "Nucleo Bandeirante", "Ceilandia", 
                                       "Guara", "Cruzeiro", "Samambaia", "Santa Maria", 
                                       "Sao Sebastiao", "Recanto das Emas", "Lago Sul", 
                                       "Riacho Fundo", "Lago Norte", "Candangolandia", 
                                       "Aguas Claras", "Riacho Fundo II", "Sudoeste Octogonal", 
                                       "Varjão", "Park Way", "SCIA", "Sobradinho II", "Jardim Botanico",
                                       "Itapoã", "SIA", "Vicente Pires", "Fercal", "Sol Nascente", 
                                       "Arniqueira", "Arapoanga", "Água Quente"),
                          latitude = c(-15.7942, -16.0250, -15.8333, -15.6644, -15.6511, 
                                       -15.6111, -15.7708, -15.8750, -15.8200, -15.8367, -15.7833,
                                       -15.8842, -16.0203, -15.8992, -15.9175, -15.8564, -15.9144, 
                                       -15.7053, -15.8569, -15.8364, -15.8953, -15.7972, -15.6844, 
                                       -15.8684, -15.8014, -15.6324, -15.8977, -15.7367, -15.7825, 
                                       -15.8092, -15.5606, -15.8125, -15.8564, -15.5725, -15.8847),
                          longitude = c(-47.8822, -48.0636, -48.0536, -48.2639, -47.7900,
                                        -47.6583, -47.8556, -47.9189, -48.1083, -47.9242, -47.9208,
                                        -48.1128, -48.0625, -47.5858, -48.0486, -47.8828, -47.9325,
                                        -47.8858, -47.9581, -48.0319, -47.9397, -47.9275, -47.8842, 
                                        -47.9394, -47.9642, -47.8536, -47.7961, -47.8008, -47.8964, 
                                        -47.9992, -48.2764, -47.9908, -48.0214, -47.7631, -48.1433))

# Import Functions =============================================================

base::lapply(list.files(PATH, pattern = "\\.R$", full.names = TRUE), source)

# Import Xlsx ==================================================================

venda <- get_import_db(is_type = "venda")  
aluguel <- get_import_db(is_type = "aluguel") 

# Limpeza & Organização 

data_cleaned_venda = get_data_cleaned(db = venda)
data_cleaned_aluguel = get_data_cleaned(db = aluguel)

rm(venda, aluguel) # \* Limpando a memória \* Variáveis não utilizadas

# get_censorship: filtragem de anomalia - censura de dados \*

data_cleaned_aluguel = get_censorship(data = data_cleaned_aluguel, var = "price", pct = 0.05)
data_cleaned_aluguel = get_censorship(data = data_cleaned_aluguel, var = "size", pct = 0.05)
data_cleaned_venda = get_censorship(data = data_cleaned_venda, var = "price", pct = 0.05)
data_cleaned_venda = get_censorship(data = data_cleaned_venda, var = "size", pct = 0.05)

# get_remove_outliers: filtragen de outliers \* 

data_cleaned_aluguel = get_remove_outliers(data = data_cleaned_aluguel)
data_cleaned_venda = get_remove_outliers(data = data_cleaned_venda)

# Venda e Aluguel organizadas e agrupadas \* 

db = bind_rows(list(data_cleaned_venda, data_cleaned_aluguel))

