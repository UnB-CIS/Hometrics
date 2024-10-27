#' @title Calculando estatísticas regionais para plotagem dos mapas e gráficos
#' @author Luiz Paulo Tavares 

# Sun Oct 27 17:02:17 2024 ------------------------------

get_price_stats <- function(db, property, modo_type, stat){
  
 sumarizando_stat = db  %>% 
                    dplyr::group_by(property_type, location, modo) %>% 
                    dplyr::summarise(mean = mean(price_m2), 
                                     median = median(price_m2)) %>% 
                    dplyr::ungroup() %>% 
                    tidyr::pivot_longer(cols = mean:median) %>% 
                    dplyr::filter(property_type == property) %>% 
                    dplyr::filter(modo == modo_type) %>% 
                    dplyr::mutate(value = round(value, 2))

 
if(stat == "mean"){
  
  stats <- sumarizando_stat %>% dplyr::filter(name == "mean")
  
} else if(stat == "all"){
  
  stats <- sumarizando_stat
  
  
} else{
  
  stop("ERRO:OPÇÃO INVÁLIDA")
  
}

return(stats)
 
}