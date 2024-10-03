#' @title Visualizando o preço do m² por região 
#' @author Luiz Paulo Tavares Gonçalves 


get_plot_region <- function(data, type, title_plot){
  
  sumarizando = data  %>% 
                dplyr::group_by(property_type, location) %>% 
                       summarise(mean = mean(price_m2), 
                                 median = median(price_m2)) %>% ungroup() %>% 
                tidyr::pivot_longer(cols = mean:median) %>% 
                dplyr::filter(property_type == type)
  
  # Visualizando \* 
  
 plot_region = ggplot2::ggplot(sumarizando) +
                aes(x = fct_reorder(location, value), y = value, fill = name) +
                geom_col(position = "dodge2") +
                scale_fill_brewer(palette = "Blues", direction = 1) +
                labs(title = paste0(title_plot),
                     y = "", 
                     x = "", 
                     fill = "")+
                ylim(0, max(sumarizando$value)+1000)+
                coord_flip() +
                theme_minimal() +
                theme(legend.position = "bottom")
  
                
    return(plot_region)
    
}





