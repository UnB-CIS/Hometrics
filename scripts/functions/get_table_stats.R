#' @title Função para calcular e gerar tabelas com estatísticas descritivas 
#' @author Luiz Paulo Tavares 

get_table_stats <- function(db, modo_type){
  
   summarizando_price = db %>% 
                        dplyr::group_by(property_type, modo) %>% 
                        dplyr::summarise("Média" = round(mean(price_m2), 2), 
                                         "Mediana" = round(median(price_m2), 2), 
                                         "Desvio" = round(sd(price_m2), 2), 
                                         "Mínimo" = round(min(price_m2), 2), 
                                         "Máximo" = round(max(price_m2), 2)) %>% 
                        dplyr::ungroup() %>% 
                        dplyr::rename("Tipo" = "property_type", "Modo" = "modo") %>% 
                        dplyr::filter(Modo == modo_type)
  
  return(summarizando_price)
  
}