#' @title Desenvolvimento do Back-end 
#' @author Luiz Paulo Tavares 

server <- function(input, output, session) {
  
  # Tabela com estatísticas descritivas \* 
  
  output$table_description <- DT::renderDataTable({
    
    table_stats = get_table_stats(db = db) 
    
    DT::datatable(as.data.frame(table_stats),
                  options = list(pageLength = 2, 
                                 autoWidth = TRUE,
                                 columnDefs = list(list(className = 'dt-center', targets = "_all"))),
                  caption = "Em R$. Considerando Brasília e todas as regiões administrativas do DF.",
                  style = "bootstrap4")
    
  })
  
  
  # Exibindo o histograma de Venda \* 
  
  output$histogramVenda <- renderPlotly({
    
    plot_histogram <- get_plot_histogram(data_cleaned_venda) + ggtitle("Preço de Venda")
   
    # Adicionando interatividade
    
    plotly::ggplotly(plot_histogram)
    
  })
  
  # Exibindo o histograma de Aluguel\* 
  
  output$histogramAluguel <- renderPlotly({
    
    plot_histogram <- get_plot_histogram(data_cleaned_aluguel) + ggtitle("Preço do Aluguel")
    
    # Adicionando interatividade
    
    plotly::ggplotly(plot_histogram)
    
  })
  
  # SEGUNDA SECÇÃO =============================================================
  # SECÇÃO REGIÕES DO DF \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  
  
  output$maps_price <- renderLeaflet({
    
    req(input$property_type, input$modo)  # Certifica que ambos inputs estão disponíveis
    
    map_region <- get_plot_map(data = db, 
                               type = input$property_type,  
                               modo = input$modo)

   map_region
    
  })
  
  
}

shinyApp(ui, server)
