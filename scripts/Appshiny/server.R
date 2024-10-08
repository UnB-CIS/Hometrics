#' @title Desenvolvimento do Back-end 
#' @author Luiz Paulo Tavares 

server <- function(input, output, session) {
  
  # Exibindo o histograma
  
  output$histogramPlot <- renderPlotly({
    
    plot_property_type <- ggplot2::ggplot(data_cleaned) +
                          aes(x = price_m2, fill = property_type) +
                          geom_histogram(bins = 30L) +
                          scale_fill_brewer(palette = "Blues", direction = 1) +
                          labs(y = "Contagem", 
                               x = "Preço nominal do m²", 
                               fill = "") + get_thema_plots()
    
    # Adicionando interatividade
    
    plotly::ggplotly(plot_property_type)
    
  })
  
  # Gráfico por regiões baseado na seleção
  
  output$regionPlot <- renderPlotly({
    
    req(input$property_type)  # Certifica que um tipo de imóvel foi selecionado
    
    plot_region <- get_plot_region(data = data_cleaned, 
                                   type = input$property_type, 
                                   title_plot = paste(input$property_type, "-", "Preço de Venda do m² no DF"))
    
    # Adicionando interatividade
    
    plotly::ggplotly(plot_region)
    
  })
}

shinyApp(ui, server)
