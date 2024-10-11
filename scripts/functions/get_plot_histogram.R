#' @title Gráfico de distribuição 
#' @author Luiz Paulo Tavares 

get_plot_histogram <- function(data){
  
  plot_property_type <- ggplot2::ggplot(data) +
                                 aes(x = price_m2, fill = property_type) +
                                 geom_histogram(bins = 30L) +
                                 scale_fill_brewer(palette = "Blues", direction = 1) +
                                 labs(y = "Contagem", 
                                      x = "Preço nominal do m²", 
                                      fill = "") + get_thema_plots()
  
  return(plot_property_type)
  
}