#' @title: Run - Rodando pipeline para front e back-end *AMBIENTE DE STAGE/TESTE*
#' @author: Luiz Paulo Tavares 

# Definindo ambiente de trabalhp ===============================================

base::rm(list = ls()) 
grDevices::graphics.off()

setwd("~/Github/Projetos/IEEE/Projects/HousePriceProject/DBs")

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
               shiny)

# Globais & Constantes 

PATH = "~/Github/Projetos/IEEE/Projects/HousePriceProject/scripts/functions"

# Import Functions =============================================================

base::lapply(list.files(PATH, pattern = "\\.R$", full.names = TRUE), source)

# Import Xlsx ==================================================================

venda <- get_import_db(is_type = "venda")  
aluguel <- get_import_db(is_type = "aluguel") 

# Limpeza & Organização 

data_cleaned_venda = get_data_cleaned(db = venda)
data_cleaned_aluguel = get_data_cleaned(db = aluguel)

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

