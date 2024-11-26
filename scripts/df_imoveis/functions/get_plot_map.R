#' @title Visualizando o preço do m² por região em mapas
#' @author Luiz Paulo Tavares Gonçalves 

get_plot_map <- function(data, type, modo, coord = COORDINATES){
  
  mean_region = get_price_stats(db = data, property = type, modo_type = modo, stat = "mean")  
  
  # Merge com as coordenadas de longitude e latitude 
  
  mean_price <- mean_region %>% base::merge(coord, by = "location")
  
  # Paleta para escala do mapa 
  
  palette <- leaflet::colorNumeric(palette = "inferno", domain = mean_price$value, reverse = TRUE)
  
  # Mapas \* 
  
  map <- leaflet::leaflet(data = mean_price) %>%
         leaflet::addTiles() %>%
                  addCircleMarkers(
                                   lng = ~longitude,
                                   lat = ~latitude,
                                   radius = ~value / max(value) * 15,     # Escala o tamanho do marcador pela média
                                   color = ~palette(value),                  # Cor do contorno com base na média
                                   fillColor = ~palette(value),              # Cor de preenchimento com base na média
                                   fillOpacity = 0.85,                  # Aumenta a opacidade de preenchimento
                                   stroke = TRUE,                       # Ativa o contorno
                                   weight = 1,                          # Define a espessura do contorno
                                   popup = ~paste("<b>Região:</b>", location,
                                                 "<br><b>Média:</b>", value)
                                ) %>%
          leaflet::addLegend("bottomright",              
                             pal = palette,
                             values = ~value,
                             title = "Preço Médio",
                             opacity = 1)
  
 return(map)
  
  
  
}