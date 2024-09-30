#' @title remoção de observações discrepantes 
#' @author Luiz Paulo Tavares 

get_remove_outliers <- function(data) {
  
  numeric_cols <- data %>% 
                  dplyr::select(where(is.numeric)) %>% base::colnames()
  
  for (column in numeric_cols) {
    
    Q1 <- stats::quantile(data[[column]], 0.25, na.rm = TRUE)
    Q3 <- stats::quantile(data[[column]], 0.75, na.rm = TRUE)
    
    IQR <- Q3 - Q1
    
    lower_bound <- Q1 - 1.5 * IQR
    upper_bound <- Q3 + 1.5 * IQR
    
    data <- data %>% dplyr::filter(data[[column]] >= lower_bound & 
                                     data[[column]] <= upper_bound)
  }
  return(data)
}
