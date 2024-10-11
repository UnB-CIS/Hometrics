#' @title Desenvolvimento do Back-end 
#' @author Luiz Paulo Tavares 

server <- function(input, output, session) {
  
  # Exibindo o histograma de Venda \* 
  
  output$histogramVenda <- renderPlotly({
    
    plot_histogram <- get_plot_histogram(data_cleaned_venda)
    
    # Adicionando interatividade
    
    plotly::ggplotly(plot_histogram)
    
  })
  
  # Exibindo o histograma de Aluguel\* 
  
  output$histogramAluguel <- renderPlotly({
    
    plot_histogram <- get_plot_histogram(data_cleaned_aluguel)
    
    # Adicionando interatividade
    
    plotly::ggplotly(plot_histogram)
    
  })
  
  # Gráfico por regiões baseado na seleção
  
  output$regionPlot <- renderPlotly({
    
    req(input$property_type, input$modo)  # Certifica que ambos inputs estão disponíveis
    
    plot_region <- get_plot_region(data = db, 
                                   is_type = input$property_type,  
                                   is_modo = input$modo,           
                                   title_plot = paste(input$property_type, "-", 
                                                      ifelse(input$modo == "venda", "Preço de Venda", "Preço de Aluguel"), 
                                                      "do m² no DF"))

    
    # Adicionando interatividade ao gráfico gerado
    
    ggplotly(plot_region)
    
  })
  
  
  
}

shinyApp(ui, server)
