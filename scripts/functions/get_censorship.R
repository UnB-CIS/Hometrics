#' @title Função de filtro de censura 
#' @details Forma de filtrar as anomalias 
#' @author Luiz Paulo Tavares 


get_censorship <- function(){
  
  # ideia geral: partindo da métrica de média aparada 
  # censurar % do início da distribuição e do final da distribuição 
  # ou seja, censurar as caldas da distribuição 
  
  n <- nrow(data_raw) * 0.05
  
  ordenado <- data_raw %>% 
              dplyr::arrange(price) %>% 
              dplyr::slice(1601:(n() - 1600))
  
  
}