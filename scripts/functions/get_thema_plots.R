#' @title Tema dos gráficos 
#' @author Luiz Paulo Tavares 

# grDevices::graphics.off()

get_thema_plots <- function(){
  
    tema = ggplot2::theme_minimal() +
                    theme(legend.position = "bottom",
                          legend.justification = "bottom", 
                          axis.title.x = element_text(face = "bold"),  
                          axis.title.y = element_text(face = "bold"), 
                          axis.text.x = element_text(face = "bold"),    
                          axis.text.y = element_text(face = "bold"))
    
    return(tema)
  
}
