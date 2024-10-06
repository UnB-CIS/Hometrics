#' @title Desenvolvimento do Back-end 
#' @author Luiz Paulo Tavares 

server <- function(input, output, session) {
  
  # Exibindo o histograma
  
  output$histogramPlot <- renderPlot({
    
    ggplot2::ggplot(data_cleaned) +
              aes(x = price_m2, fill = property_type) +
              geom_histogram(bins = 30L) +
              scale_fill_brewer(palette = "Blues", direction = 1) +
              labs(y = "Contagem", 
                   x = "Preço nominal do m²", 
                   fill = "") +
              theme_minimal() +
              theme(legend.position = "bottom", 
                    axis.title.x = element_text(face = "bold"),  
                    axis.title.y = element_text(face = "bold"), 
                    axis.text.x = element_text(face = "bold"),    
                    axis.text.y = element_text(face = "bold"))
    
  })
  
  # Gráfico por regiões baseado na seleção
  
  output$regionPlot <- renderPlot({
    
    req(input$property_type)  # Certifica que um tipo de imóvel foi selecionado
    get_plot_region(data = data_cleaned, 
                    type = input$property_type, 
                    title_plot = paste("Preço do m² de", input$property_type, "no DF"))
  })
}

shinyApp(ui, server)
