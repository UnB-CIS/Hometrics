#' @title Função de filtro de censura 
#' @details Forma de filtrar as anomalias 
#' @author Luiz Paulo Tavares 


get_censorship <- function(data, pct, var) {
  
  censorship <- base::floor(nrow(data) * pct)
  
  censored_data = data %>%
                  dplyr::arrange(get(var)) %>%
                  dplyr::slice((censorship + 1):(n() - censorship))

  return(censored_data)
}
