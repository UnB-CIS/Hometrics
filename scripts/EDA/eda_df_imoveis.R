#' @title: Análise prévia dos dados coletados via Scraping 
#' @author: Luiz Paulo Tavares 

# Definindo ambiente de trabalhp ===============================================

base::rm(list = ls()) 
grDevices::graphics.off()

setwd("~/Github/Projetos/IEEE/Projects/PropertyPrices/DBs")

# Dependências \* 

library(pacman)
pacman::p_load(tidyverse, stats, DataExplorer, GGally)

# FUNCTIONS ====================================================================

get_remove_outliers <- function(data) {
  
  numeric_cols <- data %>% 
                  dplyr::select(where(is.numeric)) %>% base::colnames()
  
  for (column in numeric_cols) {
    
    Q1 <- stats::quantile(data[[column]], 0.25, na.rm = TRUE)
    Q3 <- stats::quantile(data[[column]], 0.75, na.rm = TRUE)
    
    IQR <- Q3 - Q1
    
    lower_bound <- Q1 - 1.5 * IQR
    upper_bound <- Q3 + 1.5 * IQR
    
    data <- data %>% dplyr::filter(data[[column]] >= lower_bound & 
                                     data[[column]] <= upper_bound)
  }
  return(data)
}


# import dataset & cleaning 

data_raw = readxl::read_excel("imoveis_df.xlsx") %>%
           janitor::clean_names() %>% 
           stats::na.omit() %>% 
           dplyr::mutate(bedrooms = as.integer(str_sub(bedrooms, 
                                                       start = 1, end = 1)), 
                         price = as.numeric(base::gsub("\\.", "", price))/10^6,
                         price_m2 = as.numeric(base::gsub("\\.", "", price_m2)), 
                         size_m2 = as.numeric(base::gsub("m²", "", size_m2))) 



censorship_filter <- function(){
  
  n <- nrow(data_raw) * 0.05
  
  ordenado <- data_raw %>% 
              dplyr::arrange(price) %>% 
               dplyr::slice(1601:(n() - 1600))
    
  
}
data_raw = ordenado
# Chamando Funcões \* 

data_cleaned = get_remove_outliers(data = data_raw)

summary(data_cleaned$price)
summary(data_cleaned$price_m2)

data_cleaned <- data_cleaned %>% 
                filter(price_m2 > 1000)

# Visualizando \* 

# DataExplorer::plot_intro(data = data_cleaned)


ggplot2::ggplot(data_cleaned, aes(x = price_m2)) +
          geom_histogram(binwidth = 100,
                         fill = "dodgerblue", color = "white", alpha = 0.7) +
          labs(title = "Distribuição do Preço por m² dos imóveis anunciados no DFimoveis.com",
               x = "Preço",
               y = "Frequência", 
               caption = "Fonte: elaboração de Luiz Paulo Tavares. Dados raspados do https://www.dfimoveis.com.br/. Excluídos os outliers") +
          theme_minimal(base_size = 15) +
          theme(plot.title = element_text(hjust = 0.5, face = "bold"),
                axis.title = element_text(face = "bold"))


ggplot2::ggplot(data = data_cleaned)+
         aes(y = price, x = size_m2)+
         geom_point()+
         geom_smooth(method = "lm")

GGally::ggpairs(data_cleaned[, 2:5])
