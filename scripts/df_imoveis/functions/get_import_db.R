#' @title Pré-processamento 
#' @title Luiz Paulo Tavares 

get_import_db <- function(is_type){
  
  combined_data <- dplyr::bind_rows(lapply(list.files(pattern = "\\.xlsx$"), read_excel))
  
  # Filtrar modo de interesse 
  
  db = combined_data %>% dplyr::filter(modo == is_type)

  return(db)
  
}

