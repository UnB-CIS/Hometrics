#' @title: Run - Rodando pipeline para front e back-end *AMBIENTE DE STAGE/TESTE*
#' @author: Luiz Paulo Tavares 

# Definindo ambiente de trabalhp ===============================================
# Sun Oct 27 13:04:06 2024 ------------------------------

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

COORDINATES = base::data.frame(
                              location = c("Brasilia", "Gama", "Taguatinga", "Brazlandia", "Sobradinho", 
                                           "Planaltina", "Paranoa", "Nucleo Bandeirante", "Ceilandia", 
                                           "Guara", "Cruzeiro", "Samambaia", "Santa Maria", 
                                           "Sao Sebastiao", "Recanto das Emas", "Lago Sul", 
                                           "Riacho Fundo", "Lago Norte", "Candangolandia", 
                                           "Aguas Claras", "Riacho Fundo II", "Sudoeste Octogonal", 
                                           "Varjão", "Park Way", "SCIA", "Sobradinho II", "Jardim Botanico",
                                           "Itapoã", "SIA", "Vicente Pires", "Fercal", "Sol Nascente", 
                                           "Arniqueira", "Arapoanga", "Água Quente"),
                              latitude = c(-15.7801, -16.0328, -15.8350, -15.6644, -15.6521, 
                                           -15.6047, -15.7734, -15.8701, -15.8266, -15.8505, -15.7784,
                                           -15.8771, -16.0164, -15.8854, -15.9164, -15.8421, -15.9329, 
                                           -15.7202, -15.8618, -15.8346, -15.8872, -15.7989, -15.6841, 
                                           -15.8718, -15.7864, -15.6324, -15.9057, -15.7255, -15.7745, 
                                           -15.8153, -15.5522, -15.8109, -15.8644, -15.5704, -15.8928),
                              longitude = c(-47.9292, -48.0651, -48.0500, -48.2731, -47.8359,
                                            -47.6510, -47.8620, -47.9204, -48.1103, -47.9431, -47.9318,
                                            -48.1122, -48.0559, -47.5795, -48.0396, -47.8787, -47.9310,
                                            -47.8614, -47.9566, -48.0261, -47.9418, -47.9383, -47.9075, 
                                            -47.9238, -47.9638, -47.8417, -47.7973, -47.7962, -47.8934, 
                                            -47.9952, -48.2703, -47.9924, -48.0151, -47.7625, -48.1512))

# Import Functions =============================================================

base::lapply(list.files(PATH, pattern = "\\.R$", full.names = TRUE), source)

# Import Xlsx ==================================================================

venda <- get_import_db(is_type = "venda")  
aluguel <- get_import_db(is_type = "aluguel") 

# Limpeza & Organização \* 

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

# Estatísticas Descritivas \* 

table_stats = get_table_stats(db = db) 



db <- db %>% 
      base::merge(COORDINATES, by = "location")
      

test <- db %>% 
        filter(property_type == "Apartamento") %>% 
        group_by(location, latitude, longitude) %>% 
  summarise(mean = mean(price_m2)) %>% ungroup()



# test2 <- db %>% 
#   filter(property_type == "Casa") %>% 
#   group_by(location) %>% 
#   summarise(mean = mean(price_m2)) %>% ungroup()



# Definindo uma paleta de cores de azul a vermelho
pal <- colorNumeric(palette = "RdYlBu", domain = test$mean, reverse = TRUE)

# Criando o mapa interativo com o data frame `test`
map <- leaflet(data = test) %>%
  addTiles() %>%
  addCircleMarkers(
    lng = ~longitude, 
    lat = ~latitude,
    radius = ~mean / max(mean) * 10,  # Escala o tamanho do marcador pela média
    color = ~pal(mean),               # Aplica a cor com base no valor médio
    fillColor = ~pal(mean),
    fillOpacity = 0.6,
    popup = ~paste("<b>Região:</b>", location,
                   "<br><b>Média:</b>", mean)
  ) %>%
  addLegend("bottomright",             # Adiciona legenda
            pal = pal, 
            values = ~mean,
            title = "Valor Médio",
            opacity = 1)

# Exibindo o mapa
map

