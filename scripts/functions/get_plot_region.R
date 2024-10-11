#' @title Visualizando o preço do m² por região 
#' @author Luiz Paulo Tavares Gonçalves 


get_plot_region <- function(data, is_type, is_modo, title_plot){
  
  sumarizando = data  %>% 
                dplyr::group_by(property_type, location, modo) %>% 
                       summarise(mean = mean(price_m2), 
                                 median = median(price_m2)) %>% ungroup() %>% 
                tidyr::pivot_longer(cols = mean:median) %>% 
                dplyr::filter(property_type == is_type) %>% 
                dplyr::filter(modo == is_modo)
  
  # Visualizando \* 
  
 plot_region = ggplot2::ggplot(sumarizando) +
                aes(x = fct_reorder(location, value), y = value, fill = name) +
                geom_col(position = "dodge2") +
                scale_fill_brewer(palette = "Blues", direction = 1) +
                labs(title = paste0(title_plot),
                     y = "", 
                     x = "", 
                     fill = "")+
                ylim(0, max(sumarizando$value))+
                coord_flip() + get_thema_plots()
  
                
    return(plot_region)
    
}





