#' @title Calculando preço médio e mediano dos imoveis e plotando
#' @author Luiz Paulo Tavares 

get_plot_type <- function(data){
  
type_sumarise = data  %>% 
                dplyr::group_by(property_type) %>% 
                       summarise(mean = mean(price_m2), 
                                 median = median(price_m2)) %>% ungroup() %>% 
                tidyr::pivot_longer(cols = mean:median)
  
 # Visualizando \* 

plot_type_sumarise = ggplot2::ggplot(type_sumarise) +
                      aes(x = property_type, 
                          y = value, 
                          fill = name) +
                      geom_col(position = "dodge2") +
                      scale_fill_brewer(palette = "Blues",
                                        direction = 1) +
                      labs(title = "Preço do m² do imóvel no Distrito Federal", 
                           x = "", y = "Preço nominal do m²", 
                           fill = "")+
                      geom_text(aes(label = round(value), 
                                    y = value), 
                                position = position_dodge(width = 0.9), 
                                vjust = -0.5) +
                      ylim(0, max(type_sumarise$value)+1000)+ get_thema_plots()
                      

  return(plot_type_sumarise)
  
}

